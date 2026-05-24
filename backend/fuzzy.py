"""
fuzzy.py — scikit-fuzzy Partial Matching (stub for Day 1)
Full implementation: Day 3
"""

def fuzzy_score(engine_result: dict, candidate_facts: dict, role_title: str) -> float:
    """
    Stub: returns engine raw_score directly.
    Replace on Day 3 with scikit-fuzzy membership functions.
    """
    print(f"[fuzzy] STUB — fuzzy_score called")
    return engine_result.get("raw_score", 0.0)
