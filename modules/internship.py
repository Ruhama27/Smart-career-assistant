"""
internship.py — Internship CRUD operations for PathFinder AI.

Phase 1 changes:
  - All CSV I/O now uses load_internships() / save_internships() from utils.py.
  - All user inputs use safe helpers from utils.py.
  - min_cgpa input is validated to 0.0–10.0 (0.0 means "no requirement").
  - Confirmation prompt added before deleting an internship.
"""

import pandas as pd
from modules.utils import (
    load_internships,
    save_internships,
    get_non_empty_input,
    get_float_input,
    get_unique_id,
)


# ── View all internships ──────────────────────────────────────────────────────

def view_internships():
    internships = load_internships()

    print("\n========== INTERNSHIP DATABASE ==========\n")

    if internships.empty:
        print("No internship records found.")
        return

    for _, row in internships.iterrows():
        print(f"Internship ID : {row['internship_id']}")
        print(f"Company       : {row['company']}")
        print(f"Role          : {row['role']}")
        print(f"Skills        : {row['required_skills']}")
        print(f"Domain        : {row['domain']}")
        # Phase 1 fix: display "None" clearly when min_cgpa is 0
        min_cgpa_display = (
            "No requirement" if row["min_cgpa"] == 0.0
            else str(row["min_cgpa"])
        )
        print(f"Minimum CGPA  : {min_cgpa_display}")
        print(f"Location      : {row['location']}")
        print(f"Duration      : {row['duration']}")
        print("-" * 55)


# ── Search internship ─────────────────────────────────────────────────────────

def search_internship():
    internships = load_internships()

    internship_id = input("Enter Internship ID: ").strip()

    internship = internships[internships["internship_id"] == internship_id]

    if internship.empty:
        print("\nInternship not found!")
    else:
        print("\nInternship Found\n")
        print(internship.to_string(index=False))


# ── Add internship ────────────────────────────────────────────────────────────

def add_internship():
    internships = load_internships()

    internship_id = get_unique_id("Internship ID: ", internships["internship_id"].values)

    # Phase 1 fix: min_cgpa uses safe float input; 0.0 = no requirement
    print("  (Enter 0.0 for minimum CGPA if there is no CGPA requirement)")
    new_data = {
        "internship_id":  internship_id,
        "company":        get_non_empty_input("Company: "),
        "role":           get_non_empty_input("Role: "),
        "required_skills":get_non_empty_input("Required Skills (comma separated): "),
        "domain":         get_non_empty_input("Domain: "),
        "min_cgpa":       get_float_input("Minimum CGPA (0.0 – 10.0, enter 0 for no requirement): ",
                                          min_val=0.0, max_val=10.0),
        "location":       get_non_empty_input("Location: "),
        "duration":       get_non_empty_input("Duration: "),
    }

    internships = pd.concat(
        [internships, pd.DataFrame([new_data])],
        ignore_index=True
    )
    save_internships(internships)

    print("\nInternship Added Successfully!")


# ── Update internship ─────────────────────────────────────────────────────────

def update_internship():
    internships = load_internships()

    internship_id = input("Enter Internship ID: ").strip()
    index = internships[internships["internship_id"] == internship_id].index

    if len(index) == 0:
        print("Internship not found!")
        return

    index = index[0]

    print("\nLeave blank if you don't want to change a field.\n")

    company = input(f"Company ({internships.at[index, 'company']}): ").strip()
    role    = input(f"Role ({internships.at[index, 'role']}): ").strip()

    # Phase 1 fix: safe CGPA update on update too
    cgpa_input = input(
        f"Min CGPA ({internships.at[index, 'min_cgpa']}, 0=no requirement): "
    ).strip()

    if company:
        internships.at[index, "company"] = company

    if role:
        internships.at[index, "role"] = role

    if cgpa_input:
        try:
            cgpa = float(cgpa_input)
            if 0.0 <= cgpa <= 10.0:
                internships.at[index, "min_cgpa"] = cgpa
            else:
                print("  ⚠  CGPA must be between 0.0 and 10.0. Skipping update.")
        except ValueError:
            print("  ⚠  Invalid CGPA value entered. Skipping CGPA update.")

    save_internships(internships)

    print("\nInternship Updated Successfully!")


# ── Delete internship ─────────────────────────────────────────────────────────

def delete_internship():
    internships = load_internships()

    internship_id = input("Enter Internship ID: ").strip()

    if internship_id not in internships["internship_id"].values:
        print("Internship not found!")
        return

    confirm = input(
        f"Are you sure you want to delete internship '{internship_id}'? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Delete cancelled.")
        return

    internships = internships[internships["internship_id"] != internship_id]
    save_internships(internships)

    print("\nInternship Deleted Successfully!")
