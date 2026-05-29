import re
import datetime
import json
import os
import httpx
import pdfplumber
import spacy
from typing import Any
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

print("[cv_parser] Loading spaCy model...")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("spaCy model not found. Run: python -m spacy download en_core_web_sm")

# VOCABULARIES
SKILL_KEYWORDS: dict[str, list[str]] = {
    "python":                   ["python"],
    "java":                     ["java"],
    "javascript":               ["javascript", "js"],
    "typescript":               ["typescript"],
    "c++":                      ["c++", "cpp"],
    "c#":                       ["c#", "csharp"],
    "sql":                      ["sql", "mysql", "postgresql", "sqlite", "pl/sql"],
    "r":                        [r"\br\b"],
    "bash":                     ["bash", "shell scripting"],
    "go":                       [r"\bgo\b", "golang"],
    "react":                    ["react", "reactjs", "react.js"],
    "nextjs":                   ["next.js", "nextjs"],
    "html":                     ["html", "html5"],
    "css":                      ["css", "css3", "tailwind", "bootstrap"],
    "nodejs":                   ["node.js", "nodejs", "express"],
    "restapi":                  ["rest api", "restful", "rest"],
    "graphql":                  ["graphql"],
    "pandas":                   ["pandas"],
    "numpy":                    ["numpy"],
    "sklearn":                  ["scikit-learn", "sklearn"],
    "tensorflow":               ["tensorflow"],
    "pytorch":                  ["pytorch", "torch"],
    "keras":                    ["keras"],
    "matplotlib":               ["matplotlib", "seaborn", "plotly"],
    "powerbi":                  ["power bi", "powerbi"],
    "tableau":                  ["tableau"],
    "excel":                    ["excel", "ms excel"],
    "mongodb":                  ["mongodb", "mongo"],
    "redis":                    ["redis"],
    "aws":                      ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "gcp":                      ["gcp", "google cloud"],
    "azure":                    ["azure", "microsoft azure"],
    "docker":                   ["docker"],
    "kubernetes":               ["kubernetes", "k8s"],
    "git":                      ["git", "github", "gitlab"],
    "linux":                    ["linux", "ubuntu", "centos"],
    "network_security":         ["network security", "firewall", "ids", "ips"],
    "pentesting":               ["penetration testing", "pentesting", "ethical hacking"],
    "cryptography":             ["cryptography", "encryption", "ssl", "tls"],
    "siem":                     ["siem", "splunk", "qradar"],
    "vulnerability_assessment": ["vulnerability assessment", "nmap", "metasploit", "burp suite"],
    "owasp":                    ["owasp"],
    "nlp":                      ["nlp", "natural language processing", "spacy", "nltk", "bert", "transformers"],
    "computer_vision":          ["computer vision", "opencv", "image processing"],
    "mlops":                    ["mlops", "mlflow", "kubeflow"],
    "statistics":               ["statistics", "probability", "regression", "hypothesis testing"],
    "data_wrangling":           ["data wrangling", "data cleaning", "etl"],
}

EDUCATION_KEYWORDS = {
    "phd":       ["phd", "ph.d", "doctorate", "doctor of philosophy"],
    "masters":   ["ms", "m.s", "msc", "m.sc", "master", "masters", "m.e", "m.tech"],
    "bachelors": ["bs", "b.s", "bsc", "b.sc", "bachelor", "b.e", "b.tech", "be", "bcs", "bscs"],
    "associate": ["associate", "a.s", "a.a"],
    "diploma":   ["diploma", "certificate"],
}

EXPERIENCE_PATTERNS = [
    r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
    r"(\d+)\+?\s*yrs?\s+(?:of\s+)?experience",
    r"experience[:\s]+(\d+)\+?\s*years?",
]

