EDU_RANK = {
    "unknown":   0,
    "diploma":   1,
    "bachelors": 2,
    "masters":   3,
    "phd":       4,
}

def _has(skill: str):
    """Return a checker: does cv_facts['skills'] contain this skill?"""
    def check(f: dict) -> bool:
        return skill.lower() in [s.lower() for s in f.get("skills", [])]
    return check

def _has_any(*skills: str):
    """Return a checker: does cv_facts['skills'] contain ANY of these skills?"""
    skill_set = {s.lower() for s in skills}
    def check(f: dict) -> bool:
        return bool(skill_set & {s.lower() for s in f.get("skills", [])})
    return check

def _exp_gte(min_years: float):
    """Return a checker: years_experience >= min_years?"""
    def check(f: dict) -> bool:
        return float(f.get("years_experience", 0)) >= min_years
    return check

def _edu_gte(minimum: str):
    """Return a checker: education_level >= minimum in EDU_RANK?"""
    def check(f: dict) -> bool:
        level = f.get("education_level", "unknown").lower()
        return EDU_RANK.get(level, 0) >= EDU_RANK.get(minimum, 0)
    return check

def _projects_gte(min_count: int):
    """Return a checker: number of projects >= min_count?"""
    def check(f: dict) -> bool:
        return len(f.get("projects", [])) >= min_count
    return check

def _has_skill_and_exp(skill: str, min_years: float):
    """Return a checker: has the skill AND enough total experience?"""
    def check(f: dict) -> bool:
        return _has(skill)(f) and _exp_gte(min_years)(f)
    return check

def _has_cert_keyword(*keywords: str):
    """Return a checker: any certification string contains one of these keywords?"""
    kws = [k.lower() for k in keywords]
    def check(f: dict) -> bool:
        certs = [c.lower() for c in f.get("certifications", [])]
        return any(kw in cert for cert in certs for kw in kws)
    return check

# 1. SOFTWARE ENGINEER
SOFTWARE_ENGINEER_RULES = [
    {
        "name":        "python_2yr",
        "weight":      0.90,
        "description": "Python with 2+ years experience",
        "check":       _has_skill_and_exp("python", 2),
    },
    {
        "name":        "java",
        "weight":      0.70,
        "description": "Java programming language",
        "check":       _has("java"),
    },
    {
        "name":        "javascript",
        "weight":      0.70,
        "description": "JavaScript programming language",
        "check":       _has("javascript"),
    },
    {
        "name":        "sql",
        "weight":      0.80,
        "description": "SQL / relational databases",
        "check":       _has("sql"),
    },
    {
        "name":        "git",
        "weight":      0.90,
        "description": "Git version control",
        "check":       _has("git"),
    },
    {
        "name":        "docker",
        "weight":      0.60,
        "description": "Docker / containerisation",
        "check":       _has("docker"),
    },
    {
        "name":        "rest_api",
        "weight":      0.80,
        "description": "REST API design / consumption",
        "check":       _has_any("rest", "restapi", "rest_api"),
    },
    {
        "name":        "linux",
        "weight":      0.70,
        "description": "Linux / Unix environment",
        "check":       _has("linux"),
    },
    {
        "name":        "edu_bachelors",
        "weight":      0.80,
        "description": "Bachelor's degree or higher",
        "check":       _edu_gte("bachelors"),
    },
    {
        "name":        "exp_2yr",
        "weight":      0.85,
        "description": "2+ years total work experience",
        "check":       _exp_gte(2),
    },
    {
        "name":        "projects_2",
        "weight":      0.70,
        "description": "2 or more projects on CV",
        "check":       _projects_gte(2),
    },
    {
        "name":        "cloud",
        "weight":      0.50,
        "description": "Cloud platform (AWS / GCP / Azure)",
        "check":       _has_any("aws", "gcp", "azure", "cloud"),
    },
]

