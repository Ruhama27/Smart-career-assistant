"""
main.py — CLI entry point for PathFinder AI.

Phase 1 changes:
  - Uses refactored modules with safe input helpers and CGPA eligibility filter.
  - Invalid menu choices no longer crash the loop.
  - Evaluation section clearly labelled as using synthetic test data.
"""

from modules.profile import *
from modules.internship import *
from modules.content_based import recommend_internships
from modules.collaborative import collaborative_recommendation
from modules.hybrid import hybrid_recommendation
from modules.evaluation import precision, recall, rmse

while True:

    print("\n" + "=" * 55)
    print("      PATHFINDER AI — Internship Recommendation")
    print("=" * 55)

    print("  1.  View Students")
    print("  2.  Search Student")
    print("  3.  Add Student")
    print("  4.  Update Student")
    print("  5.  Delete Student")
    print("  6.  View Internships")
    print("  7.  Search Internship")
    print("  8.  Add Internship")
    print("  9.  Update Internship")
    print("  10. Delete Internship")
    print("  11. Recommend Internships (Content-Based)")
    print("  12. Recommend Internships (Collaborative)")
    print("  13. Recommend Internships (Hybrid)")
    print("  14. Evaluate Recommendation System")
    print("  15. Exit")

    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        view_students()

    elif choice == "2":
        search_student()

    elif choice == "3":
        add_student()

    elif choice == "4":
        update_student()

    elif choice == "5":
        delete_student()

    elif choice == "6":
        view_internships()

    elif choice == "7":
        search_internship()

    elif choice == "8":
        add_internship()

    elif choice == "9":
        update_internship()

    elif choice == "10":
        delete_internship()

    elif choice == "11":
        student_id = input("Enter Student ID: ").strip()
        recommend_internships(student_id)

    elif choice == "12":
        student_id = input("Enter Student ID: ").strip()
        collaborative_recommendation(student_id)

    elif choice == "13":
        student_id = input("Enter Student ID: ").strip()
        hybrid_recommendation(student_id)

    elif choice == "14":
        # NOTE: These are synthetic test values for demonstration only.
        # Replace with real student data for a meaningful evaluation.
        recommended = ["I001", "I002", "I003", "I004"]
        relevant    = ["I001", "I003", "I005"]

        actual    = [5, 4, 3, 5]
        predicted = [4.8, 4.2, 2.7, 4.9]

        print("\n========== Evaluation (Synthetic Test Data) ==========\n")
        print("Precision :", round(precision(recommended, relevant), 2))
        print("Recall    :", round(recall(recommended, relevant), 2))
        print("RMSE      :", round(rmse(actual, predicted), 2))
        print("\n  ⚠  Results above use synthetic data — not real student ratings.")

    elif choice == "15":
        print("\nThank you for using PathFinder AI!")
        break

    else:
        print("\n  ⚠  Invalid choice. Please enter a number between 1 and 15.")