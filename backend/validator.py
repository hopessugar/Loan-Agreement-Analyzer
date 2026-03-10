import re
from Levenshtein import ratio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


LEVENSHTEIN_THRESHOLD = 0.80   # minimum similarity for short values
COSINE_THRESHOLD      = 0.80   # minimum similarity for clause-level text
CONFIDENCE_THRESHOLD  = 0.50   # below this score entity is flagged with warning
MATH_TOLERANCE        = 0.10   # ±10% tolerance for mathematical consistency check

FINANCIAL_KEYWORDS = [
    "interest", "rate", "loan", "amount", "repayment", "monthly",
    "instalment", "installment", "penalty", "late", "fee", "charge",
    "processing", "insurance", "administrative", "duration", "total",
    "cost", "principal", "emi", "default", "prepayment", "schedule"
]


# ═══════════════════════════════════════════════
# STEP 1 — HALLUCINATION DETECTION
# ═══════════════════════════════════════════════

def check_hallucination(value: str, source_clause: str, full_contract: str) -> dict:
    if not value or not full_contract:
        return {"is_verified": False, "similarity": 0.0, "method": "none"}

    value_str = str(value).strip().lower()
    contract_lower = full_contract.lower()
    if len(value_str) <= 50:
        best_score = 0.0
        window_size = len(value_str)

        for i in range(0, len(contract_lower) - window_size + 1, 5):
            window = contract_lower[i:i + window_size]
            score = ratio(value_str, window)
            if score > best_score:
                best_score = score

        is_verified = best_score >= LEVENSHTEIN_THRESHOLD
        return {
            "is_verified": is_verified,
            "similarity": round(best_score, 3),
            "method": "levenshtein"
        }

    else:
        if not source_clause:
            return {"is_verified": False, "similarity": 0.0, "method": "cosine"}

        try:
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([source_clause.lower(), contract_lower])
            score = cosine_similarity(vectors[0], vectors[1])[0][0]
            is_verified = score >= COSINE_THRESHOLD
            return {
                "is_verified": is_verified,
                "similarity": round(float(score), 3),
                "method": "cosine"
            }
        except Exception:
            return {"is_verified": False, "similarity": 0.0, "method": "cosine_failed"}


# ═══════════════════════════════════════════════
# STEP 2 — MATHEMATICAL CONSISTENCY CHECK
# ═══════════════════════════════════════════════

def check_mathematical_consistency(extraction: dict) -> dict:
    try:
        monthly  = extraction.get("monthly_payment", {}).get("value")
        duration = extraction.get("repayment_duration", {}).get("value")
        total    = extraction.get("total_cost", {}).get("value")

        # Can only check if all three values were extracted
        if not all([monthly, duration, total]):
            return {
                "is_consistent": None,
                "reason": "Cannot check — one or more values missing",
                "difference_pct": None
            }

        monthly  = float(str(monthly).replace(",", "").strip())
        duration = float(str(duration).replace(",", "").strip())
        total    = float(str(total).replace(",", "").strip())

        calculated_total = monthly * duration
        difference       = abs(calculated_total - total)
        difference_pct   = difference / total if total > 0 else 1.0

        is_consistent = difference_pct <= MATH_TOLERANCE

        return {
            "is_consistent": is_consistent,
            "calculated_total": round(calculated_total, 2),
            "stated_total":     round(total, 2),
            "difference_pct":   round(difference_pct * 100, 2),
            "reason": "Within tolerance" if is_consistent else
                      f"⚠️ Numbers don't add up — {round(difference_pct*100,2)}% difference. Ask lender to explain."
        }

    except (ValueError, TypeError) as e:
        return {
            "is_consistent": None,
            "reason": f"Could not parse numeric values: {e}",
            "difference_pct": None
        }


