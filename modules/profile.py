"""
profile.py — Student CRUD operations for PathFinder AI (Phase 2 SQL Edition).

Phase 2 changes:
  - All operations now use parameterized SQL queries against SQLite (via database.db).
  - Student skills are stored in a normalized `student_skills` table and `skills` lookup table.
  - Deletions properly cascade through foreign keys.
  - Backwards-compatible view formatting for existing CLI interfaces.
"""

from typing import Optional
from database.db import (
    add_student as db_add_student,
    get_student_by_id,
    get_all_students,
    update_student as db_update_student,
    delete_student as db_delete_student,
)
from modules.utils import (
    get_non_empty_input,
    get_float_input,
    get_int_input,
)


# ── View all students ─────────────────────────────────────────────────────────

def view_students():
    """Retrieve and display all student profiles from the SQLite database."""
    students = get_all_students()

    print("\n========== STUDENT DETAILS ==========\n")

    if not students:
        print("No student records found.")
        return

    for row in students:
        print(f"Student ID : {row['student_id']}")
        print(f"Name       : {row['name']}")
        print(f"University : {row.get('university') or row.get('college', '')}")
        print(f"Department : {row.get('department') or row.get('branch', '')}")
        print(f"Year       : {row['year']}")
        scale_info = f" (scale: {row.get('cgpa_scale', 10.0)})" if row.get("cgpa_scale") else ""
        print(f"CGPA       : {row['cgpa']}{scale_info}")
        print(f"Skills     : {row.get('skills', '')}")
        print(f"Interests  : {row.get('interests', '')}")
        print(f"Career Goal: {row.get('career_goal', '')}")
        print(f"Location   : {row.get('location_pref') or row.get('preferred_location', '')}")
        print("-" * 50)


# ── Search student ────────────────────────────────────────────────────────────

def search_student():
    """Search for a student by student_id in SQLite."""
    student_id = input("Enter Student ID: ").strip()

    student = get_student_by_id(student_id)

    if not student:
        print("\nStudent not found!")
    else:
        print("\nStudent Found:\n")
        print(f"Student ID  : {student['student_id']}")
        print(f"Name        : {student['name']}")
        print(f"Email       : {student.get('email') or 'N/A'}")
        print(f"University  : {student.get('university') or student.get('college', '')}")
        print(f"Department  : {student.get('department') or student.get('branch', '')}")
        print(f"Year        : {student['year']}")
        print(f"CGPA        : {student['cgpa']} (scale: {student.get('cgpa_scale', 10.0)})")
        print(f"Skills      : {student.get('skills', '')}")
        print(f"Interests   : {student.get('interests', '')}")
        print(f"Career Goal : {student.get('career_goal', '')}")
        print(f"Location    : {student.get('location_pref') or student.get('preferred_location', '')}")


# ── Add student ───────────────────────────────────────────────────────────────

def add_student():
    """Prompt user and insert a new student record into SQLite with normalized skills."""
    while True:
        student_id = get_non_empty_input("Student ID: ").strip()
        if get_student_by_id(student_id):
            print(f"  [!] Student ID '{student_id}' already exists in database. Please enter a different ID.")
        else:
            break

    name = get_non_empty_input("Name: ")
    university = get_non_empty_input("University / College: ")
    department = get_non_empty_input("Department / Branch: ")
    year = get_int_input("Year (1-6): ", min_val=1, max_val=6)

    scale_choice = input("CGPA Scale (default 10.0, enter 4 for 4.0 scale): ").strip()
    cgpa_scale = 4.0 if scale_choice == "4" or scale_choice == "4.0" else 10.0
    cgpa = get_float_input(f"CGPA (0.0 - {cgpa_scale}): ", min_val=0.0, max_val=cgpa_scale)

    skills = get_non_empty_input("Skills (comma separated): ")
    interests = get_non_empty_input("Interests (comma separated): ")
    career_goal = get_non_empty_input("Career Goal: ")
    location_pref = get_non_empty_input("Preferred Location: ")
    email = input("Email (optional): ").strip() or None

    db_add_student(
        student_id=student_id,
        name=name,
        university=university,
        department=department,
        year=year,
        cgpa=cgpa,
        cgpa_scale=cgpa_scale,
        career_goal=career_goal,
        interests=interests,
        location_pref=location_pref,
        email=email,
        skills=skills,
    )

    print("\nStudent added successfully to SQLite database!")


# ── Update student ────────────────────────────────────────────────────────────

def update_student():
    """Update fields of an existing student in SQLite."""
    student_id = input("Enter Student ID: ").strip()
    student = get_student_by_id(student_id)

    if not student:
        print("Student not found!")
        return

    print("\nLeave blank if you don't want to change a field.\n")

    name = input(f"Name ({student['name']}): ").strip()
    cgpa_input = input(f"CGPA ({student['cgpa']}): ").strip()
    skills_input = input(f"Skills ({student.get('skills', '')}): ").strip()
    career_goal = input(f"Career Goal ({student.get('career_goal', '')}): ").strip()

    updates = {}
    if name:
        updates["name"] = name
    if career_goal:
        updates["career_goal"] = career_goal

    if cgpa_input:
        try:
            val = float(cgpa_input)
            scale = float(student.get("cgpa_scale", 10.0))
            if 0.0 <= val <= scale:
                updates["cgpa"] = val
            else:
                print(f"  [!] CGPA must be between 0.0 and {scale}. Skipping CGPA update.")
        except ValueError:
            print("  [!] Invalid numeric value for CGPA. Skipping CGPA update.")

    skills_to_update = skills_input if skills_input else None

    if updates or skills_to_update is not None:
        db_update_student(student_id, updates, skills=skills_to_update)
        print("\nStudent updated successfully in SQLite database!")
    else:
        print("\nNo changes made.")


# ── Delete student ────────────────────────────────────────────────────────────

def delete_student():
    """Delete a student and cascade relationships from SQLite."""
    student_id = input("Enter Student ID: ").strip()
    student = get_student_by_id(student_id)

    if not student:
        print("Student not found!")
        return

    confirm = input(
        f"Are you sure you want to delete student '{student_id}' ({student['name']})? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Delete cancelled.")
        return

    db_delete_student(student_id)
    print("\nStudent deleted successfully from SQLite database!")
