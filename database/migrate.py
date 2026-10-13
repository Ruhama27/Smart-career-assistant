"""
migrate.py — One-time CSV migration and dataset expansion for PathFinder AI.

Tasks:
  1. Initialize SQLite database schema from database/schema.sql
  2. Populate `skills` table uniquely from all skill occurrences
  3. Migrate existing students, internships, and ratings from CSV
  4. Expand dataset with 12 additional students and 12 additional internships
     (including Ethiopian universities like AAU, DBU, ASTU and global/local companies)
  5. Add realistic collaborative filtering ratings for new pairs
  6. Archive original CSV files into data/backup_csv/
"""

import os
import sys
import shutil
import sqlite3
import pandas as pd
from typing import Optional

# Ensure UTF-8 output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database.db import (
    DEFAULT_DB_PATH,
    init_db,
    add_student,
    add_internship,
    add_rating,
    get_connection,
)

STUDENTS_CSV    = os.path.join("data", "students.csv")
INTERNSHIPS_CSV = os.path.join("data", "internships.csv")
RATINGS_CSV     = os.path.join("data", "ratings.csv")
BACKUP_DIR      = os.path.join("data", "backup_csv")


# ── Additional students (aiming for 22 total >= 20) ───────────────────────────
ADDITIONAL_STUDENTS = [
    {
        "student_id": "S011",
        "name": "Ruhama Nigusu",
        "university": "Debre Berhan University",
        "department": "Software Engineering",
        "year": 4,
        "cgpa": 3.82,
        "cgpa_scale": 4.0,
        "career_goal": "Full Stack & AI Engineer",
        "interests": "Machine Learning, Web Platforms, Cloud Computing",
        "location_pref": "Addis Ababa",
        "skills": "Python, JavaScript, React, FastAPI, SQL, Machine Learning",
        "email": "ruhama@dbu.edu.et",
    },
    {
        "student_id": "S012",
        "name": "Bereket Tadesse",
        "university": "Addis Ababa University",
        "department": "Computer Science",
        "year": 3,
        "cgpa": 3.65,
        "cgpa_scale": 4.0,
        "career_goal": "Backend Engineer",
        "interests": "Fintech, Microservices, Distributed Systems",
        "location_pref": "Addis Ababa",
        "skills": "Java, Spring Boot, PostgreSQL, Docker, Redis",
        "email": "bereket.t@aau.edu.et",
    },
    {
        "student_id": "S013",
        "name": "Bethlehem Assefa",
        "university": "ASTU",
        "department": "Software Engineering",
        "year": 3,
        "cgpa": 3.75,
        "cgpa_scale": 4.0,
        "career_goal": "Data Scientist",
        "interests": "Big Data, Predictive Modeling, AI",
        "location_pref": "Remote",
        "skills": "Python, Pandas, Scikit-learn, SQL, Power BI",
        "email": "bethlehem@astu.edu.et",
    },
    {
        "student_id": "S014",
        "name": "Yohannes Bekele",
        "university": "Addis Ababa University",
        "department": "Information Technology",
        "year": 4,
        "cgpa": 3.40,
        "cgpa_scale": 4.0,
        "career_goal": "DevOps Engineer",
        "interests": "CI/CD, Cloud Infrastructure, Linux",
        "location_pref": "Addis Ababa",
        "skills": "Linux, Docker, Kubernetes, Python, Git, Go",
        "email": "yohannes.b@aau.edu.et",
    },
    {
        "student_id": "S015",
        "name": "Helina Solomon",
        "university": "Hawassa University",
        "department": "Computer Science",
        "year": 3,
        "cgpa": 3.55,
        "cgpa_scale": 4.0,
        "career_goal": "Mobile App Developer",
        "interests": "Cross-Platform Apps, UX, Mobile Architecture",
        "location_pref": "Remote",
        "skills": "Flutter, Dart, Firebase, REST APIs, Git",
        "email": "helina@hu.edu.et",
    },
    {
        "student_id": "S016",
        "name": "Dawit Haile",
        "university": "Bahir Dar University",
        "department": "Software Engineering",
        "year": 2,
        "cgpa": 3.20,
        "cgpa_scale": 4.0,
        "career_goal": "Frontend Developer",
        "interests": "UI/UX, Modern Web, Responsive Design",
        "location_pref": "Remote",
        "skills": "HTML, CSS, JavaScript, React, Tailwind CSS",
        "email": "dawit.h@bdu.edu.et",
    },
    {
        "student_id": "S017",
        "name": "Meron Getachew",
        "university": "Debre Berhan University",
        "department": "Computer Science",
        "year": 3,
        "cgpa": 3.70,
        "cgpa_scale": 4.0,
        "career_goal": "Machine Learning Engineer",
        "interests": "NLP, Computer Vision, Deep Learning",
        "location_pref": "Remote",
        "skills": "Python, PyTorch, TensorFlow, Scikit-learn, OpenCV",
        "email": "meron.g@dbu.edu.et",
    },
    {
        "student_id": "S018",
        "name": "Abel Worku",
        "university": "Addis Ababa University",
        "department": "Electrical & Computer Engineering",
        "year": 4,
        "cgpa": 3.60,
        "cgpa_scale": 4.0,
        "career_goal": "Embedded & IoT Developer",
        "interests": "Hardware-Software Integration, C++, Edge Computing",
        "location_pref": "Addis Ababa",
        "skills": "C++, C, Python, Linux, RTOS, Git",
        "email": "abel.w@aau.edu.et",
    },
    {
        "student_id": "S019",
        "name": "Sara Mohammed",
        "university": "ASTU",
        "department": "Computer Science",
        "year": 3,
        "cgpa": 3.88,
        "cgpa_scale": 4.0,
        "career_goal": "Cloud Solutions Architect",
        "interests": "Cloud Computing, Scalability, Serverless",
        "location_pref": "Remote",
        "skills": "AWS, Python, Docker, Terraform, SQL",
        "email": "sara.m@astu.edu.et",
    },
    {
        "student_id": "S020",
        "name": "Kirubel Girma",
        "university": "Debre Berhan University",
        "department": "Information Systems",
        "year": 3,
        "cgpa": 3.35,
        "cgpa_scale": 4.0,
        "career_goal": "Business & Data Analyst",
        "interests": "Analytics, Business Intelligence, Strategy",
        "location_pref": "Addis Ababa",
        "skills": "SQL, Excel, Power BI, Python, Tableau",
        "email": "kirubel.g@dbu.edu.et",
    },
    {
        "student_id": "S021",
        "name": "Kavya Patel",
        "university": "DTU",
        "department": "CSE",
        "year": 3,
        "cgpa": 8.70,
        "cgpa_scale": 10.0,
        "career_goal": "Cybersecurity Analyst",
        "interests": "Network Security, Cryptography, Ethical Hacking",
        "location_pref": "Delhi",
        "skills": "Python, Linux, Wireshark, Bash, Cryptography",
        "email": "kavya@dtu.ac.in",
    },
    {
        "student_id": "S022",
        "name": "Vikram Sen",
        "university": "NSUT",
        "department": "IT",
        "year": 4,
        "cgpa": 8.45,
        "cgpa_scale": 10.0,
        "career_goal": "Backend Developer",
        "interests": "APIs, Database Design, Scalable Architectures",
        "location_pref": "Bangalore",
        "skills": "Go, Python, PostgreSQL, Docker, GraphQL",
        "email": "vikram@nsut.ac.in",
    },
]

