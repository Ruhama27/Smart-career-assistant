"""
profile.py — Student CRUD operations for PathFinder AI.

Phase 1 changes:
  - All CSV I/O now uses load_students() / save_students() from utils.py
    (data is always reloaded fresh — never stale).
  - All user inputs use safe helpers from utils.py:
      get_non_empty_input, get_float_input, get_unique_id
    so a bad CGPA entry (e.g. typing "eight") no longer crashes the app.
  - CGPA input is validated to the range 0.0 – 10.0.
"""

import pandas as pd
from modules.utils import (
    load_students,
    save_students,
    get_non_empty_input,
    get_float_input,
    get_int_input,
    get_unique_id,
)


# ── View all students ─────────────────────────────────────────────────────────

def view_students():
    students = load_students()

    print("\n========== STUDENT DETAILS ==========\n")

    if students.empty:
        print("No student records found.")
        return

    for _, row in students.iterrows():
        print(f"Student ID : {row['student_id']}")
        print(f"Name       : {row['name']}")
        print(f"College    : {row['college']}")
        print(f"Branch     : {row['branch']}")
        print(f"Year       : {row['year']}")
        print(f"CGPA       : {row['cgpa']}")
        print(f"Skills     : {row['skills']}")
        print(f"Interests  : {row['interests']}")
        print(f"Career Goal: {row['career_goal']}")
        print(f"Location   : {row['preferred_location']}")
        print("-" * 50)


# ── Search student ────────────────────────────────────────────────────────────

def search_student():
    students = load_students()

    student_id = input("Enter Student ID: ").strip()

    student = students[students["student_id"] == student_id]

    if student.empty:
        print("\nStudent not found!")
    else:
        print("\nStudent Found:\n")
        print(student.to_string(index=False))


# ── Add student ───────────────────────────────────────────────────────────────

def add_student():
    students = load_students()

    # Validate unique ID
    student_id = get_unique_id("Student ID: ", students["student_id"].values)

    new_student = {
        "student_id":         student_id,
        "name":               get_non_empty_input("Name: "),
        "college":            get_non_empty_input("College: "),
        "branch":             get_non_empty_input("Branch: "),
        "year":               get_int_input("Year (1–6): ", min_val=1, max_val=6),
        # Phase 1 fix: safe float input prevents crash on bad CGPA entry
        "cgpa":               get_float_input("CGPA (0.0 – 10.0): ", min_val=0.0, max_val=10.0),
        "skills":             get_non_empty_input("Skills (comma separated): "),
        "interests":          get_non_empty_input("Interests (comma separated): "),
        "career_goal":        get_non_empty_input("Career Goal: "),
        "preferred_location": get_non_empty_input("Preferred Location: "),
    }

    students = pd.concat(
        [students, pd.DataFrame([new_student])],
        ignore_index=True
    )
    save_students(students)

    print("\nStudent added successfully!")


# ── Update student ────────────────────────────────────────────────────────────

def update_student():
    students = load_students()

    student_id = input("Enter Student ID: ").strip()
    index      = students[students["student_id"] == student_id].index

    if len(index) == 0:
        print("Student not found!")
        return

    index = index[0]

    print("\nLeave blank if you don't want to change a field.\n")

    name   = input(f"Name ({students.at[index, 'name']}): ").strip()
    # Phase 1 fix: safe CGPA update — empty string = keep old value
    cgpa_input = input(f"CGPA ({students.at[index, 'cgpa']}): ").strip()
    skills = input(f"Skills ({students.at[index, 'skills']}): ").strip()

    if name:
        students.at[index, "name"] = name

    if cgpa_input:
        try:
            cgpa = float(cgpa_input)
            if 0.0 <= cgpa <= 10.0:
                students.at[index, "cgpa"] = cgpa
            else:
                print("  ⚠  CGPA must be between 0.0 and 10.0. Skipping update.")
        except ValueError:
            print("  ⚠  Invalid CGPA value entered. Skipping CGPA update.")

    if skills:
        students.at[index, "skills"] = skills

    save_students(students)

    print("\nStudent updated successfully!")


# ── Delete student ────────────────────────────────────────────────────────────

def delete_student():
    students = load_students()

    student_id = input("Enter Student ID: ").strip()

    if student_id not in students["student_id"].values:
        print("Student not found!")
        return

    confirm = input(
        f"Are you sure you want to delete student '{student_id}'? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Delete cancelled.")
        return

    students = students[students["student_id"] != student_id]
    save_students(students)

    print("\nStudent deleted successfully!")