def compute_financial_summary(extraction: dict) -> dict:
    """
    Computes total repayment, total interest and an effective interest
    percentage when enough information is available.
    """
    try:
        loan_amount = extraction.get("loan_amount", {}).get("value")
        monthly     = extraction.get("monthly_payment", {}).get("value")
        duration    = extraction.get("repayment_duration", {}).get("value")
        total_cost  = extraction.get("total_cost", {}).get("value")

        if not loan_amount:
            return {}

        loan_amount_f = float(str(loan_amount).replace(",", "").strip())

        # IMPORTANT RULE:
        # - If total_cost is explicitly extracted from the contract, use that value.
        # - Only when total_cost is NOT found, compute total_repayment = EMI * months.
        if total_cost is not None:
            total_repayment = float(str(total_cost).replace(",", "").strip())
        elif monthly is not None and duration is not None:
            monthly_f  = float(str(monthly).replace(",", "").strip())
            duration_f = float(str(duration).replace(",", "").strip())
            total_repayment = monthly_f * duration_f
        else:
            return {}

        total_interest = total_repayment - loan_amount_f
        eff_rate = (total_interest / loan_amount_f) * 100 if loan_amount_f > 0 else None

        return {
            "loan_amount": round(loan_amount_f, 2),
            "total_repayment": round(total_repayment, 2),
            "total_interest": round(total_interest, 2),
            "effective_interest_pct": round(eff_rate, 2) if eff_rate is not None else None,
        }
    except Exception:
        return {}


# ═══════════════════════════════════════════════
# STEP 3 — CONFIDENCE SCORING
# ═══════════════════════════════════════════════

def get_regex_score(entity_name: str, value: str) -> float:
    if not value:
        return 0.0

    value_str = str(value).strip()

    patterns = {
        "loan_amount":          r'[\d,]+(\.\d+)?',
        "interest_rate":        r'\d+(\.\d+)?',
        "repayment_duration":   r'\d+',
        "monthly_payment":      r'[\d,]+(\.\d+)?',
        "total_cost":           r'[\d,]+(\.\d+)?',
        "late_fee":             r'[\d,]+(\.\d+)?|[\d]+\s*%',
        "penalty_interest":     r'\d+(\.\d+)?\s*%',
        "prepayment_penalty":   r'[\d,]+(\.\d+)?|[\d]+\s*%',
        "processing_fee":       r'[\d,]+(\.\d+)?|[\d]+\s*%',
        "insurance_fee":        r'[\d,]+(\.\d+)?|[\d]+\s*%',
        "administrative_fee":   r'[\d,]+(\.\d+)?|[\d]+\s*%',
        "other_fee":            r'[\d,]+(\.\d+)?',
        "repayment_start_date": r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{1,2}\s+\w+\s+\d{4}',
    }

    pattern = patterns.get(entity_name, r'\w+')
    if re.search(pattern, value_str):
        # Boost confidence for very clean numeric patterns.
        if entity_name in {"loan_amount", "monthly_payment", "total_cost"} and re.fullmatch(r'[\d,]+(\.\d+)?', value_str):
            return 1.0
        if entity_name == "interest_rate" and re.fullmatch(r'\d+(\.\d+)?', value_str):
            return 1.0
        return 0.9
    return 0.3


def get_keyword_proximity_score(entity_name: str, source_clause: str) -> float:
    if not source_clause:
        return 0.0

    clause_lower = source_clause.lower()
    entity_keywords = {
        "loan_amount":          ["loan", "amount", "principal", "sanctioned"],
        "interest_rate":        ["interest", "rate", "%", "per annum", "p.a"],
        "repayment_duration":   ["repayment", "duration", "tenure", "period", "months", "years"],
        "monthly_payment":      ["monthly", "instalment", "installment", "emi"],
        "total_cost":           ["total", "cost", "payable", "repayable"],
        "late_fee":             ["late", "overdue", "delay", "default"],
        "penalty_interest":     ["penalty", "penal", "default", "interest"],
        "prepayment_penalty":   ["prepayment", "preclosure", "early", "penalty"],
        "processing_fee":       ["processing", "origination", "disbursement"],
        "insurance_fee":        ["insurance", "premium", "cover"],
        "administrative_fee":   ["administrative", "admin", "service", "handling"],
        "other_fee":            ["fee", "charge", "levy"],
        "repayment_start_date": ["start", "commence", "first", "due", "date"],
    }

    keywords = entity_keywords.get(entity_name, FINANCIAL_KEYWORDS)
    matches  = sum(1 for kw in keywords if kw in clause_lower)
    return min(1.0, matches / max(len(keywords), 1))