# 2. DATA ANALYST  
DATA_ANALYST_RULES = [
    {
        "name":        "sql_2yr",
        "weight":      0.95,
        "description": "SQL with 2+ years experience",
        "check":       _has_skill_and_exp("sql", 2),
    },
    {
        "name":        "python",
        "weight":      0.80,
        "description": "Python programming language",
        "check":       _has("python"),
    },
    {
        "name":        "excel",
        "weight":      0.80,
        "description": "Microsoft Excel / spreadsheets",
        "check":       _has("excel"),
    },
    {
        "name":        "pandas",
        "weight":      0.85,
        "description": "Pandas data manipulation library",
        "check":       _has("pandas"),
    },
    {
        "name":        "statistics",
        "weight":      0.90,
        "description": "Statistics / probability knowledge",
        "check":       _has_any("statistics", "probability", "stats"),
    },
    {
        "name":        "data_wrangling",
        "weight":      0.85,
        "description": "Data wrangling / cleaning skills",
        "check":       _has_any("pandas", "numpy", "data_wrangling", "data_cleaning"),
    },
    {
        "name":        "visualization",
        "weight":      0.75,
        "description": "Data visualisation (matplotlib / Power BI / Tableau)",
        "check":       _has_any("matplotlib", "powerbi", "tableau", "seaborn", "plotly"),
    },
    {
        "name":        "r_language",
        "weight":      0.60,
        "description": "R programming language",
        "check":       _has("r"),
    },
    {
        "name":        "edu_bachelors",
        "weight":      0.80,
        "description": "Bachelor's degree or higher",
        "check":       _edu_gte("bachelors"),
    },
    {
        "name":        "exp_1yr",
        "weight":      0.80,
        "description": "1+ year total work experience",
        "check":       _exp_gte(1),
    },
    {
        "name":        "projects_1",
        "weight":      0.70,
        "description": "1 or more projects on CV",
        "check":       _projects_gte(1),
    },
    {
        "name":        "database",
        "weight":      0.70,
        "description": "Database knowledge (SQL / NoSQL)",
        "check":       _has_any("sql", "mongodb", "postgresql", "mysql", "sqlite"),
    },
]

# 3. WEB DEVELOPER  
WEB_DEVELOPER_RULES = [
    {
        "name":        "html",
        "weight":      0.95,
        "description": "HTML markup language",
        "check":       _has("html"),
    },
    {
        "name":        "css",
        "weight":      0.90,
        "description": "CSS styling",
        "check":       _has("css"),
    },
    {
        "name":        "js_2yr",
        "weight":      0.95,
        "description": "JavaScript with 2+ years experience",
        "check":       _has_skill_and_exp("javascript", 2),
    },
    {
        "name":        "react",
        "weight":      0.80,
        "description": "React.js framework",
        "check":       _has("react"),
    },
    {
        "name":        "nodejs",
        "weight":      0.70,
        "description": "Node.js runtime",
        "check":       _has_any("nodejs", "node"),
    },
    {
        "name":        "git",
        "weight":      0.85,
        "description": "Git version control",
        "check":       _has("git"),
    },
    {
        "name":        "rest_api",
        "weight":      0.75,
        "description": "REST API consumption / design",
        "check":       _has_any("rest", "restapi", "rest_api"),
    },
    {
        "name":        "projects_3",
        "weight":      0.80,
        "description": "3 or more projects on CV",
        "check":       _projects_gte(3),
    },
    {
        "name":        "database",
        "weight":      0.60,
        "description": "SQL or MongoDB database skills",
        "check":       _has_any("sql", "mongodb"),
    },
    {
        "name":        "edu_diploma",
        "weight":      0.70,
        "description": "Diploma or higher education",
        "check":       _edu_gte("diploma"),
    },
    {
        "name":        "exp_1yr",
        "weight":      0.75,
        "description": "1+ year total work experience",
        "check":       _exp_gte(1),
    },
    {
        "name":        "typescript",
        "weight":      0.60,
        "description": "TypeScript",
        "check":       _has("typescript"),
    },
]