# PUBLIC API
def parse_cv(pdf_path: str) -> dict[str, Any]:
    raw_text = _extract_text(pdf_path)

    skills = _extract_skills(raw_text)
    edu    = _extract_education(raw_text)
    exp    = _extract_experience(raw_text)
    certs  = _extract_certifications(raw_text)

    llm_data = _extract_via_gemini(raw_text)
    projects = llm_data.get("projects", [])
    orgs     = llm_data.get("organisations", [])

    facts = {
        "raw_text":         raw_text,
        "skills":           skills,
        "education_level":  edu,
        "years_experience": exp,
        "projects":         projects,
        "organisations":    orgs,
        "certifications":   certs,
    }

    print(f"[cv_parser] Done: {len(skills)} skills | edu={edu} | "
          f"exp={exp}yr | {len(projects)} projects | "
          f"{len(certs)} certs | {len(orgs)} orgs")
    return facts

# STEP 1: PDF TEXT EXTRACTION
def _extract_text(pdf_path: str) -> str:
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)

_GEMINI_PROMPT = """You are a CV/resume parser. Extract structured data from the resume text below.
Return ONLY valid JSON with exactly these two keys:
- "projects": list of project title strings (name only — no descriptions, no roles, no links)
- "organisations": list of employer/company name strings (name only — no job titles, no dates, no locations)

Rules:
- Projects: extract only the NAME. "PicoShell | Engineer | Code" → "PicoShell". Skip all bullet descriptions.
- Organisations: extract only the COMPANY NAME. "Senior Engineer   PURELOGICS" → "Purelogics".
- Do NOT include Kaggle, LinkedIn, GitHub, Medium, or portfolio platforms as organisations.
- Do NOT include universities unless the person was employed there as staff.
- Return proper casing — not ALL CAPS.
- If nothing found for a field return an empty list [].

Example output:
{"projects": ["PicoShell", "TagMe", "Mood Music Generator"], "organisations": ["Walmart Inc.", "Google", "NVIDIA"]}

CV TEXT:
"""

def _extract_via_gemini(raw_text: str) -> dict[str, list[str]]:
    if not GEMINI_API_KEY:
        print("[cv_parser] WARNING: GEMINI_API_KEY not set in .env file")
        print("[cv_parser] Get free key at https://aistudio.google.com → Get API key")
        print("[cv_parser] Falling back to rule-based extraction...")
        return _extract_fallback(raw_text)

    # Truncate to 8000 chars — covers 3 pages, well within Gemini token limits
    text_chunk = raw_text[:8000]

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": _GEMINI_PROMPT + text_chunk}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1,
            "maxOutputTokens": 3000
        }
    }

    # Retry up to 3 times on 429, with increasing wait: 5s → 15s → 30s
    retry_delays = [5, 15, 30]

    for attempt, delay in enumerate(retry_delays, start=1):
        try:
            response = httpx.post(url, json=payload, timeout=30.0)

            # Handle 429 rate limit specifically — wait and retry
            if response.status_code == 429:
                if attempt < len(retry_delays):
                    print(f"[cv_parser] Gemini rate limited (429). "
                          f"Waiting {delay}s before retry {attempt}/{len(retry_delays)-1}...")
                    import time
                    time.sleep(delay)
                    continue
                else:
                    print("[cv_parser] Gemini rate limit persists after retries. "
                          "Using rule-based fallback.")
                    return _extract_fallback(raw_text)

            response.raise_for_status()

            data       = response.json()
            raw_output = data["candidates"][0]["content"]["parts"][0]["text"]

            cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw_output).strip()
            result  = json.loads(cleaned)

            projects = result.get("projects", [])
            orgs     = result.get("organisations", [])
            if not isinstance(projects, list): projects = []
            if not isinstance(orgs, list):     orgs = []

            print(f"[cv_parser] Gemini extracted {len(projects)} projects, {len(orgs)} orgs")
            return {"projects": projects, "organisations": orgs}

        except httpx.HTTPStatusError as e:
            print(f"[cv_parser] Gemini HTTP error {e.response.status_code}. "
                  f"Using rule-based fallback.")
            break
        except KeyError:
            print("[cv_parser] Gemini response format unexpected. Using rule-based fallback.")
            break
        except json.JSONDecodeError as e:
            print(f"[cv_parser] Gemini returned invalid JSON: {e}. Using rule-based fallback.")
            break
        except Exception as e:
            print(f"[cv_parser] Gemini failed ({type(e).__name__}). Using rule-based fallback.")
            break

    return _extract_fallback(raw_text)