def calculate_confidence(
    entity_name:   str,
    value:         str,
    source_clause: str,
    levenshtein_sim: float
) -> float:
    regex_score     = get_regex_score(entity_name, value)
    proximity_score = get_keyword_proximity_score(entity_name, source_clause)

    score = (
        0.40 * regex_score     +
        0.35 * proximity_score +
        0.25 * levenshtein_sim
    )

    return round(score, 3)


def compute_risk_analysis(extraction: dict, default_events: list | None) -> dict:
    """
    Basic borrower-side risk score from 0–10 plus contributing factors.
    """
    score = 0.0
    factors: list[str] = []

    # Interest rate
    try:
        ir = extraction.get("interest_rate", {}).get("value")
        if ir is not None:
            ir_f = float(str(ir).replace("%", "").strip())
            if ir_f >= 36:
                score += 4
                factors.append("Very high interest rate")
            elif ir_f >= 24:
                score += 3
                factors.append("High interest rate")
            elif ir_f >= 18:
                score += 2
                factors.append("Moderately high interest rate")
    except Exception:
        pass

    # Penalty interest
    try:
        pen = extraction.get("penalty_interest", {}).get("value")
        if pen is not None:
            pen_f = float(str(pen).replace("%", "").strip())
            if pen_f >= 36:
                score += 2
                factors.append("High penalty interest on late payments")
    except Exception:
        pass

    # Prepayment penalty
    pre = extraction.get("prepayment_penalty", {})
    if isinstance(pre, dict) and pre.get("value") not in (None, 0, "0"):
        score += 1
        factors.append("Prepayment penalty if you repay early")

    # Collateral
    coll = extraction.get("collateral") or {}
    if isinstance(coll, dict) and coll.get("present"):
        score += 2
        factors.append("Loan secured by collateral that may be seized on default")

    # Default events
    if default_events:
        hard_triggers = [e for e in default_events if isinstance(e, dict)]
        if len(hard_triggers) >= 3:
            score += 1.5
            factors.append("Many events of default defined in the contract")

    # Math / consistency
    fs = compute_financial_summary(extraction)
    if fs:
        eff = fs.get("effective_interest_pct")
        if eff and eff > 50:
            score += 1.5
            factors.append("Very high effective cost relative to principal")

    # Clamp 0–10
    score = max(0.0, min(10.0, score))

    return {"score": round(score, 1), "factors": factors}


# ═══════════════════════════════════════════════
# MAIN VALIDATION FUNCTION
# ═══════════════════════════════════════════════

def validate_extraction(extraction: dict, full_contract: str) -> dict:
    validated = {}

    for entity_name, entity_data in extraction.items():
        if not isinstance(entity_data, dict):
            continue

        value         = entity_data.get("value")
        source_clause = entity_data.get("source_clause", "")

        if value is None:
            validated[entity_name] = {
                **entity_data,
                "confidence":   None,
                "is_verified":  None,
                "flag":         None
            }
            continue

        
        hallucination_result = check_hallucination(str(value), source_clause, full_contract)

        confidence = calculate_confidence(
            entity_name,
            str(value),
            source_clause,
            hallucination_result["similarity"]
        )

     
        flag = None
        if not hallucination_result["is_verified"]:
            flag = "⚠️ Could not verify this value in the source contract"
        elif confidence < CONFIDENCE_THRESHOLD:
            flag = "⚠️ Low confidence — please verify manually"

        validated[entity_name] = {
            **entity_data,
            "confidence":      confidence,
            "is_verified":     hallucination_result["is_verified"],
            "similarity":      hallucination_result["similarity"],
            "verify_method":   hallucination_result["method"],
            "flag":            flag
        }

    math_check = check_mathematical_consistency(extraction)
    financial_summary = compute_financial_summary(extraction)

    # default_events may be a list (not a dict with value/source_clause)
    default_events = extraction.get("default_events") or []
    risk_analysis = compute_risk_analysis(extraction, default_events)

    return {
        "entities":           validated,
        "math_check":         math_check,
        "financial_summary":  financial_summary,
        "risk_analysis":      risk_analysis,
        "default_events":     default_events,
    }