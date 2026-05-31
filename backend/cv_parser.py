import re
import datetime
import json
import os
import httpx
import pdfplumber
from typing import Any
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# SKILL VOCABULARY  (used by rule-based fallback only)
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

SKILL_KEYS = sorted(SKILL_KEYWORDS.keys())

def parse_cv(pdf_path: str) -> dict[str, Any]:
    raw_text = _extract_text(pdf_path)
    facts    = _extract_via_gemini(raw_text)

    print(
        f"[cv_parser] Done: {len(facts['skills'])} skills | "
        f"edu={facts['education_level']} | "
        f"exp={facts['years_experience']}yr | "
        f"{len(facts['projects'])} projects | "
        f"{len(facts['certifications'])} certs | "
        f"{len(facts['organisations'])} orgs"
    )
    return facts

# PDF TEXT EXTRACTION

def _extract_text(pdf_path: str) -> str:
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)

#GEMINI FULL EXTRACTION
_GEMINI_PROMPT = """You are a precise CV/resume parser. Extract structured data from the resume text below.

Return ONLY valid JSON with exactly these keys:

{{
  "education_level": "<one of: phd | masters | bachelors | associate | diploma | unknown>",
  "years_experience": <float — total NON-OVERLAPPING years of professional work experience>,
  "skills": [<list of matched skill keys from the SKILL VOCABULARY below>],
  "projects": [<list of project title strings — names only, no descriptions>],
  "certifications": [<list of full certification name strings>],
  "organisations": [<list of employer/company name strings — names only>]
}}

━━━━━━━━━━━━━━━━━━━━━━━━
EXTRACTION RULES
━━━━━━━━━━━━━━━━━━━━━━━━

education_level:
  - Return the HIGHEST degree the candidate holds.
  - "Bachelor in Computer Science" → "bachelors".
  - "Kaggle Master" or "Master of Ceremonies" are NOT degrees — ignore them.
  - If no degree is mentioned return "unknown".

years_experience:
  - Sum up ALL work experience date ranges, de-overlapping concurrent roles.
  - Handle formats: "Jan 2021 – Dec 2021", "01/2021 – 12/2021", "2021 – Present", "12/2024 – Currently".
  - "Currently" / "Present" / "Now" = {current_year} (today's year).
  - If two jobs overlap in time, count those months only ONCE.
  - Return a float rounded to 1 decimal place (e.g. 5.5).

skills:
  - Return ONLY keys from this exact vocabulary list — do not invent new keys:
    {skill_keys}
  - Match liberally: "Hugging Face Transformers" → "nlp", "SciKit-Learn" → "sklearn",
    "OpenCV" → "computer_vision", "REST APIs" → "restapi", "GitHub Actions" → "git".

projects:
  - Extract the project NAME only. Strip descriptions, bullet text, tech stack.
  - "• Health Assistance Application (LLM): Architected..." → "Health Assistance Application"
  - Include ALL projects listed under a Projects section.

certifications:
  - Extract the FULL certification name as written.
  - Include specializations, professional certificates, exam preps.
  - "IBM Machine Learning Specialization Professional Certificate, IBM." → keep it as-is.
  - A two-column layout may put two certs on one line separated by "•" — extract both.

organisations:
  - Employer/company names only. No job titles, dates, or locations.
  - Do NOT include universities, Kaggle, GitHub, LinkedIn, or portfolio sites.
  - "Senior Data Scientist & ML Engineer   PURELOGICS" → "Purelogics"

━━━━━━━━━━━━━━━━━━━━━━━━
RESUME TEXT
━━━━━━━━━━━━━━━━━━━━━━━━
{cv_text}
"""

