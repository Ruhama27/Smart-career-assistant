"""
utils.py — Shared helper functions for PathFinder AI.

Provides:
  - Safe numeric and text input with validation
  - CGPA normalization across different scales (e.g., 4.0 and 10.0)
  - Data loading helpers backed by SQLite (using pd.read_sql_query)
"""

import os
import sqlite3
import pandas as pd
from typing import Optional, List, Any

from database.db import (
    get_connection,
    ensure_db_exists,
    DEFAULT_DB_PATH,
)

# ── File paths ────────────────────────────────────────────────────────────────
STUDENTS_FILE    = os.path.join("data", "students.csv")
INTERNSHIPS_FILE = os.path.join("data", "internships.csv")
RATINGS_FILE     = os.path.join("data", "ratings.csv")


# ── Data loaders (backed by SQLite for structured, queryable data) ────────────

def load_students(db_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load and return the students DataFrame fresh from SQLite database view (v_students).
    Falls back to CSV if database is not yet initialized.
    """
    try:
        ensure_db_exists(db_path)
        conn = get_connection(db_path)
        df = pd.read_sql_query("SELECT * FROM v_students;", conn)
        conn.close()
        return df
    except Exception:
        if os.path.exists(STUDENTS_FILE):
            return pd.read_csv(STUDENTS_FILE)
        raise


def load_internships(db_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load and return the internships DataFrame fresh from SQLite database view (v_internships).
    Falls back to CSV if database is not yet initialized.
    """
    try:
        ensure_db_exists(db_path)
        conn = get_connection(db_path)
        df = pd.read_sql_query("SELECT * FROM v_internships;", conn)
        conn.close()
        return df
    except Exception:
        if os.path.exists(INTERNSHIPS_FILE):
            return pd.read_csv(INTERNSHIPS_FILE)
        raise


def load_ratings(db_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load and return the ratings DataFrame fresh from SQLite database view (v_ratings).
    Falls back to CSV if database is not yet initialized.
    """
    try:
        ensure_db_exists(db_path)
        conn = get_connection(db_path)
        df = pd.read_sql_query("SELECT * FROM v_ratings;", conn)
        conn.close()
        return df
    except Exception:
        if os.path.exists(RATINGS_FILE):
            return pd.read_csv(RATINGS_FILE)
        raise


def save_students(df: pd.DataFrame) -> None:
    """
    Persist the students DataFrame to CSV backup.
    For primary persistent storage, use database.db.add_student or update_student.
    """
    os.makedirs(os.path.dirname(STUDENTS_FILE), exist_ok=True)
    df.to_csv(STUDENTS_FILE, index=False)


def save_internships(df: pd.DataFrame) -> None:
    """
    Persist the internships DataFrame to CSV backup.
    For primary persistent storage, use database.db.add_internship or update_internship.
    """
    os.makedirs(os.path.dirname(INTERNSHIPS_FILE), exist_ok=True)
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
    """
    if min_required == 0.0:
        return True

    student_normalized     = normalize_cgpa(student_cgpa, from_scale=student_scale, to_scale=10.0)
    requirement_normalized = normalize_cgpa(min_required, from_scale=internship_scale, to_scale=10.0)

    return student_normalized >= requirement_normalized


# ── Safe input helpers (CLI) ──────────────────────────────────────────────────

def get_float_input(prompt: str, min_val: Optional[float] = None,
                    max_val: Optional[float] = None) -> float:
    """Prompt the user for a float value and keep asking until a valid one is given."""
    while True:
        try:
            value = float(input(prompt).strip())
            if min_val is not None and value < min_val:
                print(f"  [!] Value must be at least {min_val}. Please try again.")
                continue
            if max_val is not None and value > max_val:
                print(f"  [!] Value must be at most {max_val}. Please try again.")
                continue
            return value
        except ValueError:
            print("  [!] Invalid input - please enter a numeric value.")


def get_int_input(prompt: str, min_val: Optional[int] = None,
                  max_val: Optional[int] = None) -> int:
    """Prompt the user for an integer and keep asking until a valid one is given."""
    while True:
        try:
            value = int(input(prompt).strip())
            if min_val is not None and value < min_val:
                print(f"  [!] Value must be at least {min_val}. Please try again.")
                continue
            if max_val is not None and value > max_val:
                print(f"  [!] Value must be at most {max_val}. Please try again.")
                continue
            return value
        except ValueError:
            print("  [!] Invalid input - please enter a whole number.")


def get_non_empty_input(prompt: str) -> str:
    """Prompt the user for a non-empty string and keep asking until one is given."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  [!] This field cannot be empty. Please try again.")


def get_unique_id(prompt: str, existing_ids: Any) -> str:
    """Prompt for an ID and keep asking until one is entered that is unique."""
    while True:
        value = get_non_empty_input(prompt).strip()
        if value in existing_ids:
            print(f"  [!] ID '{value}' already exists. Please choose a different ID.")
        else:
            return value


def get_choice_input(prompt: str, valid_choices: Any) -> str:
    """Prompt the user to pick from a list of valid choices."""
    choices_str = " / ".join(str(c) for c in valid_choices)
    full_prompt = f"{prompt} [{choices_str}]: "
    while True:
        value = input(full_prompt).strip()
        if value in [str(c) for c in valid_choices]:
            return value
        print(f"  [!] Please enter one of: {choices_str}")
