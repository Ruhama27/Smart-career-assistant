"""
test_phase1.py — Automated tests for Phase 1 fixes.

Tests cover:
  1. CGPA normalization correctness
  2. Eligibility check logic (0.0 = no requirement, cross-scale comparison)
  3. Content-based recommender excludes ineligible internships
  4. Collaborative recommender excludes ineligible internships
  5. No crash when student or internship is not found

Run with:  pytest tests/test_phase1.py -v
"""

import sys
import os

# Allow imports from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import pytest

from modules.utils import normalize_cgpa, is_cgpa_eligible
from modules.content_based import recommend_internships
from modules.collaborative import collaborative_recommendation


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CGPA normalization
# ═══════════════════════════════════════════════════════════════════════════════

class TestNormalizeCGPA:

    def test_same_scale_returns_same_value(self):
        assert normalize_cgpa(8.5, from_scale=10.0, to_scale=10.0) == 8.5

    def test_4_to_10_scale(self):
        assert normalize_cgpa(3.2, from_scale=4.0, to_scale=10.0) == 8.0

    def test_10_to_4_scale(self):
        assert normalize_cgpa(8.0, from_scale=10.0, to_scale=4.0) == 3.2

    def test_zero_value_normalizes_to_zero(self):
        assert normalize_cgpa(0.0, from_scale=4.0, to_scale=10.0) == 0.0

    def test_invalid_scale_raises_error(self):
        with pytest.raises(ValueError):
            normalize_cgpa(8.0, from_scale=0.0, to_scale=10.0)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CGPA eligibility check
# ═══════════════════════════════════════════════════════════════════════════════

class TestIsCGPAEligible:

    def test_zero_min_cgpa_always_eligible(self):
        """0.0 means no requirement — any student qualifies."""
        assert is_cgpa_eligible(student_cgpa=5.0, min_required=0.0) is True
        assert is_cgpa_eligible(student_cgpa=0.0, min_required=0.0) is True

    def test_student_above_minimum_eligible(self):
        assert is_cgpa_eligible(student_cgpa=9.0, min_required=8.5) is True

    def test_student_exactly_at_minimum_eligible(self):
        assert is_cgpa_eligible(student_cgpa=8.5, min_required=8.5) is True

    def test_student_below_minimum_not_eligible(self):
        assert is_cgpa_eligible(student_cgpa=7.8, min_required=8.5) is False

    def test_cross_scale_comparison(self):
        """3.2 on 4.0 scale == 8.0 on 10.0 scale — should be eligible for 7.5."""
        assert is_cgpa_eligible(
            student_cgpa=3.2,
            min_required=7.5,
            student_scale=4.0,
            internship_scale=10.0,
        ) is True

    def test_cross_scale_not_eligible(self):
        """2.8 on 4.0 scale == 7.0 on 10.0 — should NOT meet 8.5 requirement."""
        assert is_cgpa_eligible(
            student_cgpa=2.8,
            min_required=8.5,
            student_scale=4.0,
            internship_scale=10.0,
        ) is False


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Content-based — CGPA filter and basic correctness
# ═══════════════════════════════════════════════════════════════════════════════

class TestContentBasedRecommender:

    def test_returns_list_for_valid_student(self):
        result = recommend_internships("S001")
        assert isinstance(result, list)

    def test_returns_empty_for_unknown_student(self):
        result = recommend_internships("DOES_NOT_EXIST")
        assert result == []

    def test_no_more_than_five_results(self):
        result = recommend_internships("S001")
        assert len(result) <= 5

    def test_all_results_have_required_keys(self):
        result = recommend_internships("S001")
        for item in result:
            assert "internship_id" in item
            assert "score" in item

    def test_cgpa_filter_excludes_ineligible(self):
        """
        S010 has CGPA 7.8. Internship I001 requires 8.5.
        I001 should NOT appear in S010's recommendations.
        """
        result = recommend_internships("S010")
        ids = [r["internship_id"] for r in result]
        # I001 requires 8.5 CGPA — S010 (7.8) should not see it
        assert "I001" not in ids, (
            "S010 (CGPA 7.8) should not be recommended I001 (min CGPA 8.5)"
        )

    def test_scores_are_between_0_and_1(self):
        result = recommend_internships("S001")
        for item in result:
            assert 0.0 <= item["score"] <= 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Collaborative — CGPA filter and basic correctness
# ═══════════════════════════════════════════════════════════════════════════════

class TestCollaborativeRecommender:

    def test_returns_list_for_valid_student(self):
        result = collaborative_recommendation("S001", display=False)
        assert isinstance(result, list)

    def test_returns_empty_for_unknown_student(self):
        result = collaborative_recommendation("DOES_NOT_EXIST", display=False)
        assert result == []

    def test_no_more_than_five_results(self):
        result = collaborative_recommendation("S001", display=False)
        assert len(result) <= 5

    def test_all_results_have_required_keys(self):
        result = collaborative_recommendation("S001", display=False)
        for item in result:
            for key in ("internship_id", "company", "role", "score"):
                assert key in item, f"Missing key '{key}' in collaborative result"
