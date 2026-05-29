_TIPS: dict[str, list[str]] = {

    "global": [
        "Add Git and GitHub to your CV — version control is required for every software role.",
        "List your projects with clear titles, technologies used, and your specific contribution.",
        "Quantify achievements — '40% reduction in load time' is stronger than 'improved performance'.",
        "Include education level explicitly: degree name, institution, and graduation year.",
        "Add a professional summary mentioning your key skills and years of experience.",
        "Include total years of professional experience clearly in your experience section.",
        "List certifications with issuing authority and year obtained.",
        "Use strong action verbs: Architected, Implemented, Optimized, Designed, Deployed.",
        "Tailor your CV to the specific job — highlight the most relevant skills first.",
        "Include at least 2 substantial projects demonstrating end-to-end development skills.",
    ],

    "software engineer": [
        "Learn Python — it is the most in-demand language for software engineering roles.",
        "Add Python projects to your portfolio, even small scripts or automation tools count.",
        "Get comfortable with Docker — containerization is expected for modern software engineers.",
        "Study REST API design principles and build at least one API project.",
        "Practice SQL — relational database knowledge is essential for backend development.",
        "Learn Git branching strategies: feature branches, pull requests, and code reviews.",
        "Add cloud experience: try AWS Free Tier for deploying a small application.",
        "Complete at least 2 end-to-end projects showing full stack or backend expertise.",
        "Study Linux command line basics — most production servers run on Linux.",
        "Aim for a Bachelor's degree or higher in Computer Science or a related field.",
    ],

    "data analyst": [
        "Master SQL — it is the single most important skill for data analysts.",
        "Learn Pandas for data manipulation and cleaning in Python.",
        "Add data visualization skills: matplotlib, seaborn, or Tableau.",
        "Study descriptive and inferential statistics — hypothesis testing and regression.",
        "Build a portfolio with at least one end-to-end analysis project on a real dataset.",
        "Learn Excel advanced features: pivot tables, VLOOKUP, and Power Query.",
        "Practice data wrangling: handling missing values, outliers, and type conversions.",
        "Consider a Power BI or Tableau certification for business intelligence roles.",
        "Use Kaggle datasets to build analysis projects and publish them on GitHub.",
        "Study A/B testing and how to communicate results to non-technical stakeholders.",
    ],

    "web developer": [
        "Build at least 3 complete web projects — portfolio sites, apps, or open source.",
        "Master HTML5 semantic elements and CSS3 flexbox and grid layouts.",
        "Learn React.js — it is the dominant frontend framework for web developer roles.",
        "Add Node.js and Express to build full-stack applications.",
        "Learn TypeScript — type-safe JavaScript is increasingly required in production.",
        "Deploy your projects publicly using Netlify, Vercel, or Heroku.",
        "Learn REST API consumption — fetch data from public APIs in your projects.",
        "Study responsive design and mobile-first development principles.",
        "Add MongoDB or PostgreSQL to one project to show full-stack capability.",
        "Contribute to open source web projects on GitHub to show collaboration skills.",
    ],

    "cybersecurity analyst": [
        "Study network security fundamentals: TCP/IP, firewalls, VPNs, and IDS/IPS systems.",
        "Learn Linux deeply — most security tools run on Linux environments.",
        "Practice penetration testing using Metasploit, Nmap, and Burp Suite.",
        "Study the OWASP Top 10 web application vulnerabilities.",
        "Pursue CompTIA Security+ certification — widely recognized for entry-level roles.",
        "Learn cryptography basics: symmetric/asymmetric encryption, PKI, TLS/SSL.",
        "Practice vulnerability assessment using Nessus or OpenVAS on a home lab.",
        "Learn Splunk or another SIEM tool for log analysis and threat detection.",
        "Set up a home lab using VirtualBox or VMware to practice security scenarios.",
        "Study bash scripting for automating security tasks and log analysis.",
    ],

    "machine learning engineer": [
        "Learn Python deeply — it is the primary language for all ML engineering work.",
        "Master scikit-learn for classical ML algorithms and model evaluation pipelines.",
        "Study deep learning frameworks — PyTorch is preferred in research, TensorFlow in production.",
        "Build strong foundations in linear algebra, calculus, and probability theory.",
        "Learn Pandas and NumPy — data preparation is 80% of ML work.",
        "Build end-to-end ML projects: data collection, preprocessing, training, and deployment.",
        "Study NLP techniques: tokenization, embeddings, transformers, and fine-tuning BERT.",
        "Learn MLOps basics: model versioning with MLflow and containerizing with Docker.",
        "Practice on Kaggle competitions to build real ML problem-solving experience.",
        "Pursue a Master's degree or higher — ML roles often require advanced education.",
    ],
}

