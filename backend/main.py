from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.segmenter import segment_contract
from backend.prompt import build_extraction_prompt, build_summary_prompt
from backend.llm_client import run_extraction, run_summary
from backend.validator import validate_extraction
import re

app = FastAPI(
    title="Mifos Loan Agreement Summarizer",
    description="LLM-powered loan agreement extraction and summarization for Mifos X",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContractRequest(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    entities:           dict
    math_check:         dict
    financial_summary:  dict | None = None
    risk_analysis:      dict | None = None
    default_events:     list | None = None
    summary:            str
    segment_count:      int

@app.get("/")
def root():
    return {"status": "running", "service": "Mifos Loan Agreement Summarizer", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_contract(request: ContractRequest):
    try:
        if not request.text or len(request.text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Contract text is too short.")

        segments = segment_contract(request.text)
        if not segments:
            raise HTTPException(status_code=422, detail="Could not segment the contract.")

        extraction_prompt = build_extraction_prompt(segments)
        raw_extraction    = run_extraction(extraction_prompt)

        # Best-effort fix for repayment_start_date: if the model fails to
        # populate a date but the source clause contains one, extract the
        # date string so it shows correctly in the UI.
        rsd = raw_extraction.get("repayment_start_date")
        if isinstance(rsd, dict):
            val = rsd.get("value")
            src = rsd.get("source_clause") or ""
            if (not val) and src:
                m = re.search(
                    r"\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{1,2}\s+\w+\s+\d{4}",
                    src,
                )
                if m:
                    rsd["value"] = m.group(0)

        if not raw_extraction:
            raise HTTPException(status_code=502, detail="LLM did not return valid JSON. Try again.")

        validation_result = validate_extraction(raw_extraction, request.text)
        summary_prompt    = build_summary_prompt(raw_extraction)
        plain_summary     = run_summary(summary_prompt)

        return AnalysisResponse(
            entities          = validation_result["entities"],
            math_check        = validation_result["math_check"],
            financial_summary = validation_result.get("financial_summary") or {},
            risk_analysis     = validation_result.get("risk_analysis") or {},
            default_events    = validation_result.get("default_events") or [],
            summary           = plain_summary,
            segment_count     = len(segments)
        )

    except HTTPException:
        # Let FastAPI handle expected errors with appropriate status codes.
        raise
    except Exception as e:
        # Surface unexpected errors instead of a generic 500 with no detail.
        print("ERROR in /analyze:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))