# ── Additional internships (aiming for 22 total >= 20) ────────────────────────
ADDITIONAL_INTERNSHIPS = [
    {
        "internship_id": "I011",
        "company": "Safaricom Ethiopia",
        "role": "Software Engineering Intern",
        "domain": "Telecommunications & Software",
        "location": "Addis Ababa",
        "min_cgpa": 3.0,
        "cgpa_scale": 4.0,
        "duration": "3 Months",
        "is_remote": False,
        "is_paid": True,
        "required_skills": "Python, Django, PostgreSQL, REST APIs",
    },
    {
        "internship_id": "I012",
        "company": "Ethio Telecom",
        "role": "Data Analytics Intern",
        "domain": "Data Analytics",
        "location": "Addis Ababa",
        "min_cgpa": 3.0,
        "cgpa_scale": 4.0,
        "duration": "4 Months",
        "is_remote": False,
        "is_paid": True,
        "required_skills": "SQL, Python, Power BI, Excel",
    },
    {
        "internship_id": "I013",
        "company": "Commercial Bank of Ethiopia",
        "role": "Fintech Backend Developer",
        "domain": "Fintech & Banking",
        "location": "Addis Ababa",
        "min_cgpa": 3.2,
        "cgpa_scale": 4.0,
        "duration": "6 Months",
        "is_remote": False,
        "is_paid": True,
        "required_skills": "Java, Spring Boot, SQL, Docker",
    },
    {
        "internship_id": "I014",
        "company": "Chapa Financial Technologies",
        "role": "API & Backend Intern",
        "domain": "Payment Systems",
        "location": "Addis Ababa",
        "min_cgpa": 3.2,
        "cgpa_scale": 4.0,
        "duration": "3 Months",
        "is_remote": False,
        "is_paid": True,
        "required_skills": "Python, FastAPI, PostgreSQL, Redis",
    },
    {
        "internship_id": "I015",
        "company": "Gebeya Inc.",
        "role": "Full Stack Engineering Intern",
        "domain": "Software Development",
        "location": "Remote",
        "min_cgpa": 0.0,
        "cgpa_scale": 4.0,
        "duration": "3 Months",
        "is_remote": True,
        "is_paid": True,
        "required_skills": "React, Node.js, JavaScript, MongoDB",
    },
    {
        "internship_id": "I016",
        "company": "Ride (Hybrid Designs)",
        "role": "Mobile Application Intern",
        "domain": "Mobile Development",
        "location": "Addis Ababa",
        "min_cgpa": 2.8,
        "cgpa_scale": 4.0,
        "duration": "3 Months",
        "is_remote": False,
        "is_paid": True,
        "required_skills": "Flutter, Dart, Firebase, REST APIs",
    },
    {
        "internship_id": "I017",
        "company": "Meta",
        "role": "AI Research Intern",
        "domain": "Artificial Intelligence",
        "location": "Remote",
        "min_cgpa": 3.6,
        "cgpa_scale": 4.0,
        "duration": "6 Months",
        "is_remote": True,
        "is_paid": True,
        "required_skills": "Python, PyTorch, Deep Learning, Machine Learning",
    },
    {
        "internship_id": "I018",
        "company": "GitHub",
        "role": "DevOps & Cloud Intern",
        "domain": "Cloud Infrastructure",
        "location": "Remote",
        "min_cgpa": 0.0,
        "cgpa_scale": 4.0,
        "duration": "4 Months",
        "is_remote": True,
        "is_paid": True,
        "required_skills": "Linux, Docker, Kubernetes, Git, Go",
    },
    {
        "internship_id": "I019",
        "company": "Spotify",
        "role": "Machine Learning Engineer Intern",
        "domain": "AI & Recommendation Systems",
        "location": "Remote",
        "min_cgpa": 3.5,
        "cgpa_scale": 4.0,
        "duration": "6 Months",
        "is_remote": True,
        "is_paid": True,
        "required_skills": "Python, Scikit-learn, Machine Learning, SQL",
    },
    {
        "internship_id": "I020",
        "company": "Uber",
        "role": "Distributed Systems Intern",
        "domain": "Backend Systems",
        "location": "Remote",
        "min_cgpa": 3.4,
        "cgpa_scale": 4.0,
        "duration": "4 Months",
        "is_remote": True,
        "is_paid": True,
        "required_skills": "Go, Java, Distributed Systems, Docker",
    },
    {
        "internship_id": "I021",
        "company": "Apple",
        "role": "iOS Development Intern",
        "domain": "Mobile Development",
        "location": "Remote",
        "min_cgpa": 8.0,
        "cgpa_scale": 10.0,
        "duration": "6 Months",
        "is_remote": True,
        "is_paid": True,
        "required_skills": "Swift, iOS, C++, Git",
    },
    {
        "internship_id": "I022",
        "company": "Netflix",
        "role": "Cloud Platform Intern",
        "domain": "Cloud & Infrastructure",
        "location": "Remote",
        "min_cgpa": 8.5,
        "cgpa_scale": 10.0,
        "duration": "6 Months",
        "is_remote": True,
        "is_paid": True,
        "required_skills": "Java, AWS, Docker, Linux, Python",
    },
]