# 4. CYBERSECURITY ANALYST 
CYBERSECURITY_ANALYST_RULES = [
    {
        "name":        "network_security",
        "weight":      0.95,
        "description": "Network security knowledge",
        "check":       _has_any("network_security", "networking", "firewall", "ids", "ips"),
    },
    {
        "name":        "linux",
        "weight":      0.85,
        "description": "Linux / Unix environment",
        "check":       _has("linux"),
    },
    {
        "name":        "python",
        "weight":      0.70,
        "description": "Python scripting",
        "check":       _has("python"),
    },
    {
        "name":        "pen_testing",
        "weight":      0.80,
        "description": "Penetration testing",
        "check":       _has_any("penetration_testing", "pentest", "metasploit", "nmap"),
    },
    {
        "name":        "cryptography",
        "weight":      0.75,
        "description": "Cryptography knowledge",
        "check":       _has_any("cryptography", "encryption", "pki", "tls", "ssl"),
    },
    {
        "name":        "siem",
        "weight":      0.70,
        "description": "SIEM tools (Splunk / QRadar)",
        "check":       _has_any("splunk", "siem", "qradar", "elk"),
    },
    {
        "name":        "vuln_assessment",
        "weight":      0.85,
        "description": "Vulnerability assessment",
        "check":       _has_any("vulnerability_assessment", "nessus", "openvas", "burpsuite"),
    },
    {
        "name":        "owasp",
        "weight":      0.70,
        "description": "OWASP Top 10 knowledge",
        "check":       _has_any("owasp", "web_security"),
    },
    {
        "name":        "bash",
        "weight":      0.65,
        "description": "Bash / shell scripting",
        "check":       _has_any("bash", "shell_scripting", "powershell"),
    },
    {
        "name":        "edu_bachelors",
        "weight":      0.80,
        "description": "Bachelor's degree or higher",
        "check":       _edu_gte("bachelors"),
    },
    {
        "name":        "exp_2yr",
        "weight":      0.85,
        "description": "2+ years total work experience",
        "check":       _exp_gte(2),
    },
    {
        "name":        "certifications",
        "weight":      0.75,
        "description": "Security certifications (CEH / OSCP / CompTIA Security+)",
        "check":       _has_cert_keyword("ceh", "oscp", "comptia", "security+", "cissp", "cism", "ejpt"),
    },
]

# 5. MACHINE LEARNING ENGINEER  
MACHINE_LEARNING_ENGINEER_RULES = [
    {
        "name":        "python_2yr",
        "weight":      0.95,
        "description": "Python with 2+ years experience",
        "check":       _has_skill_and_exp("python", 2),
    },
    {
        "name":        "sklearn",
        "weight":      0.85,
        "description": "scikit-learn ML library",
        "check":       _has_any("scikit_learn", "sklearn", "scikit-learn"),
    },
    {
        "name":        "dl_framework",
        "weight":      0.80,
        "description": "TensorFlow or PyTorch deep-learning framework",
        "check":       _has_any("tensorflow", "pytorch", "keras"),
    },
    {
        "name":        "pandas",
        "weight":      0.85,
        "description": "Pandas data manipulation",
        "check":       _has("pandas"),
    },
    {
        "name":        "numpy",
        "weight":      0.80,
        "description": "NumPy numerical computing",
        "check":       _has("numpy"),
    },
    {
        "name":        "statistics",
        "weight":      0.90,
        "description": "Statistics / probability / math",
        "check":       _has_any("statistics", "probability", "linear_algebra", "stats"),
    },
    {
        "name":        "nlp",
        "weight":      0.70,
        "description": "NLP / text processing knowledge",
        "check":       _has_any("nlp", "nltk", "spacy", "huggingface", "transformers"),
    },
    {
        "name":        "git",
        "weight":      0.85,
        "description": "Git version control",
        "check":       _has("git"),
    },
    {
        "name":        "sql",
        "weight":      0.65,
        "description": "SQL / database querying",
        "check":       _has("sql"),
    },
    {
        "name":        "mlops",
        "weight":      0.60,
        "description": "MLOps / model deployment knowledge",
        "check":       _has_any("mlops", "mlflow", "kubeflow", "airflow", "docker", "kubernetes"),
    },
    {
        "name":        "edu_bachelors",
        "weight":      0.85,
        "description": "Bachelor's degree or higher",
        "check":       _edu_gte("bachelors"),
    },
    {
        "name":        "projects_2",
        "weight":      0.75,
        "description": "2 or more projects on CV",
        "check":       _projects_gte(2),
    },
]

#MASTER REGISTRY
ROLE_RULES: dict[str, list[dict]] = {
    "software engineer":          SOFTWARE_ENGINEER_RULES,
    "data analyst":               DATA_ANALYST_RULES,
    "web developer":              WEB_DEVELOPER_RULES,
    "cybersecurity analyst":      CYBERSECURITY_ANALYST_RULES,
    "machine learning engineer":  MACHINE_LEARNING_ENGINEER_RULES,
}