# RULE-BASED FALLBACK
# Used when Gemini is unavailable (429, no key, network error).
_BULLET_CHARS  = frozenset("-•*▪●·◦–•▪")
_DESC_VERBS    = re.compile(
    r"^(a|an|the|this|developed|implemented|created|designed|built|used|"
    r"worked|led|managed|integrated|configured|optimized|deployed|connected|"
    r"incorporated|expanded|generated|collaborated|architected|established|"
    r"performed|contributed|leveraged|engineered|spearheaded)\b",
    re.IGNORECASE
)
_CORP_SUFFIX   = re.compile(
    r"\b(inc|llc|corp|ltd|limited|co|company|group|associates|partners|"
    r"solutions|technologies|services|systems)\b",
    re.IGNORECASE
)
_JOB_TITLE_WORDS = {
    "engineer","analyst","developer","manager","programmer","architect",
    "lead","consultant","intern","specialist","director","officer",
    "coordinator","designer","scientist","volunteer"
}
_SECTION_MAP = [
    (r"project",                           "projects"),
    (r"experience|employment|workhistory", "experience"),
    (r"education|academic|qualification",  "education"),
    (r"skill|technical|certification",     "misc"),
    (r"summary|objective|profile",        "summary"),
]

def _segment_cv(text: str) -> dict[str, list[str]]:
    segments: dict[str, list[str]] = {
        "summary": [], "experience": [],
        "education": [], "projects": [], "misc": []
    }
    current = "summary"
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        clean = stripped.rstrip("_-=. \t")
        compressed = re.sub(r"\s+", "", clean).lower()
        matched = None
        if len(clean) < 65:
            for pattern, section_name in _SECTION_MAP:
                if re.search(pattern, compressed):
                    matched = section_name
                    break
        if matched:
            current = matched
            continue
        segments[current].append(line)
    return segments


def _extract_fallback(raw_text: str) -> dict[str, list[str]]:
    print("[cv_parser] Running rule-based fallback for projects + orgs")
    segments = _segment_cv(raw_text)
    projects = _fallback_projects(segments["projects"])
    orgs     = _fallback_orgs(segments["experience"], raw_text)
    print(f"[cv_parser] Fallback extracted {len(projects)} projects, {len(orgs)} orgs")
    return {"projects": projects, "organisations": orgs}


def _fallback_projects(project_lines: list[str]) -> list[str]:
    projects = []

    for line in project_lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped[0] in _BULLET_CHARS:
            rest = stripped[1:].strip()  
            if ":" in rest:
                candidate = rest.split(":")[0].strip()
                candidate = re.sub(r"\s*\([^)]*\)\s*$", "", candidate).strip()
                if (3 < len(candidate) <= 60
                        and not _DESC_VERBS.match(candidate)
                        and candidate[0].isupper()
                        and not candidate.endswith(".")):   
                    projects.append(candidate)
            continue  

        if _DESC_VERBS.match(stripped):
            continue
        if len(stripped) > 80 or len(stripped) < 3:
            continue
        if stripped[0].islower():
            continue
        if re.match(r"^\d{4}", stripped):
            continue
        if stripped.endswith("."):
            continue

        title = stripped
        for sep in ["●", " | ", " — ", " – ", "\t"]:
            if sep in title:
                title = title.split(sep)[0].strip()
                break

        if len(title) > 2:
            projects.append(title)

    seen = set()
    return [p for p in projects if not (p.lower() in seen or seen.add(p.lower()))]

    seen: set[str] = set()
    unique = []
    for p in projects:
        if p.lower() not in seen:
            seen.add(p.lower())
            unique.append(p)
    return unique


