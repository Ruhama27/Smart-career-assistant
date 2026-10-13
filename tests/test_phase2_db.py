"""
test_phase2_db.py — Automated tests for Phase 2 SQLite Database & Data Model.

Tests cover:
  1. Database initialization, tables, views, and foreign key enforcement
  2. Skills normalization and deduplication in `skills` table
  3. Student CRUD operations, unique constraints, and cascade deletion
  4. Internship CRUD operations, unique constraints, and cascade deletion
  5. Ratings CRUD, upsert logic, and foreign key relations
  6. DataFrames returned from SQLite views (v_students, v_internships, v_ratings)
  7. Dataset size verification (at least 20 students and 20 internships seeded)

Run with:  pytest tests/test_phase2_db.py -v
"""

import os
import sys
import tempfile
import sqlite3
import pytest

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.db import (
    init_db,
    get_connection,
    get_or_create_skill,
    add_student,
    get_student_by_id,
    get_all_students,
    update_student,
    delete_student,
    add_internship,
    get_internship_by_id,
    get_all_internships,
    update_internship,
    delete_internship,
    add_rating,
    get_all_ratings,
)
from modules.utils import load_students, load_internships, load_ratings


@pytest.fixture
def temp_db():
    """Create an isolated temporary database for test runs."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Database Schema & Tables
# ═══════════════════════════════════════════════════════════════════════════════

class TestDatabaseSchema:

    def test_schema_creates_all_tables(self, temp_db):
        conn = get_connection(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row["name"] for row in cur.fetchall()}
        conn.close()

        expected = {
            "skills", "students", "student_skills",
            "internships", "internship_skills", "ratings",
            "saved_internships", "applications"
        }
        assert expected.issubset(tables), f"Missing tables: {expected - tables}"

    def test_schema_creates_views(self, temp_db):
        conn = get_connection(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='view';")
        views = {row["name"] for row in cur.fetchall()}
        conn.close()

        expected_views = {"v_students", "v_internships", "v_ratings"}
        assert expected_views.issubset(views), f"Missing views: {expected_views - views}"

    def test_foreign_keys_are_enabled(self, temp_db):
        conn = get_connection(temp_db)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys;")
        status = cur.fetchone()[0]
        conn.close()
        assert status == 1, "Foreign keys must be enabled"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Skills Normalization
# ═══════════════════════════════════════════════════════════════════════════════

class TestSkillsNormalization:

    def test_get_or_create_skill_creates_and_deduplicates(self, temp_db):
        conn = get_connection(temp_db)
        id1 = get_or_create_skill(conn, "Python")
        id2 = get_or_create_skill(conn, "python")  # Case insensitive
        id3 = get_or_create_skill(conn, "  Python  ")  # Stripped
        id4 = get_or_create_skill(conn, "SQL")

        assert id1 == id2 == id3
        assert id1 != id4
        conn.close()

    def test_empty_skill_raises_error(self, temp_db):
        conn = get_connection(temp_db)
        with pytest.raises(ValueError):
            get_or_create_skill(conn, "   ")
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Student CRUD & Normalization
# ═══════════════════════════════════════════════════════════════════════════════

class TestStudentCRUD:

    def test_add_and_retrieve_student(self, temp_db):
        pk = add_student(
            student_id="STEST01",
            name="Abebe Kebede",
            university="Addis Ababa University",
            department="Software Engineering",
            year=4,
            cgpa=3.85,
            cgpa_scale=4.0,
            skills="Python, Django, PostgreSQL",
            db_path=temp_db,
        )
        assert pk > 0

        student = get_student_by_id("STEST01", db_path=temp_db)
        assert student is not None
        assert student["name"] == "Abebe Kebede"
        assert student["university"] == "Addis Ababa University"
        assert student["year"] == 4
        assert student["cgpa"] == 3.85
        assert "Python" in student["skills"]
        assert "Django" in student["skills"]

    def test_duplicate_student_id_raises_error(self, temp_db):
        add_student(student_id="STEST_DUP", name="Student One", db_path=temp_db)
        with pytest.raises(sqlite3.IntegrityError):
            add_student(student_id="STEST_DUP", name="Student Two", db_path=temp_db)

    def test_update_student(self, temp_db):
        add_student(
            student_id="STEST02",
            name="Almaz Bekele",
            cgpa=3.4,
            skills="Java, Spring",
            db_path=temp_db,
        )
        updated = update_student(
            student_id="STEST02",
            updates={"name": "Almaz Bekele Tessema", "cgpa": 3.75},
            skills="Java, Spring Boot, Microservices",
            db_path=temp_db,
        )
        assert updated is True

        student = get_student_by_id("STEST02", db_path=temp_db)
        assert student["name"] == "Almaz Bekele Tessema"
        assert student["cgpa"] == 3.75
        assert "Spring Boot" in student["skills"]
        assert "Microservices" in student["skills"]

    def test_delete_student_cascades_skills(self, temp_db):
        add_student(
            student_id="STEST03",
            name="Tadesse",
            skills="C++, Linux",
            db_path=temp_db,
        )
        deleted = delete_student("STEST03", db_path=temp_db)
        assert deleted is True

        assert get_student_by_id("STEST03", db_path=temp_db) is None

        # Verify normalized student_skills table row was also removed
        conn = get_connection(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM student_skills;")
        count = cur.fetchone()[0]
        conn.close()
        assert count == 0


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Internship CRUD & Normalization
# ═══════════════════════════════════════════════════════════════════════════════

class TestInternshipCRUD:

    def test_add_and_retrieve_internship(self, temp_db):
        pk = add_internship(
            internship_id="ITEST01",
            company="Safaricom Ethiopia",
            role="Cloud Systems Intern",
            domain="Cloud Infrastructure",
            location="Addis Ababa",
            min_cgpa=3.2,
            cgpa_scale=4.0,
            required_skills="Docker, Kubernetes, Go",
            db_path=temp_db,
        )
        assert pk > 0

        internship = get_internship_by_id("ITEST01", db_path=temp_db)
        assert internship is not None
        assert internship["company"] == "Safaricom Ethiopia"
        assert internship["min_cgpa"] == 3.2
        assert "Docker" in internship["required_skills"]

    def test_duplicate_internship_id_raises_error(self, temp_db):
        add_internship(internship_id="ITEST_DUP", company="Co 1", role="R 1", db_path=temp_db)
        with pytest.raises(sqlite3.IntegrityError):
            add_internship(internship_id="ITEST_DUP", company="Co 2", role="R 2", db_path=temp_db)

    def test_update_internship(self, temp_db):
        add_internship(
            internship_id="ITEST02",
            company="Ethio Telecom",
            role="Junior Analyst",
            min_cgpa=3.0,
            required_skills="Excel",
            db_path=temp_db,
        )
        updated = update_internship(
            internship_id="ITEST02",
            updates={"role": "Lead Data Analyst Intern", "min_cgpa": 3.4},
            required_skills="Excel, Power BI, SQL",
            db_path=temp_db,
        )
        assert updated is True

        internship = get_internship_by_id("ITEST02", db_path=temp_db)
        assert internship["role"] == "Lead Data Analyst Intern"
        assert internship["min_cgpa"] == 3.4
        assert "Power BI" in internship["required_skills"]

    def test_delete_internship_cascades(self, temp_db):
        add_internship(
            internship_id="ITEST03",
            company="CBE",
            role="Dev",
            required_skills="Java",
            db_path=temp_db,
        )
        deleted = delete_internship("ITEST03", db_path=temp_db)
        assert deleted is True
        assert get_internship_by_id("ITEST03", db_path=temp_db) is None


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Ratings CRUD & Constraints
# ═══════════════════════════════════════════════════════════════════════════════

class TestRatingsCRUD:

    def test_add_and_update_rating(self, temp_db):
        add_student(student_id="S_R1", name="Rater", db_path=temp_db)
        add_internship(internship_id="I_R1", company="RCo", role="RRole", db_path=temp_db)

        # Initial rating
        res1 = add_rating(student_id="S_R1", internship_id="I_R1", rating=4.0, db_path=temp_db)
        assert res1 is True

        ratings = get_all_ratings(db_path=temp_db)
        assert len(ratings) == 1
        assert ratings[0]["rating"] == 4.0

        # Update rating (upsert on conflict)
        res2 = add_rating(student_id="S_R1", internship_id="I_R1", rating=5.0, db_path=temp_db)
        assert res2 is True

        ratings_updated = get_all_ratings(db_path=temp_db)
        assert len(ratings_updated) == 1
        assert ratings_updated[0]["rating"] == 5.0

    def test_rating_for_nonexistent_fails(self, temp_db):
        res = add_rating(student_id="DOES_NOT_EXIST", internship_id="I_R1", rating=5.0, db_path=temp_db)
        assert res is False


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Seeded Production Database (data/pathfinder.db)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSeededDatabase:

    def test_database_contains_at_least_20_students(self):
        df = load_students()
        assert len(df) >= 20, f"Expected >= 20 students, found {len(df)}"

    def test_database_contains_at_least_20_internships(self):
        df = load_internships()
        assert len(df) >= 20, f"Expected >= 20 internships, found {len(df)}"

    def test_database_contains_ratings(self):
        df = load_ratings()
        assert len(df) >= 20, f"Expected >= 20 ratings, found {len(df)}"

    def test_all_students_have_skills(self):
        df = load_students()
        for _, row in df.iterrows():
            assert isinstance(row["skills"], str)
            assert len(row["skills"]) > 0, f"Student {row['student_id']} missing skills"

    def test_all_internships_have_required_skills(self):
        df = load_internships()
        for _, row in df.iterrows():
            assert isinstance(row["required_skills"], str)
            assert len(row["required_skills"]) > 0, f"Internship {row['internship_id']} missing skills"
