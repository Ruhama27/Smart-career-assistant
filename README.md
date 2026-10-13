# 🎯 PathFinder AI — Internship Matching & Career Readiness Platform

> **From "which internship?" to "am I ready — and how do I get there?"**

An AI-powered platform that helps students discover internships they're eligible for, understand exactly what skills they're missing, and get a roadmap to become a stronger candidate.

---

## 🚀 What's New — Phase 2: Database & Data Model Upgrades

This release upgrades the system from flat CSV storage to a fully normalized SQLite database architecture:

| Upgrade | What Changed |
|---|---|
| 🗄️ **Normalized SQLite Schema** | Third Normal Form (3NF) database with foreign key constraints in `database/schema.sql` |
| 🧩 **First-Class Skills Lookup** | Skills stored as individual entities in `skills`, linked through `student_skills` and `internship_skills` |
| 🔄 **Robust Parameterized SQL** | Full CRUD in `database/db.py`, `modules/profile.py`, and `modules/internship.py` using parameterized queries |
| 📈 **Expanded Dataset (22+ Records)** | Expanded with Ethiopian university students (DBU, AAU, ASTU, Hawassa, BDU) and tech companies (Safaricom, Ethio Telecom, CBE, Gebeya, Chapa, Meta, Apple, Netflix) |
| 🛡️ **Automated Migration Tool** | `database/migrate.py` imports legacy data, expands datasets, and archives original CSV files |
| 🧪 **Comprehensive Test Suite** | **41 automated tests passing** across Phase 1 and Phase 2 (`pytest tests/ -v`) |

---

## 📌 Project Overview

PathFinder AI answers four questions for every student:

| Question | Feature |
|---|---|
| Which internships suit me? | AI ranking using skills, interests, career goals, eligibility |
| What skills am I missing? | Per-recommendation skill gap analysis *(Phase 3)* |
| How can I become eligible? | Personalized learning roadmap *(Phase 4)* |
| How do I manage applications? | Deadline tracker + application log *(Phase 5)* |

---

## ✨ Features

### 👩‍🎓 Student Management (SQL-Powered)
- View, search, add, update, delete student profiles directly in SQLite
- Supports multiple CGPA scales (both 4.0 and 10.0 scale)
- Normalized skill associations with cascade deletions

### 💼 Internship Management (SQL-Powered)
- View, search, add, update, delete internship postings
- Minimum CGPA validation with `min_cgpa = 0.0` as "no requirement"
- Track company, role, domain, location, duration, remote status, and required skills

### 🤖 Recommendation Systems
| Algorithm | Description |
|---|---|
| Content-Based | TF-IDF + cosine similarity on skills, interests, career goals |
| Collaborative | Rating aggregation from peer students with similar preferences |
| Hybrid | Weighted ensemble (70% content-based + 30% collaborative) |

**All algorithms enforce hard CGPA eligibility filters before ranking.**

### 🌐 Web & CLI Interfaces
- **Web App**: Built with Streamlit (`streamlit run app.py`)
- **CLI**: Interactive terminal console (`python main.py`)

---

## 🛠️ Technologies

- **Python 3.10+** — core language
- **SQLite 3** — normalized relational database with foreign key cascades
- **Pandas + NumPy** — dataframes and matrix manipulations
- **scikit-learn** — TF-IDF vectorization and cosine similarity
- **Streamlit** — interactive web UI
- **pytest** — automated unit and integration testing

---

## 📂 Project Structure

```
AI-Internship-Recommendation-Engine/
│
├── database/
│   ├── schema.sql         ← 3NF SQLite schema, relations & compatibility views
│   ├── db.py              ← Parameterized CRUD functions & connection manager
│   └── migrate.py         ← Migration & dataset expansion tool
│
├── data/
│   ├── pathfinder.db      ← Production SQLite database (22 students, 22 internships)
│   ├── backup_csv/        ← Archived CSV backups
│   ├── students.csv
│   ├── internships.csv
│   └── ratings.csv
│
├── modules/
│   ├── utils.py           ← SQLite data loaders, safe input helpers, CGPA normalization
│   ├── profile.py         ← SQL-based student management
│   ├── internship.py      ← SQL-based internship management
│   ├── content_based.py   ← Content-based recommender with eligibility filtering
│   ├── collaborative.py   ← Collaborative recommender with user-item similarity
│   ├── hybrid.py          ← Hybrid ensemble recommender
│   └── evaluation.py      ← Precision, Recall, RMSE evaluation
│
├── tests/
│   ├── test_phase1.py     ← 21 tests for CGPA normalization & eligibility
│   └── test_phase2_db.py  ← 20 tests for SQLite schema, normalization, CRUD & cascade
│
├── main.py                ← Interactive CLI entrypoint
├── app.py                 ← Streamlit web dashboard
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/Ruhama27/Smart-career-assistant.git
cd Smart-career-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize or Migrate Database
```bash
python -m database.migrate
```

### 4. Run the web interface (recommended)
```bash
streamlit run app.py
```

### 5. Or run the CLI
```bash
python main.py
```

### 6. Run all automated tests
```bash
pytest tests/ -v
```

---

## 🗺️ Implementation Roadmap

| Phase | Status | Focus |
|---|---|---|
| Phase 1 | ✅ **Done** | Bug fixes, CGPA filter, safe inputs, 21 tests |
| Phase 2 | ✅ **Done** | SQLite database, normalized schema, 22+ expanded records, 41 tests |
| Phase 3 | 🔜 **Next** | Explainable weighted scoring ($S = 0.45K + 0.20I + 0.15E + 0.10L + 0.10T$) & skill gap |
| Phase 4 | 🔜 | CV parser (PDF/DOCX) & learning roadmap generator |
| Phase 5 | 🔜 | Application tracker, bookmarks, deadline highlights |
| Phase 6 | 🔜 | Deployment & portfolio presentation |

---

## 👩‍💻 Author

**Ruhama Nigusu**

Building PathFinder AI as a portfolio project demonstrating real-world AI engineering:
recommendation systems, NLP, relational data modeling, and software engineering best practices.