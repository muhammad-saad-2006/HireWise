from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import tempfile
import os

from dotenv import load_dotenv
load_dotenv()

from cv_parser import parse_cv
from engine import evaluate_candidate
from fuzzy import fuzzy_score
from rag import get_improvement_tips
from report import generate_report
from mailer import send_result_email

app = FastAPI(
    title="HireWise API",
    description="AI-powered recruitment expert system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated PDF reports as static files
reports_dir = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(reports_dir, exist_ok=True)
app.mount("/reports", StaticFiles(directory=reports_dir), name="reports")

PASS_THRESHOLD = float(os.getenv("PASS_THRESHOLD", 0.75))

# ─────────────────────────────────────────────
# IN-MEMORY COMPANY STORE
# In a real system this would be a database.
# For the demo this persists as long as the server runs.
# ─────────────────────────────────────────────
_companies: list[dict] = []

SUPPORTED_ROLES = {
    "software engineer",
    "data analyst",
    "web developer",
    "cybersecurity analyst",
    "machine learning engineer",
}

# ─────────────────────────────────────────────
# PYDANTIC MODELS
# ─────────────────────────────────────────────

class JobRole(BaseModel):
    company_name: str
    role_title: str
    description: Optional[str] = ""
    contact_email: str                    # Company email for receiving applications
    custom_threshold: Optional[float] = None  # Override global threshold (0.0–1.0)

class RuleResult(BaseModel):
    rule: str
    weight: float
    description: str

class EvaluationResult(BaseModel):
    candidate_email: str
    role_title: str
    company_name: str
    score: float
    passed: bool
    rules_passed: list[RuleResult]
    rules_failed: list[RuleResult]
    improvement_tips: list[str]
    report_path: str

# ─────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "HireWise API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# ─────────────────────────────────────────────
# ROLES
# ─────────────────────────────────────────────

@app.get("/roles")
async def list_roles():
    return {"roles": [r.title() for r in SUPPORTED_ROLES]}

# ─────────────────────────────────────────────
# COMPANY ROUTES
# ─────────────────────────────────────────────

@app.post("/companies/create")
async def create_company(job: JobRole):
    role_key = job.role_title.strip().lower()
    if role_key not in SUPPORTED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Role '{job.role_title}' not supported. Choose from: {list(SUPPORTED_ROLES)}"
        )
    company = {
        "id": len(_companies) + 1,
        "company_name": job.company_name,
        "role_title": role_key,
        "description": job.description,
        "contact_email": job.contact_email,
        "threshold": job.custom_threshold if job.custom_threshold else PASS_THRESHOLD,
    }
    _companies.append(company)
    return {"message": f"Company '{job.company_name}' registered for role '{role_key}'", "company": company}


@app.get("/companies")
async def get_all_companies():
    """Return all registered companies."""
    return {"companies": _companies}


@app.get("/companies/role/{role_title}")
async def get_companies_by_role(role_title: str):
    """Return companies hiring for a specific role."""
    role_key = role_title.strip().lower()
    matches = [c for c in _companies if c["role_title"] == role_key]
    return {"companies": matches, "role": role_key, "count": len(matches)}


# ─────────────────────────────────────────────
# CANDIDATE ROUTES
# ─────────────────────────────────────────────

@app.post("/apply", response_model=EvaluationResult)
async def apply(
    role_title: str,
    candidate_email: str,
    company_id: Optional[int] = None,
    cv_file: UploadFile = File(...),
):
    """
    Full pipeline:
    1. Parse CV
    2. Run expert system
    3. Fuzzy scoring
    4. RAG improvement tips
    5. Generate PDF report
    6. Send email (invite or rejection)
    7. Return result
    """
    if cv_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files accepted.")

    # Resolve company
    company = None
    if company_id:
        matches = [c for c in _companies if c["id"] == company_id]
        if not matches:
            raise HTTPException(status_code=404, detail=f"Company ID {company_id} not found.")
        company = matches[0]
        role_title = company["role_title"]

    role_key = role_title.strip().lower()
    if role_key not in SUPPORTED_ROLES:
        raise HTTPException(status_code=400, detail=f"Unknown role '{role_title}'. Supported: {list(SUPPORTED_ROLES)}")

    threshold = company["threshold"] if company else PASS_THRESHOLD
    company_name = company["company_name"] if company else "HireWise"

    # Save PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await cv_file.read())
        tmp_path = tmp.name

    try:
        # 1. Parse
        candidate_facts = parse_cv(tmp_path)
        candidate_facts["email"] = candidate_email
        candidate_facts["role"] = role_key

        # 2. Expert system
        engine_result = evaluate_candidate(candidate_facts, role_key)

        # 3. Fuzzy score
        final_score = fuzzy_score(engine_result, candidate_facts, role_key)
        passed = final_score >= threshold

        # 4. RAG tips (only for failures)
        tips = get_improvement_tips(
            role=role_key,
            failed_rules=engine_result["rules_failed"],
            candidate_facts=candidate_facts,
        ) if not passed else []

        # 5. PDF report
        report_url = generate_report(
            candidate_facts=candidate_facts,
            engine_result=engine_result,
            score=final_score,
            tips=tips,
            role=role_key,
        )

        # 6. Email
        send_result_email(
            to_email=candidate_email,
            passed=passed,
            score=final_score,
            role=role_key,
            report_path=report_url if not passed else None,
            company_name=company_name,
            company_email=company["contact_email"] if company else None,
        )

        # 7. Return
        return EvaluationResult(
            candidate_email=candidate_email,
            role_title=role_key,
            company_name=company_name,
            score=round(final_score, 4),
            passed=passed,
            rules_passed=engine_result["rules_passed"],
            rules_failed=engine_result["rules_failed"],
            improvement_tips=tips,
            report_path=report_url or "",
        )

    finally:
        os.unlink(tmp_path)


@app.post("/parse-cv")
async def parse_cv_only(cv_file: UploadFile = File(...)):
    """Debug endpoint — returns raw extracted facts."""
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)