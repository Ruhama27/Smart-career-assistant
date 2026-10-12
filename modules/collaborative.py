"""
collaborative.py — Collaborative filtering recommendation for PathFinder AI.

Phase 1 changes:
  - CSV files are loaded inside the function (not at module import time),
    so newly added data is always visible.
  - CGPA eligibility filter applied to final recommendation list.
  - Uses is_cgpa_eligible() from utils.py for correct scale handling.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from modules.utils import load_ratings, load_internships, load_students, is_cgpa_eligible


def collaborative_recommendation(student_id: str,
                                  display: bool = True,
                                  top_n: int = 5) -> list:
    """
    Recommend internships for a student based on ratings from similar students.

    Only internships the student is CGPA-eligible for are returned.

    Parameters
    ----------
    student_id : The student's ID string.
    display    : If True, print results to stdout.
    top_n      : Maximum number of recommendations to return.

    Returns
    -------
    list of dicts with internship details and a predicted collaborative score.
    """
    # Phase 1 fix: always load fresh data inside the function
    ratings     = load_ratings()
    internships = load_internships()
    students    = load_students()

    # ── Build user-item matrix ─────────────────────────────────────────────
    user_item_matrix = ratings.pivot_table(
        index="student_id",
        columns="internship_id",
        values="rating",
        fill_value=0,
    )

    if student_id not in user_item_matrix.index:
        if display:
            print("\nStudent not found in ratings data!")
        return []

    # ── Compute student similarities ───────────────────────────────────────
    sim_matrix     = cosine_similarity(user_item_matrix)
    student_index  = user_item_matrix.index.get_loc(student_id)
    scores         = sim_matrix[student_index]

    similar_indices = np.argsort(scores)[::-1]
    # Exclude the student themselves
    similar_indices = [i for i in similar_indices if i != student_index][:3]

    # ── Aggregate scores from similar students ─────────────────────────────
    recommended: dict = {}

    for idx in similar_indices:
        peer = user_item_matrix.iloc[idx]
        for internship_id, rating in peer.items():
            # Only recommend internships the target student has NOT rated
            if rating > 0 and user_item_matrix.loc[student_id, internship_id] == 0:
                recommended[internship_id] = recommended.get(internship_id, 0) + rating

    ranked = sorted(recommended.items(), key=lambda x: x[1], reverse=True)

    # ── Phase 1 fix: CGPA eligibility filter ──────────────────────────────
    student_rows = students[students["student_id"] == student_id]
    student_cgpa = student_rows.iloc[0]["cgpa"] if not student_rows.empty else 0.0

    recommendation_list = []

    for internship_id, score in ranked:
        row = internships[internships["internship_id"] == internship_id]
        if row.empty:
            continue

        internship = row.iloc[0]

        # Skip internships the student is not eligible for
        if not is_cgpa_eligible(student_cgpa, internship["min_cgpa"]):
            continue

        recommendation_list.append({
            "internship_id": internship_id,
            "company":       internship["company"],
            "role":          internship["role"],
            "domain":        internship["domain"],
            "location":      internship["location"],
            "duration":      internship["duration"],
            "min_cgpa":      internship["min_cgpa"],
            "score":         score,
        })

    # ── Display ────────────────────────────────────────────────────────────
    if display:
        print("\n========== Collaborative Recommendations ==========\n")

        if not recommendation_list:
            print("No collaborative recommendations available.")
            return recommendation_list

        for item in recommendation_list[:top_n]:
            print(f"Company          : {item['company']}")
            print(f"Role             : {item['role']}")
            print(f"Domain           : {item['domain']}")
            print(f"Location         : {item['location']}")
            print(f"Duration         : {item['duration']}")
            print(f"Predicted Rating : {item['score']}")
            print("-" * 45)

    return recommendation_list[:top_n]