def _fallback_orgs(experience_lines: list[str], full_text: str) -> list[str]:
    entities: set[str] = set()

    for line in experience_lines:
        if line != line.lstrip() and line.strip():
            continue

        stripped = line.strip()
        if not stripped:
            continue

        if stripped[0] in _BULLET_CHARS:
            continue

        if len(stripped) > 80:
            continue

        if _DESC_VERBS.match(stripped):
            continue

        # Strategy 1: corporate suffix (most reliable)
        suffix_match = _CORP_SUFFIX.search(stripped)
        if suffix_match:
            candidate = stripped[:suffix_match.end()].strip().rstrip(",. ")
            words_before = candidate.split()
            if (len(candidate) >= 3
                    and len(words_before) <= 6
                    and words_before[0][0].isupper()):
                entities.add(candidate.title() if candidate.isupper() else candidate)
            continue

        # Strategy 2a: right-side split on 2+ spaces or tab
        right_split = re.split(r"\s{2,}|\t", stripped)
        if len(right_split) >= 2:
            candidate = right_split[-1].strip()
            if (len(candidate) >= 2
                    and candidate[0].isupper()
                    and not _DESC_VERBS.match(candidate)
                    and not any(t in candidate.lower() for t in _JOB_TITLE_WORDS)
                    and not re.search(r"\d{4}", candidate)
                    and len(candidate.split()) <= 4):
                entities.add(candidate)
            continue

        # Strategy 2b: last ALL-CAPS word cluster at end of line
        # Handles "Senior Data Scientist & ML Engineer PURELOGICS" (single space)
        last_caps = re.search(r"\s([A-Z][A-Z0-9]+(?:\s[A-Z][A-Z0-9]+)*)$", stripped)
        if last_caps:
            candidate = last_caps.group(1).strip()
            if (len(candidate) >= 3
                    and not any(t in candidate.lower() for t in _JOB_TITLE_WORDS)
                    and len(candidate.split()) <= 3):
                entities.add(candidate.title())
            continue

        # Strategy 3: spaCy NER on short non-indented lines
        normalized = stripped.title() if stripped.isupper() else stripped
        doc = nlp(normalized)
        for ent in doc.ents:
            if ent.label_ != "ORG":
                continue
            ent_text = ent.text.strip().strip(",.- ")
            if (len(ent_text) >= 3
                    and not ent_text.isdigit()
                    and not any(t in ent_text.lower() for t in _JOB_TITLE_WORDS)):
                entities.add(ent_text)

    sorted_by_length = sorted(entities, key=len, reverse=True)
    unique: list[str] = []
    for org in sorted_by_length:
        if not any(org.lower() in existing.lower() for existing in unique):
            unique.append(org)

    return sorted(unique)

# STEP 3: SKILLS (full text, keyword matching)
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

# STEP 4: EDUCATION (full text, keyword matching)
def _extract_education(text: str) -> str:
    text_lower = text.lower()
    for level in ["phd", "masters", "bachelors", "associate", "diploma"]:
        for keyword in EDUCATION_KEYWORDS[level]:
            if keyword in text_lower:
                return level
    return "unknown"

# STEP 5: EXPERIENCE (full text, date math)
def _extract_experience(text: str) -> float:
    text_lower    = text.lower()
    current_year  = datetime.datetime.now().year

    for pattern in EXPERIENCE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return float(match.group(1))

    year_ranges = re.findall(
        r"(\d{4})\s*[-\u2013\u2014\u2010\u2011]\s*(present|current|now|\d{4})",
        text_lower
    )
    durations = []
    for start, end in year_ranges:
        start_yr = int(start)
        end_yr   = current_year if end in ("present", "current", "now") else int(end)
        if 1990 <= start_yr <= current_year and end_yr >= start_yr:
            durations.append(end_yr - start_yr)

    return float(max(durations)) if durations else 0.0

# STEP 6: CERTIFICATIONS (full text, pattern match)
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
    found      = []
    text_lower = text.lower()
    for pat in cert_patterns:
        matches = re.findall(pat, text_lower)
        found.extend([m.strip() for m in matches])
    return list(set(found))