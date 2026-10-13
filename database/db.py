"""
db.py — Database management & parameterized CRUD operations for PathFinder AI.

Provides:
  - SQLite connection factory with foreign key enforcement
  - Database schema initialization
  - Normalized skill management (single source of truth in `skills` table)
  - Parameterized CRUD for students, internships, and ratings with robust connection management
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join("data", "pathfinder.db")
SCHEMA_FILE     = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Create and return a configured SQLite connection.
    Enforces foreign keys and returns rows as sqlite3.Row objects.
    """
    path = db_path or DEFAULT_DB_PATH
    if path != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the database schema from database/schema.sql."""
    conn = get_connection(db_path)
    try:
        with conn:
            with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
    finally:
        conn.close()


def ensure_db_exists(db_path: Optional[str] = None) -> None:
    """Ensure that the database file and schema exist; create if missing."""
    path = db_path or DEFAULT_DB_PATH
    if path == ":memory:" or not os.path.exists(path) or os.path.getsize(path) == 0:
        init_db(path)


# ── Skills helpers ─────────────────────────────────────────────────────────────

def get_or_create_skill(conn: sqlite3.Connection, skill_name: str) -> int:
    """
    Return the skill ID for a given skill name, creating it if it doesn't exist.
    Skill names are normalized (stripped of whitespace).
    """
    clean_name = skill_name.strip()
    if not clean_name:
        raise ValueError("Skill name cannot be empty.")

    cur = conn.cursor()
    cur.execute("SELECT id FROM skills WHERE name = ? COLLATE NOCASE;", (clean_name,))
    row = cur.fetchone()
    if row:
        return row["id"]

    cur.execute("INSERT INTO skills (name) VALUES (?);", (clean_name,))
    return cur.lastrowid


def parse_skills_input(skills: Any) -> List[str]:
    """Parse comma-separated string or iterable of skills into clean list."""
    if not skills:
        return []
    if isinstance(skills, str):
        parts = [s.strip() for s in skills.split(",") if s.strip()]
        return parts
    return [str(s).strip() for s in skills if str(s).strip()]


# ── Student CRUD ───────────────────────────────────────────────────────────────

def add_student(
    student_id: str,
    name: str,
    university: str = "",
    department: str = "",
    year: int = 1,
    cgpa: float = 0.0,
    cgpa_scale: float = 10.0,
    career_goal: str = "",
    interests: str = "",
    location_pref: str = "",
    email: Optional[str] = None,
    skills: Any = None,
    db_path: Optional[str] = None,
) -> int:
    """
    Insert a student and their associated skills into the database.
    Returns the student's primary key id.
    """
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO students (
                    student_id, name, email, university, department,
                    year, cgpa, cgpa_scale, career_goal, interests, location_pref
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    student_id.strip(),
                    name.strip(),
                    email.strip() if email else None,
                    university.strip(),
                    department.strip(),
                    int(year),
                    float(cgpa),
                    float(cgpa_scale),
                    career_goal.strip(),
                    interests.strip(),
                    location_pref.strip(),
                ),
            )
            student_pk = cur.lastrowid

            # Insert skills into normalized student_skills table
            skill_names = parse_skills_input(skills)
            for s_name in skill_names:
                skill_id = get_or_create_skill(conn, s_name)
                cur.execute(
                    """
                    INSERT OR IGNORE INTO student_skills (student_id, skill_id)
                    VALUES (?, ?);
                    """,
                    (student_pk, skill_id),
                )
        return student_pk
    finally:
        conn.close()


def get_student_by_id(student_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a student by student_id from v_students view."""
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM v_students WHERE student_id = ?;", (student_id.strip(),))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_students(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all students from v_students view."""
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM v_students ORDER BY id ASC;")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def update_student(
    student_id: str,
    updates: Dict[str, Any],
    skills: Any = None,
    db_path: Optional[str] = None,
) -> bool:
    """
    Update specified fields of a student.
    If skills is provided, updates the normalized student_skills relationships.
    """
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM students WHERE student_id = ?;", (student_id.strip(),))
        row = cur.fetchone()
        if not row:
            return False
        student_pk = row["id"]

        with conn:
            # Map legacy aliases
            mapped_updates = {}
            for k, v in updates.items():
                if k == "college":
                    mapped_updates["university"] = v
                elif k == "branch":
                    mapped_updates["department"] = v
                elif k == "preferred_location":
                    mapped_updates["location_pref"] = v
                elif k in (
                    "name", "email", "university", "department", "year",
                    "cgpa", "cgpa_scale", "career_goal", "interests", "location_pref"
                ):
                    mapped_updates[k] = v

            if mapped_updates:
                set_clauses = [f"{col} = ?" for col in mapped_updates.keys()]
                values = list(mapped_updates.values()) + [student_pk]
                cur.execute(f"UPDATE students SET {', '.join(set_clauses)} WHERE id = ?;", values)

            if skills is not None:
                cur.execute("DELETE FROM student_skills WHERE student_id = ?;", (student_pk,))
                for s_name in parse_skills_input(skills):
                    skill_id = get_or_create_skill(conn, s_name)
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO student_skills (student_id, skill_id)
                        VALUES (?, ?);
                        """,
                        (student_pk, skill_id),
                    )
        return True
    finally:
        conn.close()


def delete_student(student_id: str, db_path: Optional[str] = None) -> bool:
    """Delete a student by student_id. Cascades to student_skills, ratings, etc."""
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM students WHERE student_id = ?;", (student_id.strip(),))
            return cur.rowcount > 0
    finally:
        conn.close()


# ── Internship CRUD ───────────────────────────────────────────────────────────

def add_internship(
    internship_id: str,
    company: str,
    role: str,
    domain: str = "",
    location: str = "",
    min_cgpa: float = 0.0,
    cgpa_scale: float = 10.0,
    duration: str = "",
    is_remote: bool = False,
    is_paid: Optional[bool] = None,
    deadline: Optional[str] = None,
    source_url: Optional[str] = None,
    verified_at: Optional[str] = None,
    is_active: bool = True,
    required_skills: Any = None,
    db_path: Optional[str] = None,
) -> int:
    """
    Insert an internship and its required skills into the database.
    Returns the internship's primary key id.
    """
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO internships (
                    internship_id, company, role, domain, location,
                    is_remote, is_paid, min_cgpa, cgpa_scale, duration,
                    deadline, source_url, verified_at, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    internship_id.strip(),
                    company.strip(),
                    role.strip(),
                    domain.strip(),
                    location.strip(),
                    bool(is_remote or (location.strip().lower() == "remote")),
                    is_paid,
                    float(min_cgpa),
                    float(cgpa_scale),
                    duration.strip(),
                    deadline,
                    source_url,
                    verified_at,
                    bool(is_active),
                ),
            )
            internship_pk = cur.lastrowid

            # Insert required skills into normalized internship_skills table
            skill_names = parse_skills_input(required_skills)
            for s_name in skill_names:
                skill_id = get_or_create_skill(conn, s_name)
                cur.execute(
                    """
                    INSERT OR IGNORE INTO internship_skills (internship_id, skill_id)
                    VALUES (?, ?);
                    """,
                    (internship_pk, skill_id),
                )
        return internship_pk
    finally:
        conn.close()


def get_internship_by_id(internship_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve an internship by internship_id from v_internships view."""
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM v_internships WHERE internship_id = ?;", (internship_id.strip(),))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_internships(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all internships from v_internships view."""
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM v_internships ORDER BY id ASC;")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def update_internship(
    internship_id: str,
    updates: Dict[str, Any],
    required_skills: Any = None,
    db_path: Optional[str] = None,
) -> bool:
    """Update specified fields of an internship and optionally its skills."""
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM internships WHERE internship_id = ?;", (internship_id.strip(),))
        row = cur.fetchone()
        if not row:
            return False
        internship_pk = row["id"]

        with conn:
            allowed_cols = (
                "company", "role", "domain", "location", "is_remote", "is_paid",
                "min_cgpa", "cgpa_scale", "duration", "deadline", "source_url",
                "verified_at", "is_active"
            )
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_cols}

            if filtered_updates:
                set_clauses = [f"{col} = ?" for col in filtered_updates.keys()]
                values = list(filtered_updates.values()) + [internship_pk]
                cur.execute(f"UPDATE internships SET {', '.join(set_clauses)} WHERE id = ?;", values)

            if required_skills is not None:
                cur.execute("DELETE FROM internship_skills WHERE internship_id = ?;", (internship_pk,))
                for s_name in parse_skills_input(required_skills):
                    skill_id = get_or_create_skill(conn, s_name)
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO internship_skills (internship_id, skill_id)
                        VALUES (?, ?);
                        """,
                        (internship_pk, skill_id),
                    )
        return True
    finally:
        conn.close()


def delete_internship(internship_id: str, db_path: Optional[str] = None) -> bool:
    """Delete an internship by internship_id. Cascades to skills and ratings."""
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM internships WHERE internship_id = ?;", (internship_id.strip(),))
            return cur.rowcount > 0
    finally:
        conn.close()


# ── Ratings CRUD ──────────────────────────────────────────────────────────────

def add_rating(
    student_id: str,
    internship_id: str,
    rating: float,
    db_path: Optional[str] = None,
) -> bool:
    """Insert or update a student rating for an internship."""
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM students WHERE student_id = ?;", (student_id.strip(),))
        s_row = cur.fetchone()
        cur.execute("SELECT id FROM internships WHERE internship_id = ?;", (internship_id.strip(),))
        i_row = cur.fetchone()

        if not s_row or not i_row:
            return False

        with conn:
            cur.execute(
                """
                INSERT INTO ratings (student_id, internship_id, rating)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id, internship_id) DO UPDATE SET rating = excluded.rating;
                """,
                (s_row["id"], i_row["id"], float(rating)),
            )
        return True
    finally:
        conn.close()


def get_all_ratings(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all ratings from v_ratings view."""
    ensure_db_exists(db_path)
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM v_ratings ORDER BY id ASC;")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