# ── Additional ratings for collaborative filtering ────────────────────────────
ADDITIONAL_RATINGS = [
    ("S011", "I011", 5),
    ("S011", "I014", 5),
    ("S011", "I015", 4),
    ("S012", "I013", 5),
    ("S012", "I014", 4),
    ("S012", "I008", 4),
    ("S013", "I001", 5),
    ("S013", "I012", 5),
    ("S013", "I019", 4),
    ("S014", "I018", 5),
    ("S014", "I020", 4),
    ("S015", "I016", 5),
    ("S015", "I009", 4),
    ("S016", "I003", 5),
    ("S016", "I015", 4),
    ("S017", "I017", 5),
    ("S017", "I002", 5),
    ("S017", "I006", 4),
    ("S018", "I020", 4),
    ("S019", "I018", 5),
    ("S019", "I022", 5),
    ("S020", "I007", 5),
    ("S020", "I012", 5),
    ("S021", "I018", 4),
    ("S022", "I020", 5),
]


def run_migration(db_path: Optional[str] = None) -> None:
    """Run full migration from CSV and seed expanded data."""
    target_db = db_path or DEFAULT_DB_PATH
    print(f"[*] Initializing database at: {target_db}")
    init_db(target_db)

    # 1. Migrate original students CSV
    if os.path.exists(STUDENTS_CSV):
        print(f"[*] Migrating students from {STUDENTS_CSV}...")
        df_students = pd.read_csv(STUDENTS_CSV)
        for _, row in df_students.iterrows():
            add_student(
                student_id=str(row["student_id"]),
                name=str(row["name"]),
                university=str(row.get("college", "")),
                department=str(row.get("branch", "")),
                year=int(row.get("year", 1)),
                cgpa=float(row.get("cgpa", 0.0)),
                cgpa_scale=10.0,
                career_goal=str(row.get("career_goal", "")),
                interests=str(row.get("interests", "")),
                location_pref=str(row.get("preferred_location", "")),
                skills=str(row.get("skills", "")),
                db_path=target_db,
            )
        print(f"    [OK] Migrated {len(df_students)} students from CSV.")

    # 2. Migrate original internships CSV
    if os.path.exists(INTERNSHIPS_CSV):
        print(f"[*] Migrating internships from {INTERNSHIPS_CSV}...")
        df_internships = pd.read_csv(INTERNSHIPS_CSV)
        for _, row in df_internships.iterrows():
            loc = str(row.get("location", ""))
            add_internship(
                internship_id=str(row["internship_id"]),
                company=str(row["company"]),
                role=str(row["role"]),
                domain=str(row.get("domain", "")),
                location=loc,
                min_cgpa=float(row.get("min_cgpa", 0.0)),
                cgpa_scale=10.0,
                duration=str(row.get("duration", "")),
                is_remote=(loc.strip().lower() == "remote"),
                is_paid=True,
                required_skills=str(row.get("required_skills", "")),
                db_path=target_db,
            )
        print(f"    [OK] Migrated {len(df_internships)} internships from CSV.")

    # 3. Migrate original ratings CSV
    if os.path.exists(RATINGS_CSV):
        print(f"[*] Migrating ratings from {RATINGS_CSV}...")
        df_ratings = pd.read_csv(RATINGS_CSV)
        for _, row in df_ratings.iterrows():
            add_rating(
                student_id=str(row["student_id"]),
                internship_id=str(row["internship_id"]),
                rating=float(row["rating"]),
                db_path=target_db,
            )
        print(f"    [OK] Migrated {len(df_ratings)} ratings from CSV.")

    # 4. Seed expanded students (Phase 2 requirement: 20+ records)
    print(f"[*] Adding {len(ADDITIONAL_STUDENTS)} additional student profiles...")
    for s in ADDITIONAL_STUDENTS:
        add_student(
            student_id=s["student_id"],
            name=s["name"],
            university=s["university"],
            department=s["department"],
            year=s["year"],
            cgpa=s["cgpa"],
            cgpa_scale=s["cgpa_scale"],
            career_goal=s["career_goal"],
            interests=s["interests"],
            location_pref=s["location_pref"],
            skills=s["skills"],
            email=s.get("email"),
            db_path=target_db,
        )
    print("    [OK] Additional students inserted.")

    # 5. Seed expanded internships (Phase 2 requirement: 20+ records)
    print(f"[*] Adding {len(ADDITIONAL_INTERNSHIPS)} additional internship listings...")
    for i in ADDITIONAL_INTERNSHIPS:
        add_internship(
            internship_id=i["internship_id"],
            company=i["company"],
            role=i["role"],
            domain=i["domain"],
            location=i["location"],
            min_cgpa=i["min_cgpa"],
            cgpa_scale=i["cgpa_scale"],
            duration=i["duration"],
            is_remote=i["is_remote"],
            is_paid=i["is_paid"],
            required_skills=i["required_skills"],
            db_path=target_db,
        )
    print("    [OK] Additional internships inserted.")

    # 6. Seed expanded collaborative ratings
    print(f"[*] Adding {len(ADDITIONAL_RATINGS)} additional ratings...")
    for sid, iid, r in ADDITIONAL_RATINGS:
        add_rating(student_id=sid, internship_id=iid, rating=r, db_path=target_db)
    print("    [OK] Additional ratings inserted.")

    # 7. Backup original CSV files
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for src in (STUDENTS_CSV, INTERNSHIPS_CSV, RATINGS_CSV):
        if os.path.exists(src):
            dst = os.path.join(BACKUP_DIR, os.path.basename(src))
            shutil.copy2(src, dst)
            print(f"    [OK] Archived {src} -> {dst}")

    # Summary
    conn = get_connection(target_db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM students;")
    total_students = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM internships;")
    total_internships = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM skills;")
    total_skills = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM ratings;")
    total_ratings = cur.fetchone()[0]
    conn.close()

    print("\n" + "=" * 50)
    print("  Phase 2 SQLite Migration Complete!")
    print("=" * 50)
    print(f"  Total Students     : {total_students}")
    print(f"  Total Internships  : {total_internships}")
    print(f"  Normalized Skills  : {total_skills}")
    print(f"  Total Ratings      : {total_ratings}")
    print(f"  Database Location  : {target_db}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_migration()
