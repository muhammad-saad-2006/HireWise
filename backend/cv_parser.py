
import re
import pdfplumber                    
import spacy
from transformers import pipeline
from typing import Any

# Load models (loaded once at module import)
print("[cv_parser] Loading spaCy model...")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError(
        "spaCy model not found. Run: python -m spacy download en_core_web_sm"
    )

print("[cv_parser] Loading HuggingFace NER model...")
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

# Master skill vocabulary
SKILL_KEYWORDS: dict[str, list[str]] = {
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp"],
    "sql": ["sql", "mysql", "postgresql", "sqlite", "pl/sql"],
    "r": [r"\br\b"],
    "bash": ["bash", "shell scripting"],
    "go": [r"\bgo\b", "golang"],
    "react": ["react", "reactjs", "react.js"],
    "nextjs": ["next.js", "nextjs"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "tailwind", "bootstrap"],
    "nodejs": ["node.js", "nodejs", "express"],
    "restapi": ["rest api", "restful", "rest"],
    "graphql": ["graphql"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "sklearn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "keras": ["keras"],
    "matplotlib": ["matplotlib", "seaborn", "plotly"],
    "powerbi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "excel": ["excel", "ms excel"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "gcp": ["gcp", "google cloud"],
    "azure": ["azure", "microsoft azure"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "git": ["git", "github", "gitlab"],
    "linux": ["linux", "ubuntu", "centos"],
    "network_security": ["network security", "firewall", "ids", "ips"],
    "pentesting": ["penetration testing", "pentesting", "ethical hacking"],
    "cryptography": ["cryptography", "encryption", "ssl", "tls"],
    "siem": ["siem", "splunk", "qradar"],
    "vulnerability_assessment": ["vulnerability assessment", "nmap", "metasploit", "burp suite"],
    "owasp": ["owasp"],
    "nlp": ["nlp", "natural language processing", "spacy", "nltk", "bert", "transformers"],
    "computer_vision": ["computer vision", "opencv", "image processing"],
    "mlops": ["mlops", "mlflow", "kubeflow"],
    "statistics": ["statistics", "probability", "regression", "hypothesis testing"],
    "data_wrangling": ["data wrangling", "data cleaning", "etl"],
}

EDUCATION_KEYWORDS = {
    "phd": ["phd", "ph.d", "doctorate", "doctor of philosophy"],
    "masters": ["ms", "m.s", "msc", "m.sc", "master", "masters", "m.e", "m.tech"],
    "bachelors": ["bs", "b.s", "bsc", "b.sc", "bachelor", "b.e", "b.tech", "be", "bcs", "bscs"],
    "associate": ["associate", "a.s", "a.a"],
    "diploma": ["diploma", "certificate"],
}

EXPERIENCE_PATTERNS = [
    r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
    r"(\d+)\+?\s*yrs?\s+(?:of\s+)?experience",
    r"experience[:\s]+(\d+)\+?\s*years?",
    r"(\d{4})\s*[-–]\s*(?:present|current|now)",
]

# Public API
def parse_cv(pdf_path: str) -> dict[str, Any]:
    raw_text = _extract_text(pdf_path)       
    skills   = _extract_skills(raw_text)
    edu      = _extract_education(raw_text)
    exp      = _extract_experience(raw_text)
    projects = _extract_projects(raw_text)
    certs    = _extract_certifications(raw_text)
    orgs     = _extract_ner_entities(raw_text, entity_type="ORG")

    facts = {
        "raw_text":         raw_text,
        "skills":           skills,
        "education_level":  edu,
        "years_experience": exp,
        "projects":         projects,
        "organisations":    orgs,
        "certifications":   certs,
    }

    print(f"[cv_parser] Extracted facts: "
          f"{len(skills)} skills | edu={edu} | exp={exp}yr | "
          f"{len(projects)} projects | {len(certs)} certs")
    return facts
# Step 1: pdfplumber text extraction  
def _extract_text(pdf_path: str) -> str:
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:                      
                pages.append(text)
    return "\n".join(pages)

def _extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = set()
    for skill_key, aliases in SKILL_KEYWORDS.items():
        for alias in aliases:
            pattern = alias if alias.startswith(r"\b") else re.escape(alias)
            if re.search(pattern, text_lower):
                found.add(skill_key)
                break
    return sorted(found)


def _extract_education(text: str) -> str:
    text_lower = text.lower()
    hierarchy = ["phd", "masters", "bachelors", "associate", "diploma"]
    for level in hierarchy:
        for keyword in EDUCATION_KEYWORDS[level]:
            if keyword in text_lower:
                return level
    return "unknown"


def _extract_experience(text: str) -> float:
    import datetime
    text_lower = text.lower()
    current_year = datetime.datetime.now().year

    for pattern in EXPERIENCE_PATTERNS[:3]:
        match = re.search(pattern, text_lower)
        if match:
            return float(match.group(1))

    year_ranges = re.findall(r"(\d{4})\s*[-–]\s*(present|current|now|\d{4})", text_lower)
    durations = []
    for start, end in year_ranges:
        start_yr = int(start)
        end_yr = current_year if end in ("present", "current", "now") else int(end)
        if 1990 <= start_yr <= current_year and end_yr >= start_yr:
            durations.append(end_yr - start_yr)
    return float(max(durations)) if durations else 0.0


def _extract_projects(text: str) -> list[str]:
    projects = []
    lines = text.splitlines()
    in_section = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        heading_lower = stripped.lower()
        if re.match(r"(personal\s+)?projects?(\s+&\s+\w+)?", heading_lower):
            in_section = True
            continue
        if in_section and re.match(
            r"(education|experience|skills|certifications|awards|summary|objective)",
            heading_lower
        ):
            in_section = False
        if in_section and len(stripped) > 5:
            projects.append(stripped)
    return projects[:10]


def _extract_certifications(text: str) -> list[str]:
    cert_patterns = [
        r"aws\s+certified[\w\s]+",
        r"google\s+cloud\s+[\w\s]+certificate",
        r"microsoft\s+certified[\w\s]+",
        r"cisco\s+ccna",
        r"certified\s+ethical\s+hacker",
        r"oscp",
        r"comptia\s+[\w+]+",
        r"pmp",
        r"coursera[\w\s]+certificate",
        r"udemy[\w\s]+certificate",
    ]
    found = []
    text_lower = text.lower()
    for pat in cert_patterns:
        matches = re.findall(pat, text_lower)
        found.extend([m.strip() for m in matches])
    return list(set(found))


def _extract_ner_entities(text: str, entity_type: str = "ORG") -> list[str]:
    max_chars = 1500
    chunks = [text[i:i+max_chars] for i in range(0, min(len(text), 9000), max_chars)]
    entities = set()
    for chunk in chunks:
        try:
            results = ner_pipeline(chunk)
            for ent in results:
                if ent["entity_group"] == entity_type and ent["score"] > 0.85:
                    entities.add(ent["word"].strip())
        except Exception as e:
            print(f"[cv_parser] NER chunk error: {e}")
    return sorted(entities)