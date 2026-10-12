"""
utils.py — Shared helper functions for PathFinder AI.

Provides:
  - Safe numeric input with validation
  - CGPA normalization across different scales
  - Data loading helpers that always return fresh data
"""

import pandas as pd

# ── File paths ────────────────────────────────────────────────────────────────
STUDENTS_FILE    = "data/students.csv"
INTERNSHIPS_FILE = "data/internships.csv"
RATINGS_FILE     = "data/ratings.csv"


# ── Data loaders (always fresh — never cached at module level) ────────────────

def load_students() -> pd.DataFrame:
    """Load and return the students DataFrame fresh from disk."""
    return pd.read_csv(STUDENTS_FILE)


def load_internships() -> pd.DataFrame:
    """Load and return the internships DataFrame fresh from disk."""
    return pd.read_csv(INTERNSHIPS_FILE)


def load_ratings() -> pd.DataFrame:
    """Load and return the ratings DataFrame fresh from disk."""
    return pd.read_csv(RATINGS_FILE)


def save_students(df: pd.DataFrame) -> None:
    """Persist the students DataFrame to disk."""
    df.to_csv(STUDENTS_FILE, index=False)


def save_internships(df: pd.DataFrame) -> None:
    """Persist the internships DataFrame to disk."""
    df.to_csv(INTERNSHIPS_FILE, index=False)


# ── CGPA helpers ─────────────────────────────────────────────────────────────

def normalize_cgpa(value: float, from_scale: float = 10.0,
                   to_scale: float = 10.0) -> float:
    """
    Normalize a CGPA value from one scale to another.

    Parameters
    ----------
    value      : The raw CGPA value.
    from_scale : The scale the value is currently on (e.g. 4.0 or 10.0).
    to_scale   : The target scale to normalize to.

    Returns
    -------
    float — the normalized CGPA value.

    Examples
    --------
    >>> normalize_cgpa(3.2, from_scale=4.0, to_scale=10.0)
    8.0
    >>> normalize_cgpa(8.0, from_scale=10.0, to_scale=4.0)
    3.2
    """
    if from_scale <= 0 or to_scale <= 0:
        raise ValueError("CGPA scale must be a positive number.")
    return round((value / from_scale) * to_scale, 4)


def is_cgpa_eligible(student_cgpa: float, min_required: float,
                     student_scale: float = 10.0,
                     internship_scale: float = 10.0) -> bool:
    """
    Check whether a student's CGPA meets an internship's minimum requirement.

    Both values are normalized to a common 10.0 scale before comparing,
    so it is safe to compare a 4.0-scale CGPA against a 10.0-scale requirement.

    A min_required of 0.0 means there is NO requirement — the student always passes.

    Parameters
    ----------
    student_cgpa      : The student's raw CGPA value.
    min_required      : The internship's minimum CGPA.
    student_scale     : Scale the student CGPA is on (default 10.0).
    internship_scale  : Scale the internship requirement is on (default 10.0).

    Returns
    -------
    bool — True if eligible, False otherwise.
    """
    # 0.0 means no CGPA requirement — always eligible
    if min_required == 0.0:
        return True

    student_normalized     = normalize_cgpa(student_cgpa, from_scale=student_scale, to_scale=10.0)
    requirement_normalized = normalize_cgpa(min_required, from_scale=internship_scale, to_scale=10.0)

    return student_normalized >= requirement_normalized


# ── Safe input helpers (CLI) ──────────────────────────────────────────────────

def get_float_input(prompt: str, min_val: float = None,
                    max_val: float = None) -> float:
    """
    Prompt the user for a float value and keep asking until a valid one is given.

    Parameters
    ----------
    prompt  : The message to display.
    min_val : Optional minimum allowed value (inclusive).
    max_val : Optional maximum allowed value (inclusive).

    Returns
    -------
    float — the validated user input.
    """
    while True:
        try:
            value = float(input(prompt).strip())
            if min_val is not None and value < min_val:
                print(f"  ⚠  Value must be at least {min_val}. Please try again.")
                continue
            if max_val is not None and value > max_val:
                print(f"  ⚠  Value must be at most {max_val}. Please try again.")
                continue
            return value
        except ValueError:
            print("  ⚠  Invalid input — please enter a numeric value.")


def get_int_input(prompt: str, min_val: int = None,
                  max_val: int = None) -> int:
    """
    Prompt the user for an integer and keep asking until a valid one is given.
    """
    while True:
        try:
            value = int(input(prompt).strip())
            if min_val is not None and value < min_val:
                print(f"  ⚠  Value must be at least {min_val}. Please try again.")
                continue
            if max_val is not None and value > max_val:
                print(f"  ⚠  Value must be at most {max_val}. Please try again.")
                continue
            return value
        except ValueError:
            print("  ⚠  Invalid input — please enter a whole number.")


def get_non_empty_input(prompt: str) -> str:
    """
    Prompt the user for a non-empty string and keep asking until one is given.
    """
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  ⚠  This field cannot be empty. Please try again.")


def get_unique_id(prompt: str, existing_ids) -> str:
    """
    Prompt for an ID and keep asking until one is entered that does not
    already exist in existing_ids.

    Parameters
    ----------
    existing_ids : Any collection that supports `in` (list, set, Series).
    """
    while True:
        value = get_non_empty_input(prompt).strip()
        if value in existing_ids:
            print(f"  ⚠  ID '{value}' already exists. Please choose a different ID.")
        else:
            return value


def get_choice_input(prompt: str, valid_choices) -> str:
    """
    Prompt the user to pick from a list of valid choices.
    """
    choices_str = " / ".join(str(c) for c in valid_choices)
    full_prompt = f"{prompt} [{choices_str}]: "
    while True:
        value = input(full_prompt).strip()
        if value in [str(c) for c in valid_choices]:
            return value
        print(f"  ⚠  Please enter one of: {choices_str}")
