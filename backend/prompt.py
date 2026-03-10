import json

# Core schema for extraction — every financial field has a value and
# source_clause (the exact sentence it came from). We also add extra
# structure for schedules, collateral and default events.
EXTRACTION_SCHEMA = {
    # Core monetary / rate terms
    "loan_amount":          {"value": None, "currency": None, "source_clause": None},
    "interest_rate":        {"value": None, "type": None, "source_clause": None},
    "repayment_duration":   {"value": None, "unit": None, "source_clause": None},
    "monthly_payment":      {"value": None, "source_clause": None},
    "total_cost":           {"value": None, "source_clause": None},
    "payment_frequency":    {"value": None, "source_clause": None},
    "payment_due_day":      {"value": None, "source_clause": None},
    "repayment_start_date": {"value": None, "source_clause": None},

    # Fees — we keep value for simple cases, and logic/base when clauses
    # describe things like "₹X or Y% whichever is higher".
    "late_fee": {
        "value": None, "logic": None, "base": None, "source_clause": None
    },
    "penalty_interest": {
        "value": None, "logic": None, "base": None, "source_clause": None
    },
    "prepayment_penalty": {
        "value": None, "logic": None, "base": None, "source_clause": None
    },
    "processing_fee": {
        "value": None, "logic": None, "base": None, "source_clause": None
    },
    "insurance_fee": {
        "value": None, "logic": None, "base": None, "source_clause": None
    },
    "administrative_fee": {
        "value": None, "logic": None, "base": None, "source_clause": None
    },
    "other_fee": {
        "value": None, "logic": None, "base": None, "source_clause": None
    },

    # Collateral and security
    "collateral": {
        "present": False,
        "description": None,
        "seizure_clause": None,
        "source_clause": None,
    },

    # Repayment schedule (high-level)
    "repayment_schedule": {
        "frequency": None,
        "installment_amount": None,
        "start_condition": None,
        "due_day": None,
        "source_clause": None,
    },

    # Events of default — list of structured triggers
    "default_events": [],  # list of {"trigger": str, "source_clause": str}
}


