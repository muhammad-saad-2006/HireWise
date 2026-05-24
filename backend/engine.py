from experta import *
from rules import ROLE_RULES

# FACT CLASSES
class HasSkill(Fact):
    """One fact per detected skill.  HasSkill(name="python")"""
    pass

class Experience(Fact):
    """Total years of experience.  Experience(years=3.5)"""
    pass

class Education(Fact):
    """Highest education level.  Education(level="masters")"""
    pass

class ProjectCount(Fact):
    """Number of listed projects.  ProjectCount(count=4)"""
    pass

class HasCertification(Fact):
    """One fact per certification string.  HasCertification(name="CEH")"""
    pass

# KNOWLEDGE ENGINE
class CandidateEngine(KnowledgeEngine):
    def __init__(self, role_rules: list[dict]):
        super().__init__()
        self._role_rules = role_rules   # list of rule dicts from rules.py
        self._fired:   list[dict] = []
        self._unfired: list[dict] = []

    @DefFacts()
    def _initial_facts(self):
        yield Fact(initialized=True)

    def evaluate(self, cv_facts: dict):
        for rule in self._role_rules:
            entry = {
                "rule":        rule["name"],
                "weight":      rule["weight"],
                "description": rule["description"],
            }
            if rule["check"](cv_facts):
                self._fired.append(entry)
            else:
                self._unfired.append(entry)

    def get_result(self) -> dict:
        total_weight = sum(r["weight"] for r in self._role_rules)
        fired_weight = sum(r["weight"] for r in self._fired)
        raw_score    = round(fired_weight / total_weight, 4) if total_weight else 0.0

        return {
            "raw_score":    raw_score,
            "passed":       raw_score >= 0.90,
            "rules_passed": self._fired,
            "rules_failed": self._unfired,
            "rule_details": {
                "total_rules":  len(self._role_rules),
                "rules_fired":  len(self._fired),
                "total_weight": round(total_weight, 4),
                "fired_weight": round(fired_weight, 4),
            },
        }

# PUBLIC FUNCTION  (called by main.py)
def evaluate_candidate(cv_facts: dict, role_name: str) -> dict:
    role_key = role_name.strip().lower()
    role_rules = ROLE_RULES.get(role_key)

    if role_rules is None:
        raise ValueError(
            f"Unknown role '{role_name}'. "
            f"Supported: {list(ROLE_RULES.keys())}"
        )

    engine = CandidateEngine(role_rules)
    engine.reset()
    engine.run()

    for skill in cv_facts.get("skills", []):
        engine.declare(HasSkill(name=skill.lower().strip()))

    engine.declare(Experience(years=float(cv_facts.get("years_experience", 0))))
    engine.declare(Education(level=cv_facts.get("education_level", "unknown").lower()))
    engine.declare(ProjectCount(count=len(cv_facts.get("projects", []))))

    for cert in cv_facts.get("certifications", []):
        engine.declare(HasCertification(name=cert.strip()))

    engine.evaluate(cv_facts)

    return engine.get_result()