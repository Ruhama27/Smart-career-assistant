# 🎯 PathFinder AI — Internship Matching & Career Readiness Platform

> **From "which internship?" to "am I ready — and how do I get there?"**

An AI-powered platform that helps students discover internships they're eligible for, understand exactly what skills they're missing, and get a roadmap to become a stronger candidate.

---

## 🚀 What's New — Phase 1 Upgrades

This version includes a complete reliability overhaul:

| Fix | What changed |
|---|---|
| ✅ **CGPA eligibility filter** | Ineligible internships are never shown — `min_cgpa=0.0` correctly means "no requirement" |
| ✅ **Safe input validation** | Bad CGPA entry (e.g. typing a word) no longer crashes the app |
| ✅ **Stale-data bug fixed** | Adding a student then immediately recommending now works correctly |
| ✅ **CGPA scale normalization** | Compares 4.0-scale and 10.0-scale CGPAs correctly |
| ✅ **Delete confirmation** | Accidental deletes are prevented with a confirmation prompt |
| ✅ **Automated tests** | 17 tests covering all Phase 1 changes (`pytest tests/`) |

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

## ✨ Current Features

### 👩‍🎓 Student Management
- View, search, add, update, delete student profiles
- Safe CGPA input (0.0–10.0) with validation

### 💼 Internship Management
- View, search, add, update, delete internship listings
- `min_cgpa = 0.0` clearly means "no requirement"

### 🤖 Recommendation Systems
| Algorithm | Description |
|---|---|
| Content-Based | TF-IDF + cosine similarity on skills, interests, career goal |
| Collaborative | Ratings from similar students |
| Hybrid | 70% content-based + 30% collaborative |

**All algorithms filter out internships the student is not eligible for before ranking.**

### 📊 Evaluation Metrics
- Precision, Recall, RMSE (evaluated on synthetic test data)

### 🌐 Web Interface
```bash
streamlit run app.py
# Open: http://localhost:8501
```

---

## 🛠️ Technologies

- **Python** — core language
- **Pandas + NumPy** — data manipulation
- **scikit-learn** — TF-IDF, cosine similarity
- **Streamlit** — web dashboard
- **pytest** — automated testing

---

## 📂 Project Structure

```
PathFinder-AI/
│
├── data/
│   ├── students.csv
│   ├── internships.csv
│   └── ratings.csv
│
├── modules/
│   ├── utils.py           ← NEW: safe inputs, CGPA normalization, data loaders
│   ├── profile.py         ← Phase 1: safe inputs, fresh data loading
│   ├── internship.py      ← Phase 1: safe inputs, fresh data loading
│   ├── content_based.py   ← Phase 1: CGPA filter, fresh data loading
│   ├── collaborative.py   ← Phase 1: CGPA filter, fresh data loading
│   ├── hybrid.py          ← Phase 1: fixed duplicate output
│   └── evaluation.py
│
├── tests/
│   └── test_phase1.py     ← NEW: 17 automated tests
│
├── main.py                ← CLI interface
├── app.py                 ← Streamlit web interface
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

### 3. Run the web interface (recommended)
```bash
streamlit run app.py
```

### 4. Or run the CLI
```bash
python main.py
```

### 5. Run tests
```bash
pytest tests/ -v
```

---

## 🧠 Recommendation Engine

### Eligibility Filter (runs first — always)
```
If student.cgpa < internship.min_cgpa → exclude
If internship.min_cgpa == 0.0        → no requirement, always include
```

### Content-Based Scoring
Uses TF-IDF vectorization + cosine similarity on:
- Student: `skills + interests + career_goal`
- Internship: `required_skills + domain + role`

### Collaborative Filtering
Finds students with similar rating patterns and recommends what they liked.

### Hybrid (default)
```
final_score = 0.70 × content_score + 0.30 × collaborative_score
```

---

## 📊 Evaluation

```
Precision : 0.5    (synthetic test data)
Recall    : 0.67   (synthetic test data)
RMSE      : 0.21   (synthetic test data)
```

> ⚠️ Evaluation uses synthetic data. Replace with real student ratings for meaningful results.

---

## 🗺️ Implementation Roadmap

| Phase | Status | Focus |
|---|---|---|
| Phase 1 | ✅ **Done** | Bug fixes, CGPA filter, safe inputs, tests |
| Phase 2 | 🔜 Next | SQLite database, normalized schema |
| Phase 3 | 🔜 | Weighted AI scoring, skill gap analysis |
| Phase 4 | 🔜 | CV upload & parser, learning roadmap |
| Phase 5 | 🔜 | Bookmarks, application tracker, dashboards |
| Phase 6 | 🔜 | Testing, deployment, documentation |

---

## 👩‍💻 Author

**Ruhama Nigusu**

Building PathFinder AI as a portfolio project demonstrating real-world AI engineering:
recommendation systems, NLP, data modeling, and software engineering best practices.

---

⭐ If you found this project useful, please star the repository.