def build_extraction_prompt(segments: list[dict]) -> str:
    segments_text = ""
    for seg in segments:
        segments_text += f"\n[{seg['label']}]\n{seg['text']}\n"

    prompt = f"""You are a financial document analyst. Extract financial terms from the loan agreement below.

CRITICAL: Return ONLY a valid JSON object. No explanation. No markdown. No preamble. Start your response with {{ and end with }}.

Use this JSON SHAPE exactly (keys and structure must match, values are just examples):

{{
  "loan_amount":          {{"value": 50000, "currency": "Rs.", "source_clause": "exact sentence from contract"}},
  "interest_rate":        {{"value": 24, "type": "flat", "source_clause": "exact sentence with the rate"}},
  "repayment_duration":   {{"value": 24, "unit": "months", "source_clause": "exact sentence with tenure"}},
  "monthly_payment":      {{"value": 3833, "source_clause": "exact sentence with EMI"}},
  "total_cost":           {{"value": 96000, "source_clause": "exact sentence with total payable"}},
  "payment_frequency":    {{"value": "monthly", "source_clause": "exact sentence with frequency"}},
  "payment_due_day":      {{"value": "5th of every month", "source_clause": "exact sentence with due date"}},
  "repayment_start_date": {{"value": "01/01/2026", "source_clause": "exact sentence with the first repayment date"}},

  "late_fee":           {{"value": 250, "logic": "Rs. 250 or 2% of EMI, whichever is higher", "base": "EMI", "source_clause": "full sentence from contract"}},
  "penalty_interest":   {{"value": 36, "logic": "up to 36% p.a. on overdue amount", "base": "overdue amount", "source_clause": "full sentence from contract"}},
  "prepayment_penalty": {{"value": 5,  "logic": "5% of outstanding principal", "base": "outstanding principal", "source_clause": "full sentence from contract"}},
  "processing_fee":     {{"value": 2500, "logic": "minimum of Rs. 2,500", "base": "loan amount", "source_clause": "full sentence from contract"}},
  "insurance_fee":      {{"value": 2400, "logic": null, "base": null, "source_clause": "exact sentence"}},
  "administrative_fee": {{"value": 800,  "logic": null, "base": null, "source_clause": "exact sentence"}},
  "other_fee":          {{"value": null, "logic": null, "base": null, "source_clause": null}},

  "collateral": {{
    "present": true,
    "description": "Residential house at XYZ",
    "seizure_clause": "In case of default, the lender may sell the mortgaged property.",
    "source_clause": "full collateral clause"
  }},

  "repayment_schedule": {{
    "frequency": "monthly",
    "installment_amount": 3833,
    "start_condition": "first EMI due on 1st Feb 2026",
    "due_day": "1st of every month",
    "source_clause": "clause describing repayment schedule"
  }},

  "default_events": [
    {{"trigger": "Payment is overdue by more than 30 days", "source_clause": "full default clause sentence"}},
    {{"trigger": "Borrower becomes insolvent or declares bankruptcy", "source_clause": "full default clause sentence"}}
  ]
}}

R U L E S:
- For every field where the contract clearly states a value, you MUST fill that value (do not leave it null).
- Only use null when the contract truly does not mention that information anywhere.
- Interest type (flat / reducing / simple / compound / diminishing) MUST ONLY be filled when the wording clearly states it (do NOT guess from context).
- For numeric amount fields (loan_amount, monthly_payment, total_cost, all *_fee.value), value must be a NUMBER (no Rs. symbol, no commas).
- For percentage fields (interest_rate.value, penalty_interest.value, prepayment_penalty.value, etc.) value must be a NUMBER without the % sign.
- For repayment_start_date, value must be the calendar date string exactly as written in the contract (e.g. "01/01/2026" or "1 January 2026"), not a number of days or months.
- For conditional fee logic (\"whichever is higher\", \"minimum of\", \"up to\", \"X% of outstanding principal\", \"greater of A or B\"), capture the full human-readable condition in the `logic` field, and the base amount in `base` (e.g. \"outstanding principal\", \"EMI\", \"loan amount\").
- For collateral, set present=true only when the contract clearly mentions collateral / security / pledge / lien / charge on an asset, and describe the asset in description.
- For default_events, list each distinct trigger condition separately, with a short trigger text and its source_clause.
- source_clause must always be copied verbatim from the contract sentence that states the value or condition.
- Never invent or guess values that are not supported by the contract text.

LOAN AGREEMENT:
{segments_text}

JSON:"""

    return prompt


def build_summary_prompt(extraction: dict) -> str:
    """
    Second prompt — takes the structured extraction and generates
    a plain-language summary a non-expert can understand.
    Called after extraction and validation are complete.
    """

    # Pull out key values for the summary
    loan_amount   = extraction.get("loan_amount", {}).get("value", "unknown")
    currency      = extraction.get("loan_amount", {}).get("currency", "Rs.")
    interest_rate = extraction.get("interest_rate", {}).get("value", "unknown")
    duration      = extraction.get("repayment_duration", {}).get("value", "unknown")
    duration_unit = extraction.get("repayment_duration", {}).get("unit", "months")
    monthly       = extraction.get("monthly_payment", {}).get("value", "unknown")
    total         = extraction.get("total_cost", {}).get("value", "unknown")
    late_fee      = extraction.get("late_fee", {}).get("value", "not specified")
    penalty       = extraction.get("penalty_interest", {}).get("value", "not specified")
    processing    = extraction.get("processing_fee", {}).get("value", "not specified")

    prompt = f"""You are explaining a loan agreement to a borrower with no financial background.

Write a plain-language summary in 6-8 sentences using simple words. No financial jargon.
Be direct and clear. If any charges seem high or unusual, mention them as something the borrower should ask about.

EXTRACTED LOAN DETAILS:
- Loan amount: {currency} {loan_amount}
- Interest rate: {interest_rate}%
- Repayment duration: {duration} {duration_unit}
- Monthly payment: {currency} {monthly}
- Total cost of loan: {currency} {total}
- Late payment fee: {late_fee}
- Penalty interest: {penalty}
- Processing fee: {processing}

Write the summary now. Plain English only. No bullet points. Just clear sentences a farmer or shopkeeper can understand."""

    return prompt