def _extract_via_gemini(raw_text: str) -> dict[str, Any]:
    if not GEMINI_API_KEY:
        print("[cv_parser] WARNING: GEMINI_API_KEY not set — using rule-based fallback.")
        return _rule_based_fallback(raw_text)

    current_year = datetime.datetime.now().year
    prompt = _GEMINI_PROMPT.format(
        current_year=current_year,
        skill_keys=", ".join(SKILL_KEYS),
        cv_text=raw_text[:32000],   # 32k chars — well within Gemini's context window
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1,
            "maxOutputTokens": 4000,
        },
    }

    retry_delays = [5, 15, 30]
    for attempt, delay in enumerate(retry_delays, start=1):
        try:
            response = httpx.post(url, json=payload, timeout=45.0)

            if response.status_code == 429:
                if attempt < len(retry_delays):
                    print(f"[cv_parser] Gemini rate limited — retrying in {delay}s "
                          f"(attempt {attempt}/{len(retry_delays) - 1})...")
                    import time; time.sleep(delay)
                    continue
                print("[cv_parser] Gemini rate limit persists — using fallback.")
                return _rule_based_fallback(raw_text)

            response.raise_for_status()

            data       = response.json()
            raw_output = data["candidates"][0]["content"]["parts"][0]["text"]
            cleaned    = re.sub(r"```(?:json)?\s*|\s*```", "", raw_output).strip()
            result     = json.loads(cleaned)

            return _validate_and_clean(result, raw_text)

        except (httpx.HTTPStatusError, KeyError, json.JSONDecodeError, Exception) as e:
            print(f"[cv_parser] Gemini error ({type(e).__name__}: {e}) — using fallback.")
            break

    return _rule_based_fallback(raw_text)


def _validate_and_clean(result: dict, raw_text: str) -> dict[str, Any]:
    """Validate Gemini output and fill any missing/invalid fields via fallback."""
    valid_edu = {"phd", "masters", "bachelors", "associate", "diploma", "unknown"}
    valid_skills = set(SKILL_KEYS)

    edu = result.get("education_level", "unknown")
    if edu not in valid_edu:
        edu = "unknown"

    try:
        exp = float(result.get("years_experience", 0))
        if exp < 0 or exp > 60:
            exp = 0.0
    except (TypeError, ValueError):
        exp = 0.0

    skills = [s for s in result.get("skills", []) if s in valid_skills]

    projects = [str(p).strip() for p in result.get("projects", []) if str(p).strip()]
    certs    = [str(c).strip() for c in result.get("certifications", []) if str(c).strip()]
    orgs     = [str(o).strip() for o in result.get("organisations", []) if str(o).strip()]

    # If Gemini missed critical fields, patch with rule-based values
    fallback = None
    if not skills:
        print("[cv_parser] Gemini returned no skills — patching with rule-based.")
        fallback = fallback or _rule_based_fallback(raw_text)
        skills = fallback["skills"]
    if edu == "unknown":
        fallback = fallback or _rule_based_fallback(raw_text)
        edu = fallback["education_level"]
    if exp == 0.0:
        fallback = fallback or _rule_based_fallback(raw_text)
        exp = fallback["years_experience"]
    if not projects:
        fallback = fallback or _rule_based_fallback(raw_text)
        projects = fallback["projects"]
    if not certs:
        fallback = fallback or _rule_based_fallback(raw_text)
        certs = fallback["certifications"]

    return {
        "raw_text":         raw_text,
        "education_level":  edu,
        "years_experience": exp,
        "skills":           sorted(skills),
        "projects":         projects,
        "certifications":   certs,
        "organisations":    orgs,
    }

# RULE-BASED FALLBACK  (used when Gemini is unavailable)

def _rule_based_fallback(raw_text: str) -> dict[str, Any]:
    print("[cv_parser] Running full rule-based fallback.")
    return {
        "raw_text":         raw_text,
        "education_level":  _fb_education(raw_text),
        "years_experience": _fb_experience(raw_text),
        "skills":           _fb_skills(raw_text),
        "projects":         _fb_projects(raw_text),
        "certifications":   _fb_certifications(raw_text),
        "organisations":    _fb_organisations(raw_text),
    }


#Fallback: Skills 

def _fb_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = set()
    for skill_key, aliases in SKILL_KEYWORDS.items():
        for alias in aliases:
            pattern = alias if alias.startswith(r"\b") else re.escape(alias)
            if re.search(pattern, text_lower):
                found.add(skill_key)
                break
    return sorted(found)

