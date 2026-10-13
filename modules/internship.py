"""
internship.py — Internship CRUD operations for PathFinder AI (Phase 2 SQL Edition).

Phase 2 changes:
  - All operations now use parameterized SQL queries against SQLite (via database.db).
  - Internship skills are stored in a normalized `internship_skills` table and `skills` lookup.
  - Foreign key constraints enforced on deletion.
  - Clean display formatting for CLI usage.
"""

from typing import Optional
from database.db import (
    add_internship as db_add_internship,
    get_internship_by_id,
    get_all_internships,
    update_internship as db_update_internship,
    delete_internship as db_delete_internship,
)
from modules.utils import (
    get_non_empty_input,
    get_float_input,
)


# ── View all internships ──────────────────────────────────────────────────────

def view_internships():
    """Retrieve and display all internship postings from the SQLite database."""
    internships = get_all_internships()

    print("\n========== INTERNSHIP DATABASE ==========\n")

    if not internships:
        print("No internship records found.")
        return

    for row in internships:
        print(f"Internship ID : {row['internship_id']}")
        print(f"Company       : {row['company']}")
        print(f"Role          : {row['role']}")
        print(f"Skills        : {row.get('required_skills', '')}")
        print(f"Domain        : {row.get('domain', '')}")
        min_cgpa = row.get("min_cgpa", 0.0)
        scale = row.get("cgpa_scale", 10.0)
        min_cgpa_display = "No requirement" if min_cgpa == 0.0 else f"{min_cgpa} (scale: {scale})"
        print(f"Minimum CGPA  : {min_cgpa_display}")
        print(f"Location      : {row.get('location', '')}")
        print(f"Duration      : {row.get('duration', '')}")
        if row.get("is_paid") is not None:
            print(f"Paid          : {'Yes' if row['is_paid'] else 'No'}")
        print("-" * 55)


# ── Search internship ─────────────────────────────────────────────────────────

def search_internship():
    """Search for an internship by internship_id in SQLite."""
    internship_id = input("Enter Internship ID: ").strip()

    internship = get_internship_by_id(internship_id)

    if not internship:
        print("\nInternship not found!")
    else:
        print("\nInternship Found:\n")
        print(f"Internship ID : {internship['internship_id']}")
        print(f"Company       : {internship['company']}")
        print(f"Role          : {internship['role']}")
        print(f"Skills        : {internship.get('required_skills', '')}")
        print(f"Domain        : {internship.get('domain', '')}")
        min_cgpa = internship.get("min_cgpa", 0.0)
        scale = internship.get("cgpa_scale", 10.0)
        min_cgpa_display = "No requirement" if min_cgpa == 0.0 else f"{min_cgpa} (scale: {scale})"
        print(f"Minimum CGPA  : {min_cgpa_display}")
        print(f"Location      : {internship.get('location', '')}")
        print(f"Duration      : {internship.get('duration', '')}")


# ── Add internship ────────────────────────────────────────────────────────────

def add_internship():
    """Prompt user and insert a new internship posting into SQLite."""
    while True:
        internship_id = get_non_empty_input("Internship ID: ").strip()
        if get_internship_by_id(internship_id):
            print(f"  [!] Internship ID '{internship_id}' already exists. Please choose a different ID.")
        else:
            break

    company = get_non_empty_input("Company: ")
    role = get_non_empty_input("Role: ")
    required_skills = get_non_empty_input("Required Skills (comma separated): ")
    domain = get_non_empty_input("Domain: ")

    scale_choice = input("CGPA Scale for requirement (default 10.0, enter 4 for 4.0 scale): ").strip()
    cgpa_scale = 4.0 if scale_choice == "4" or scale_choice == "4.0" else 10.0
    print("  (Enter 0.0 for minimum CGPA if there is no minimum requirement)")
    min_cgpa = get_float_input(
        f"Minimum CGPA (0.0 - {cgpa_scale}, enter 0 for no requirement): ",
        min_val=0.0,
        max_val=cgpa_scale,
    )

    location = get_non_empty_input("Location: ")
    duration = get_non_empty_input("Duration: ")
    is_remote = location.strip().lower() == "remote"

    db_add_internship(
        internship_id=internship_id,
        company=company,
        role=role,
        domain=domain,
        location=location,
        min_cgpa=min_cgpa,
        cgpa_scale=cgpa_scale,
        duration=duration,
        is_remote=is_remote,
        is_paid=True,
        required_skills=required_skills,
    )

    print("\nInternship Added Successfully to SQLite database!")


# ── Update internship ─────────────────────────────────────────────────────────

def update_internship():
    """Update fields of an existing internship posting in SQLite."""
    internship_id = input("Enter Internship ID: ").strip()
    internship = get_internship_by_id(internship_id)

    if not internship:
        print("Internship not found!")
        return

    print("\nLeave blank if you don't want to change a field.\n")

    company = input(f"Company ({internship['company']}): ").strip()
    role = input(f"Role ({internship['role']}): ").strip()
    skills_input = input(f"Required Skills ({internship.get('required_skills', '')}): ").strip()
    cgpa_input = input(f"Min CGPA ({internship['min_cgpa']}, 0=no requirement): ").strip()
    location = input(f"Location ({internship.get('location', '')}): ").strip()

    updates = {}
    if company:
        updates["company"] = company
    if role:
        updates["role"] = role
    if location:
        updates["location"] = location
        updates["is_remote"] = location.strip().lower() == "remote"

    if cgpa_input:
        try:
            val = float(cgpa_input)
            scale = float(internship.get("cgpa_scale", 10.0))
            if 0.0 <= val <= scale:
                updates["min_cgpa"] = val
            else:
                print(f"  [!] CGPA must be between 0.0 and {scale}. Skipping update.")
        except ValueError:
            print("  [!] Invalid numeric CGPA entered. Skipping update.")

    skills_to_update = skills_input if skills_input else None

    if updates or skills_to_update is not None:
        db_update_internship(internship_id, updates, required_skills=skills_to_update)
        print("\nInternship Updated Successfully in SQLite database!")
    else:
        print("\nNo changes made.")


# ── Delete internship ─────────────────────────────────────────────────────────

def delete_internship():
    """Delete an internship posting and cascade relationships in SQLite."""
    internship_id = input("Enter Internship ID: ").strip()
    internship = get_internship_by_id(internship_id)

    if not internship:
        print("Internship not found!")
        return

    confirm = input(
        f"Are you sure you want to delete internship '{internship_id}' ({internship['company']} - {internship['role']})? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Delete cancelled.")
        return

    db_delete_internship(internship_id)
    print("\nInternship Deleted Successfully from SQLite database!")