_RULE_TO_KEYWORDS: dict[str, list[str]] = {
    "python_2yr":         ["python"],
    "java":               ["java"],
    "javascript":         ["javascript"],
    "sql":                ["sql", "database"],
    "sql_2yr":            ["sql", "database"],
    "git":                ["git", "github", "version control"],
    "docker":             ["docker", "container"],
    "rest_api":           ["rest", "api"],
    "linux":              ["linux"],
    "edu_bachelors":      ["bachelor", "degree", "education"],
    "edu_diploma":        ["diploma", "degree", "education"],
    "exp_2yr":            ["experience", "years"],
    "exp_1yr":            ["experience", "years"],
    "projects_2":         ["project", "portfolio"],
    "projects_3":         ["project", "portfolio"],
    "projects_1":         ["project", "portfolio"],
    "cloud":              ["cloud", "aws", "deploy"],
    "react":              ["react"],
    "nodejs":             ["node", "nodejs"],
    "typescript":         ["typescript"],
    "html":               ["html"],
    "css":                ["css"],
    "pandas":             ["pandas", "data"],
    "numpy":              ["numpy", "data"],
    "statistics":         ["statistics", "math"],
    "visualization":      ["visualization", "tableau", "powerbi"],
    "data_wrangling":     ["data wrangling", "data"],
    "r_language":         ["r language"],
    "database":           ["sql", "database"],
    "excel":              ["excel"],
    "sklearn":            ["scikit-learn", "sklearn"],
    "dl_framework":       ["pytorch", "tensorflow", "deep learning"],
    "nlp":                ["nlp", "language processing"],
    "mlops":              ["mlops", "deployment"],
    "network_security":   ["network security", "firewall"],
    "pen_testing":        ["penetration testing"],
    "cryptography":       ["cryptography", "encryption"],
    "siem":               ["splunk", "siem"],
    "vuln_assessment":    ["vulnerability"],
    "owasp":              ["owasp"],
    "bash":               ["bash", "scripting"],
    "certifications":     ["certification"],
}

def get_improvement_tips(role: str, failed_rules: list, candidate_facts: dict) -> list[str]:
    role_key = role.strip().lower()

    if not failed_rules:
        return []

    query_keywords: set[str] = set()
    for r in failed_rules:
        rule_name = r.get("rule", "")
        keywords  = _RULE_TO_KEYWORDS.get(rule_name, [])
        query_keywords.update(keywords)

    role_tips   = _TIPS.get(role_key, [])
    global_tips = _TIPS["global"]
    all_tips    = role_tips + global_tips

    scored: list[tuple[int, str]] = []
    for tip in all_tips:
        tip_lower = tip.lower()
        score = sum(1 for kw in query_keywords if kw.lower() in tip_lower)
     
        if tip in role_tips:
            score += 0.5
        scored.append((score, tip))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_tips = [tip for _, tip in scored[:5]]

    print(f"[rag] {len(top_tips)} tips matched for role='{role_key}' "
          f"from {len(failed_rules)} failed rules")

    return top_tips