"""
content_based.py — Content-based internship recommendation for PathFinder AI.

Phase 1 changes:
  - CSV files are loaded inside the function (not at module import time),
    so newly added students and internships are always visible immediately.
  - CGPA eligibility filter applied BEFORE ranking:
      internships where min_cgpa > student.cgpa are excluded entirely.
      min_cgpa == 0.0 means "no requirement" — student always qualifies.
  - Uses is_cgpa_eligible() from utils.py so CGPA scales are handled correctly.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from modules.utils import load_students, load_internships, is_cgpa_eligible


def recommend_internships(student_id: str, top_n: int = 5) -> list:
    """
    Recommend the top-N internships for a student using TF-IDF cosine similarity.

    Only internships the student is CGPA-eligible for are considered.

    Parameters
    ----------
    student_id : The student's ID string (e.g. "S001").
    top_n      : Number of recommendations to return (default 5).

    Returns
    -------
    list of dicts with keys: internship_id, score.
    """
    # Phase 1 fix: always load fresh data — never use module-level cached frames
    students    = load_students()
    internships = load_internships()

    # ── Look up the student ────────────────────────────────────────────────
    student_rows = students[students["student_id"] == student_id]

    if student_rows.empty:
        print("Student not found!")
        return []

    student = student_rows.iloc[0]

    # ── Phase 1 fix: CGPA eligibility filter ──────────────────────────────
    # Exclude internships where the student's CGPA is below the minimum.
    # min_cgpa == 0.0 is treated as "no requirement".
    eligible_mask = internships["min_cgpa"].apply(
        lambda min_cgpa: is_cgpa_eligible(
            student_cgpa=student["cgpa"],
            min_required=min_cgpa,
        )
    )
    eligible_internships = internships[eligible_mask].copy()

    if eligible_internships.empty:
        print(
            f"\nNo eligible internships found for student {student_id} "
            f"(CGPA: {student['cgpa']}).\n"
            "Try improving your CGPA or checking back for new listings."
        )
        return []

    excluded_count = len(internships) - len(eligible_internships)
    if excluded_count > 0:
        print(
            f"\n  ℹ  {excluded_count} internship(s) excluded — CGPA requirement not met."
        )

    # ── Build text profiles ────────────────────────────────────────────────
    student_profile = (
        str(student["skills"])      + " " +
        str(student["interests"])   + " " +
        str(student["career_goal"])
    )

    internship_profiles = (
        eligible_internships["required_skills"] + " " +
        eligible_internships["domain"]          + " " +
        eligible_internships["role"]
    )

    # ── TF-IDF cosine similarity ───────────────────────────────────────────
    documents = [student_profile] + list(internship_profiles)

    vectorizer  = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    student_vector      = tfidf_matrix[0]
    internship_vectors  = tfidf_matrix[1:]

    similarity = cosine_similarity(student_vector, internship_vectors).flatten()

    eligible_internships = eligible_internships.copy()
    eligible_internships["match_score"] = similarity

    ranked = eligible_internships.sort_values("match_score", ascending=False)

    # ── Display results ────────────────────────────────────────────────────
    recommendations = []

    print("\n========== TOP RECOMMENDATIONS ==========\n")

    for _, row in ranked.head(top_n).iterrows():
        print(f"Company      : {row['company']}")
        print(f"Role         : {row['role']}")
        print(f"Domain       : {row['domain']}")
        print(f"Match Score  : {round(row['match_score'] * 100, 2)}%")
        min_display = "No requirement" if row["min_cgpa"] == 0.0 else row["min_cgpa"]
        print(f"Min CGPA     : {min_display}")
        print("-" * 45)

        recommendations.append({
            "internship_id": row["internship_id"],
            "score":         row["match_score"],
        })

    return recommendations
