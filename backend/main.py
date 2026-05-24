"""
main.py — HireWise FastAPI Backend
All routes, startup logic, CORS, and orchestration.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import tempfile
import os

from dotenv import load_dotenv
load_dotenv()

# ── Local modules (stubbed until Day 2-5) ─────────────────
from cv_parser import parse_cv
from engine import evaluate_candidate
from fuzzy import fuzzy_score
from rag import get_improvement_tips
from report import generate_report
from mailer import send_result_email

# ──────────────────────────────────────────────────────────
app = FastAPI(
    title="HireWise API",
    description="AI-powered recruitment expert system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PASS_THRESHOLD = float(os.getenv("PASS_THRESHOLD", 0.90))

# ──────────────────────────────────────────────────────────
# Pydantic Models
# ──────────────────────────────────────────────────────────

class JobRole(BaseModel):
    company_name: str
    role_title: str                # must match one of the 5 covered roles
    description: Optional[str] = ""
    custom_rules: Optional[dict] = {}   # future: company-level rule overrides


class EvaluationResult(BaseModel):
    candidate_email: str
    role_title: str
    score: float                   # 0.0 – 1.0
    passed: bool
    rules_passed: list[str]
    rules_failed: list[str]
    improvement_tips: list[str]
    report_path: Optional[str]     # path to generated PDF


# ──────────────────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "HireWise API is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# ──────────────────────────────────────────────────────────
# Company Routes
# ──────────────────────────────────────────────────────────

@app.get("/roles")
async def list_roles():
    """Return the 5 supported job roles."""
    return {
        "roles": [
            "Software Engineer",
            "Data Analyst",
            "Web Developer",
            "Cybersecurity Analyst",
            "Machine Learning Engineer",
        ]
    }


@app.post("/roles/create")
async def create_role(job: JobRole):
    """
    Company posts a job role.
    In this prototype, roles are predefined. Custom rules can extend defaults.
    """
    supported = {
        "Software Engineer", "Data Analyst", "Web Developer",
        "Cybersecurity Analyst", "Machine Learning Engineer"
    }
    if job.role_title not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Role '{job.role_title}' not supported. Choose from: {supported}"
        )
    # TODO Day 5+: persist to DB / in-memory store
    return {
        "message": f"Role '{job.role_title}' created for {job.company_name}",
        "role": job.model_dump(),
    }


# ──────────────────────────────────────────────────────────
# Candidate Routes
# ──────────────────────────────────────────────────────────

@app.post("/apply", response_model=EvaluationResult)
async def apply(
    role_title: str,
    candidate_email: str,
    cv_file: UploadFile = File(...),
):
    """
    Full pipeline:
      1. Save uploaded PDF
      2. Parse CV (PyMuPDF + spaCy + HuggingFace NER)
      3. Run expert system (PyKnow forward chaining)
      4. Apply fuzzy scoring
      5. Retrieve RAG improvement tips
      6. Generate PDF report
      7. Send email
      8. Return result
    """
    # ── 1. Save PDF to temp file ───────────────────────────
    if cv_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files accepted.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await cv_file.read())
        tmp_path = tmp.name

    try:
        # ── 2. Parse CV ───────────────────────────────────
        candidate_facts = parse_cv(tmp_path)
        candidate_facts["email"] = candidate_email
        candidate_facts["role"] = role_title

        # ── 3. Expert system evaluation ───────────────────
        engine_result = evaluate_candidate(candidate_facts, role_title)

        # ── 4. Fuzzy scoring overlay ──────────────────────
        final_score = fuzzy_score(engine_result, candidate_facts, role_title)

        passed = final_score >= PASS_THRESHOLD

        # ── 5. RAG improvement tips ───────────────────────
        tips = get_improvement_tips(
            role=role_title,
            failed_rules=engine_result["rules_failed"],
            candidate_facts=candidate_facts,
        ) if not passed else []

        # ── 6. Generate PDF report ────────────────────────
        report_path = generate_report(
            candidate_facts=candidate_facts,
            engine_result=engine_result,
            score=final_score,
            tips=tips,
            role=role_title,
        )

        # ── 7. Send email ─────────────────────────────────
        send_result_email(
            to_email=candidate_email,
            passed=passed,
            score=final_score,
            role=role_title,
            report_path=report_path if not passed else None,
        )

        # ── 8. Return result ──────────────────────────────
        return EvaluationResult(
            candidate_email=candidate_email,
            role_title=role_title,
            score=round(final_score, 4),
            passed=passed,
            rules_passed=engine_result["rules_passed"],
            rules_failed=engine_result["rules_failed"],
            improvement_tips=tips,
            report_path=report_path,
        )

    finally:
        os.unlink(tmp_path)   # clean up temp PDF


@app.post("/parse-cv")
async def parse_cv_only(cv_file: UploadFile = File(...)):
    """Debug endpoint — returns raw extracted facts from a CV."""
    if cv_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files accepted.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await cv_file.read())
        tmp_path = tmp.name

    try:
        facts = parse_cv(tmp_path)
        return {"facts": facts}
    finally:
        os.unlink(tmp_path)


# ──────────────────────────────────────────────────────────
# Dev entry point
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