_EDU_PATTERNS: dict[str, list[str]] = {
    "phd":       [r"\bphd\b", r"\bph\.d\.?\b", r"\bdoctorate\b"],
    "masters":   [r"\bm\.?sc\.?\b", r"\bmaster(?:s|'s)?\s+(?:of|in|degree)\b", r"\bm\.?tech\b"],
    "bachelors": [r"\bb\.?sc\.?\b", r"\bbachelor(?:s|'s)?", r"\bb\.?tech\b", r"\bbcs\b", r"\bbscs?\b"],
    "associate": [r"\bassociate\b"],
    "diploma":   [r"\bdiploma\b"],
}

def _fb_education(text: str) -> str:
    m = re.search(
        r"education\s*[_\-=]{3,}(.*?)(?:\n[A-Z][A-Z\s]+[_\-=]{3,}|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    search_text = m.group(1).lower() if m else text.lower()

    for level in ["phd", "masters", "bachelors", "associate", "diploma"]:
        for pattern in _EDU_PATTERNS[level]:
            if re.search(pattern, search_text):
                return level
    return "unknown"


_OPEN_ENDS = frozenset(["present", "current", "currently", "now", "ongoing", "today"])
_EXP_EXPLICIT = [
    r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
    r"(\d+)\+?\s*yrs?\s+(?:of\s+)?experience",
    r"experience[:\s]+(\d+)\+?\s*years?",
]

def _fb_experience(text: str) -> float:
    text_lower    = text.lower()
    current_year  = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    for pattern in _EXP_EXPLICIT:
        m = re.search(pattern, text_lower)
        if m:
            return float(m.group(1))

    _DASH = r"[-\u2013\u2014\u2010\u2011]"
    jobs: list[tuple[int, int, int, int]] = []

    for start, end in re.findall(
        rf"(\d{{4}})\s*{_DASH}\s*(present|current|currently|now|ongoing|today|\d{{4}})",
        text_lower
    ):
        s_yr = int(start)
        e_yr, e_mo = (current_year, current_month) if end in _OPEN_ENDS else (int(end), 12)
        if 1990 <= s_yr <= current_year:
            jobs.append((s_yr, 1, e_yr, e_mo))

    for sm, sy, em, ey in re.findall(
        rf"(\d{{1,2}})[/\.](\d{{4}})\s*{_DASH}\s*(\d{{1,2}})[/\.](\d{{4}})",
        text_lower
    ):
        s_yr, s_mo, e_yr, e_mo = int(sy), int(sm), int(ey), int(em)
        if 1990 <= s_yr <= current_year and 1 <= s_mo <= 12 and 1 <= e_mo <= 12:
            jobs.append((s_yr, s_mo, e_yr, e_mo))

    for sm, sy in re.findall(
        rf"(\d{{1,2}})[/\.](\d{{4}})\s*{_DASH}\s*(?:present|current|currently|now|ongoing|today)",
        text_lower
    ):
        s_yr, s_mo = int(sy), int(sm)
        if 1990 <= s_yr <= current_year and 1 <= s_mo <= 12:
            jobs.append((s_yr, s_mo, current_year, current_month))

    if not jobs:
        return 0.0

    months_worked: set[tuple[int, int]] = set()
    for s_yr, s_mo, e_yr, e_mo in jobs:
        yr, mo = s_yr, s_mo
        while (yr, mo) <= (e_yr, e_mo):
            months_worked.add((yr, mo))
            mo += 1
            if mo > 12:
                mo, yr = 1, yr + 1

    return round(len(months_worked) / 12, 1)

_BULLET_CHARS = frozenset("-•*▪●·◦–•▪")
_DESC_VERBS   = re.compile(
    r"^(a|an|the|this|developed|implemented|created|designed|built|used|"
    r"worked|led|managed|integrated|configured|optimized|deployed|connected|"
    r"incorporated|expanded|generated|collaborated|architected|established|"
    r"performed|contributed|leveraged|engineered|spearheaded)\b",
    re.IGNORECASE
)

def _fb_projects(text: str) -> list[str]:
    m = re.search(
        r"projects?\s*[_\-=]{3,}(.*?)(?:\n[A-Z][A-Z\s]+[_\-=]{3,}|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    block = m.group(1) if m else text
    projects = []

    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped[0] in _BULLET_CHARS:
            rest = stripped[1:].strip()
            if ":" in rest:
                candidate = rest.split(":")[0].strip()
                candidate = re.sub(r"\s*\([^)]*\)\s*$", "", candidate).strip()
                if 3 < len(candidate) <= 80 and not _DESC_VERBS.match(candidate) and candidate[0].isupper():
                    projects.append(candidate)

    seen: set[str] = set()
    return [p for p in projects if not (p.lower() in seen or seen.add(p.lower()))]

def _fb_certifications(text: str) -> list[str]:
    certs: list[str] = []

    m = re.search(
        r"certifications?\s*[_\-=]{3,}(.*?)(?:\n[A-Z][A-Z\s]+[_\-=]{3,}|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    if m:
        for raw in re.split(r"[•\n]", m.group(1)):
            for item in [s.strip() for s in raw.split("•") if s.strip()]:
                item = re.sub(r"\s+", " ", item).strip(" .,•")
                if len(item) > 10 and re.search(
                    r"\b(certificate|specialization|certification|exam\s+prep|"
                    r"operations|professional|architect|analytics|engineer|fundamentals)\b",
                    item, re.IGNORECASE
                ):
                    certs.append(item)

    seen: set[str] = set()
    return [c for c in certs if not (c.lower() in seen or seen.add(c.lower()))]


_CORP_SUFFIX    = re.compile(
    r"\b(inc|llc|corp|ltd|limited|co|company|group|associates|partners|"
    r"solutions|technologies|services|systems)\b", re.IGNORECASE
)
_JOB_TITLE_WORDS = {
    "engineer", "analyst", "developer", "manager", "programmer", "architect",
    "lead", "consultant", "intern", "specialist", "director", "officer",
    "coordinator", "designer", "scientist", "volunteer",
}

def _fb_organisations(text: str) -> list[str]:
    m = re.search(
        r"experience\s*[_\-=]{3,}(.*?)(?:\nProjects|Education|Certifications|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    block_lines = m.group(1).splitlines() if m else text.splitlines()
    entities: set[str] = set()

    for line in block_lines:
        if line != line.lstrip() and line.strip():
            continue
        stripped = line.strip()
        if not stripped or stripped[0] in _BULLET_CHARS or len(stripped) > 80:
            continue
        if _DESC_VERBS.match(stripped):
            continue

        sfx = _CORP_SUFFIX.search(stripped)
        if sfx:
            candidate = stripped[:sfx.end()].strip().rstrip(",. ")
            words = candidate.split()
            if len(candidate) >= 3 and len(words) <= 6 and words[0][0].isupper():
                entities.add(candidate.title() if candidate.isupper() else candidate)
            continue

        parts = re.split(r"\s{2,}|\t", stripped)
        if len(parts) >= 2:
            candidate = parts[-1].strip()
            if (len(candidate) >= 2 and candidate[0].isupper()
                    and not _DESC_VERBS.match(candidate)
                    and not any(t in candidate.lower() for t in _JOB_TITLE_WORDS)
                    and not re.search(r"\d{4}", candidate)
                    and len(candidate.split()) <= 4):
                entities.add(candidate)
            continue

        last_caps = re.search(r"\s([A-Z][A-Z0-9]+(?:\s[A-Z][A-Z0-9]+)*)$", stripped)
        if last_caps:
            candidate = last_caps.group(1).strip()
            if (len(candidate) >= 3
                    and not any(t in candidate.lower() for t in _JOB_TITLE_WORDS)
                    and len(candidate.split()) <= 3):
                entities.add(candidate.title())

    sorted_by_len = sorted(entities, key=len, reverse=True)
    unique: list[str] = []
    for org in sorted_by_len:
        if not any(org.lower() in existing.lower() for existing in unique):
            unique.append(org)
    return sorted(unique)