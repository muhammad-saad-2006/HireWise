import skfuzzy as fuzz
import numpy as np

# Years of experience: 0 to 15
_exp_universe = np.arange(0, 16, 0.1)

# Skill count: 0 to 20
_skill_universe = np.arange(0, 21, 1)

# Project count: 0 to 10
_proj_universe = np.arange(0, 11, 1)

# Education rank: 0=unknown, 1=diploma, 2=bachelors, 3=masters, 4=phd
_edu_universe = np.arange(0, 5, 1)

# Output score: 0.0 to 1.0
_score_universe = np.arange(0, 1.01, 0.01)

_EDU_RANK = {
    "unknown":   0,
    "diploma":   1,
    "bachelors": 2,
    "masters":   3,
    "phd":       4,
}

_ROLE_REQUIREMENTS = {
    "software engineer": {
        "min_exp":      2,
        "min_skills":   7,
        "min_projects": 2,
        "min_edu":      2,   # bachelors
    },
    "data analyst": {
        "min_exp":      1,
        "min_skills":   6,
        "min_projects": 1,
        "min_edu":      2,
    },
    "web developer": {
        "min_exp":      1,
        "min_skills":   6,
        "min_projects": 3,
        "min_edu":      1,   # diploma
    },
    "cybersecurity analyst": {
        "min_exp":      2,
        "min_skills":   7,
        "min_projects": 1,
        "min_edu":      2,
    },
    "machine learning engineer": {
        "min_exp":      2,
        "min_skills":   8,
        "min_projects": 2,
        "min_edu":      2,
    },
}


def _membership_experience(years: float, min_years: float) -> float:
    lo = max(0, min_years - 1.0)   # start of ramp
    hi = min_years                  # full membership

    mf = fuzz.trapmf(
        _exp_universe,
        [lo, hi, 15, 15]            
    )
    return float(fuzz.interp_membership(_exp_universe, mf, min(years, 15)))


def _membership_skills(count: int, min_count: int) -> float:
    lo = max(0, min_count - 2)
    hi = min_count

    mf = fuzz.trapmf(
        _skill_universe,
        [lo, hi, 20, 20]
    )
    return float(fuzz.interp_membership(_skill_universe, mf, min(count, 20)))


def _membership_projects(count: int, min_count: int) -> float:
    lo = max(0, min_count - 1)
    hi = min_count

    mf = fuzz.trapmf(
        _proj_universe,
        [lo, hi, 10, 10]
    )
    return float(fuzz.interp_membership(_proj_universe, mf, min(count, 10)))


def _membership_education(edu_level: str, min_edu_rank: int) -> float:
    candidate_rank = _EDU_RANK.get(edu_level.lower(), 0)

    lo = max(0, min_edu_rank - 1)
    hi = min_edu_rank

    mf = fuzz.trapmf(
        _edu_universe,
        [lo, hi, 4, 4]
    )
    return float(fuzz.interp_membership(_edu_universe, mf, candidate_rank))

def _compute_fuzzy_partial(cv_facts: dict, role_key: str) -> float:
    reqs = _ROLE_REQUIREMENTS.get(role_key, {
        "min_exp": 1, "min_skills": 5, "min_projects": 1, "min_edu": 1
    })

    years     = float(cv_facts.get("years_experience", 0))
    skills    = len(cv_facts.get("skills", []))
    projects  = len(cv_facts.get("projects", []))
    edu_level = cv_facts.get("education_level", "unknown")

    m_exp   = _membership_experience(years,    reqs["min_exp"])
    m_skill = _membership_skills(skills,       reqs["min_skills"])
    m_proj  = _membership_projects(projects,   reqs["min_projects"])
    m_edu   = _membership_education(edu_level, reqs["min_edu"])

    weights = {
        "exp":   0.35,
        "skill": 0.35,
        "proj":  0.20,
        "edu":   0.10,
    }

    partial = (
        weights["exp"]   * m_exp   +
        weights["skill"] * m_skill +
        weights["proj"]  * m_proj  +
        weights["edu"]   * m_edu
    )

    print(f"[fuzzy] memberships → exp={m_exp:.3f} | "
          f"skills={m_skill:.3f} | projects={m_proj:.3f} | edu={m_edu:.3f} | "
          f"partial={partial:.3f}")

    return round(partial, 4)

def fuzzy_score(engine_result: dict, candidate_facts: dict, role_title: str) -> float:
    role_key    = role_title.strip().lower()
    hard_score  = engine_result.get("raw_score", 0.0)
    fuzzy_part  = _compute_fuzzy_partial(candidate_facts, role_key)

    # Blend: 60% hard rules + 40% fuzzy partial
    HARD_WEIGHT  = 0.60
    FUZZY_WEIGHT = 0.40

    final = round(HARD_WEIGHT * hard_score + FUZZY_WEIGHT * fuzzy_part, 4)

    print(f"[fuzzy] hard={hard_score:.4f} × {HARD_WEIGHT} + "
          f"fuzzy={fuzzy_part:.4f} × {FUZZY_WEIGHT} = final={final:.4f}")

    return final