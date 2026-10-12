"""
hybrid.py — Hybrid recommendation engine for PathFinder AI.

Phase 1 changes:
  - Data is loaded fresh inside the function.
  - CGPA eligibility is enforced via content_based and collaborative modules,
    so no ineligible internship ever appears in the hybrid result.
  - Passes display=False to sub-engines to avoid duplicate output.
"""

import pandas as pd

from modules.utils import load_internships
from modules.content_based import recommend_internships
from modules.collaborative import collaborative_recommendation


def hybrid_recommendation(student_id: str, top_n: int = 5) -> None:
    """
    Combine content-based (70%) and collaborative (30%) scores for a student.

    Only internships that pass the CGPA eligibility check (enforced inside
    each sub-engine) appear in the final result.

    Parameters
    ----------
    student_id : The student's ID string.
    top_n      : Number of results to display.
    """
    # Phase 1 fix: display=False suppresses duplicate output from sub-engines
    content = recommend_internships(student_id, top_n=top_n)
    collab  = collaborative_recommendation(student_id, display=False, top_n=top_n)

    scores: dict = {}

    for item in content:
        scores[item["internship_id"]] = item["score"] * 0.7

    for item in collab:
        iid   = item["internship_id"]
        score = item["score"] * 0.3
        scores[iid] = scores.get(iid, 0) + score

    final_ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    internships = load_internships()

    print("\n========== Hybrid Recommendation ==========\n")

    if not final_ranked:
        print("No hybrid recommendations available.")
        return

    for internship_id, score in final_ranked[:top_n]:
        row = internships[internships["internship_id"] == internship_id]
        if row.empty:
            continue
        internship = row.iloc[0]

        print(f"Company     : {internship['company']}")
        print(f"Role        : {internship['role']}")
        print(f"Location    : {internship['location']}")
        print(f"Final Score : {round(score, 4)}")
        print("-" * 40)
