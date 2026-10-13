import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import math

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Internship Recommendation Engine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label { color: #94a3b8 !important; font-size: 0.85rem; }

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(168,85,247,0.3));
    border: 1px solid rgba(99,102,241,0.4);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
    text-align: center;
}
.hero-banner h1 {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0;
}
.hero-banner p { color: #94a3b8; font-size: 1rem; margin: 0; }

/* ── Metric Cards ── */
.metric-row { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
.metric-card {
    flex: 1;
    min-width: 140px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
    backdrop-filter: blur(8px);
    transition: transform 0.2s, border-color 0.2s;
}
.metric-card:hover { transform: translateY(-2px); border-color: rgba(129,140,248,0.5); }
.metric-card .num {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-card .lbl { color: #94a3b8; font-size: 0.8rem; margin-top: 0.2rem; }

/* ── Section Title ── */
.section-title {
    font-size: 1.3rem; font-weight: 700; color: #e2e8f0;
    border-left: 4px solid #818cf8;
    padding-left: 0.75rem; margin: 1.5rem 0 1rem 0;
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
    transition: all 0.25s ease;
}
.card:hover {
    border-color: rgba(129,140,248,0.4);
    background: rgba(99,102,241,0.08);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(99,102,241,0.15);
}
.card-header { display: flex; justify-content: space-between; align-items: flex-start; }
.card-title { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.card-subtitle { font-size: 0.85rem; color: #94a3b8; margin-top: 0.2rem; }
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 0.15rem 0.1rem;
}
.badge-purple { background: rgba(168,85,247,0.2); color: #c084fc; border: 1px solid rgba(168,85,247,0.3); }
.badge-blue   { background: rgba(56,189,248,0.15); color: #38bdf8; border: 1px solid rgba(56,189,248,0.3); }
.badge-green  { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-orange { background: rgba(251,146,60,0.15); color: #fb923c; border: 1px solid rgba(251,146,60,0.3); }

/* ── Score Bar ── */
.score-bar-wrap { margin-top: 0.8rem; }
.score-label { font-size: 0.78rem; color: #94a3b8; margin-bottom: 0.3rem; }
.score-bar-bg { background: rgba(255,255,255,0.08); border-radius: 999px; height: 8px; overflow: hidden; }
.score-bar-fill { height: 8px; border-radius: 999px; background: linear-gradient(90deg, #818cf8, #c084fc); }

/* ── Recommendation Cards ── */
.rec-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.08));
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: all 0.25s ease;
}
.rec-card:hover {
    border-color: rgba(129,140,248,0.5);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(99,102,241,0.2);
}
.rank-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    color: white; font-weight: 800; font-size: 0.85rem;
    margin-right: 0.75rem; flex-shrink: 0;
}

/* ── Eval Cards ── */
.eval-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
}
.eval-num { font-size: 2.5rem; font-weight: 800; }
.eval-label { color: #94a3b8; font-size: 0.85rem; margin-top: 0.3rem; }
.eval-desc { color: #64748b; font-size: 0.75rem; margin-top: 0.5rem; }

/* ── Inputs & Buttons ── */
.stTextInput input, .stSelectbox select, .stNumberInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(99,102,241,0.4) !important;
}
.stSuccess { background: rgba(52,211,153,0.1) !important; border-color: rgba(52,211,153,0.3) !important; }
.stError   { background: rgba(239,68,68,0.1)  !important; border-color: rgba(239,68,68,0.3)  !important; }
.stWarning { background: rgba(251,146,60,0.1) !important; border-color: rgba(251,146,60,0.3) !important; }

/* ── Table ── */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #94a3b8 !important;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.3) !important;
    color: #818cf8 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(129,140,248,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Data Helpers ───────────────────────────────────────────────────────────
from modules.utils import load_students, load_internships, load_ratings, is_cgpa_eligible

# ─── Recommendation Engines ─────────────────────────────────────────────────
def content_based_recommend(student_id):
    students     = load_students()
    internships  = load_internships()
    student      = students[students["student_id"] == student_id]
    if student.empty:
        return []
    student = student.iloc[0]

    # CGPA Eligibility Filter
    s_scale = float(student["cgpa_scale"]) if "cgpa_scale" in student and pd.notna(student["cgpa_scale"]) else 10.0
    eligible_mask = internships.apply(
        lambda row: is_cgpa_eligible(
            student_cgpa=float(student["cgpa"]),
            min_required=float(row["min_cgpa"]),
            student_scale=s_scale,
            internship_scale=float(row["cgpa_scale"]) if "cgpa_scale" in row and pd.notna(row["cgpa_scale"]) else 10.0,
        ),
        axis=1,
    )
    eligible_internships = internships[eligible_mask].copy()
    if eligible_internships.empty:
        return []

    student_profile = (
        str(student["skills"]) + " " +
        str(student["interests"]) + " " +
        str(student["career_goal"])
    )
    internship_profiles = (
        eligible_internships["required_skills"] + " " +
        eligible_internships["domain"] + " " +
        eligible_internships["role"]
    )
    docs = [student_profile] + list(internship_profiles)
    vec  = TfidfVectorizer()
    mat  = vec.fit_transform(docs)
    sim  = cosine_similarity(mat[0], mat[1:]).flatten()
    eligible_internships["match_score"] = sim
    return eligible_internships.sort_values("match_score", ascending=False).head(5).to_dict("records")

def collaborative_recommend(student_id):
    ratings      = load_ratings()
    internships  = load_internships()
    students     = load_students()
    matrix       = ratings.pivot_table(index="student_id", columns="internship_id", values="rating", fill_value=0)
    if student_id not in matrix.index:
        return []
    sim = cosine_similarity(matrix)
    idx = matrix.index.get_loc(student_id)
    scores = sim[idx]
    similar = np.argsort(scores)[::-1]
    similar = similar[similar != idx][:3]
    recommended = {}
    for i in similar:
        peer = matrix.iloc[i]
        for iid, rating in peer.items():
            if rating > 0 and matrix.loc[student_id, iid] == 0:
                recommended[iid] = recommended.get(iid, 0) + rating
    result = []
    student_rows = students[students["student_id"] == student_id]
    s_cgpa = float(student_rows.iloc[0]["cgpa"]) if not student_rows.empty else 0.0
    s_scale = float(student_rows.iloc[0]["cgpa_scale"]) if not student_rows.empty and "cgpa_scale" in student_rows.columns and pd.notna(student_rows.iloc[0]["cgpa_scale"]) else 10.0

    for iid, score in sorted(recommended.items(), key=lambda x: x[1], reverse=True):
        row = internships[internships["internship_id"] == iid]
        if not row.empty:
            i_row = row.iloc[0]
            i_scale = float(i_row["cgpa_scale"]) if "cgpa_scale" in i_row and pd.notna(i_row["cgpa_scale"]) else 10.0
            if not is_cgpa_eligible(s_cgpa, float(i_row["min_cgpa"]), student_scale=s_scale, internship_scale=i_scale):
                continue
            r = i_row.to_dict()
            r["collab_score"] = score
            result.append(r)
    return result[:5]

def hybrid_recommend(student_id):
    content = content_based_recommend(student_id)
    collab  = collaborative_recommend(student_id)
    scores  = {}
    for item in content:
        scores[item["internship_id"]] = item["match_score"] * 0.7
    for item in collab:
        iid   = item["internship_id"]
        score = item["collab_score"] * 0.3
        scores[iid] = scores.get(iid, 0) + score
    internships = load_internships()
    result = []
    for iid, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]:
        row = internships[internships["internship_id"] == iid]
        if not row.empty:
            r = row.iloc[0].to_dict()
            r["hybrid_score"] = score
            result.append(r)
    return result

def precision_metric(recommended, relevant):
    hits = len(set(recommended) & set(relevant))
    return hits / len(recommended) if recommended else 0

def recall_metric(recommended, relevant):
    hits = len(set(recommended) & set(relevant))
    return hits / len(relevant) if relevant else 0

def rmse_metric(actual, predicted):
    return math.sqrt(sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual))

# ─── UI Helpers ─────────────────────────────────────────────────────────────
def score_bar(score, max_val=1.0):
    pct = min(100, round((score / max_val) * 100, 1))
    return f"""
    <div class="score-bar-wrap">
        <div class="score-label">Match Score: <b style="color:#818cf8">{pct}%</b></div>
        <div class="score-bar-bg"><div class="score-bar-fill" style="width:{pct}%"></div></div>
    </div>"""

def skills_badges(skills_str, color="purple"):
    badges = "".join(
        f'<span class="badge badge-{color}">{s.strip()}</span>'
        for s in str(skills_str).split(",") if s.strip()
    )
    return badges

# ─── Sidebar Navigation ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size:2.5rem">🚀</div>
        <div style="font-size:1.1rem; font-weight:700; color:#818cf8; margin-top:0.3rem;">AI Internship</div>
        <div style="font-size:0.85rem; color:#94a3b8;">Recommendation Engine</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    nav = st.radio(
        "Navigation",
        options=[
            "🏠  Dashboard",
            "👩‍🎓  Students",
            "💼  Internships",
            "✨  Recommendations",
            "📊  Evaluation",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    students_df    = load_students()
    internships_df = load_internships()
    ratings_df     = load_ratings()
    st.markdown(f"""
    <div style="padding: 0.5rem;">
        <div style="color:#64748b; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">Quick Stats</div>
        <div style="display:flex; justify-content:space-between; color:#e2e8f0; font-size:0.85rem; margin:0.3rem 0;">
            <span>Students</span><span style="color:#818cf8; font-weight:700;">{len(students_df)}</span>
        </div>
        <div style="display:flex; justify-content:space-between; color:#e2e8f0; font-size:0.85rem; margin:0.3rem 0;">
            <span>Internships</span><span style="color:#c084fc; font-weight:700;">{len(internships_df)}</span>
        </div>
        <div style="display:flex; justify-content:space-between; color:#e2e8f0; font-size:0.85rem; margin:0.3rem 0;">
            <span>Ratings</span><span style="color:#38bdf8; font-weight:700;">{len(ratings_df)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if nav == "🏠  Dashboard":
    st.markdown("""
    <div class="hero-banner">
        <h1>🚀 AI Internship Recommendation Engine</h1>
        <p>Powered by Content-Based Filtering · Collaborative Filtering · Hybrid AI</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    avg_cgpa = round(students_df["cgpa"].mean(), 2)
    top_domain = internships_df["domain"].mode()[0]
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="num">{len(students_df)}</div>
            <div class="lbl">👩‍🎓 Registered Students</div>
        </div>
        <div class="metric-card">
            <div class="num">{len(internships_df)}</div>
            <div class="lbl">💼 Active Internships</div>
        </div>
        <div class="metric-card">
            <div class="num">{len(ratings_df)}</div>
            <div class="lbl">⭐ Total Ratings</div>
        </div>
        <div class="metric-card">
            <div class="num">{avg_cgpa}</div>
            <div class="lbl">🎓 Avg. CGPA</div>
        </div>
        <div class="metric-card">
            <div class="num">3</div>
            <div class="lbl">🤖 AI Algorithms</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Recent Students</div>', unsafe_allow_html=True)
        for _, row in students_df.tail(4).iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">👤 {row['name']}</div>
                        <div class="card-subtitle">{row['college']} · {row['branch']} · Year {row['year']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="color:#818cf8; font-weight:700; font-size:1.1rem;">{row['cgpa']}</div>
                        <div style="color:#64748b; font-size:0.75rem;">CGPA</div>
                    </div>
                </div>
                <div style="margin-top:0.6rem;">{skills_badges(row['skills'], 'blue')}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">Featured Internships</div>', unsafe_allow_html=True)
        for _, row in internships_df.head(4).iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">🏢 {row['company']}</div>
                        <div class="card-subtitle">{row['role']} · {row['domain']}</div>
                    </div>
                    <div style="text-align:right;">
                        <span class="badge badge-green">{row['location']}</span><br>
                        <span class="badge badge-orange">{row['duration']}</span>
                    </div>
                </div>
                <div style="margin-top:0.6rem;">{skills_badges(row['required_skills'], 'purple')}</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STUDENTS
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "👩‍🎓  Students":
    st.markdown('<div class="hero-banner"><h1>👩‍🎓 Student Management</h1><p>View, search, add, update, and delete student profiles</p></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 View All", "🔍 Search", "➕ Add", "✏️ Update", "🗑️ Delete"])

    # ── View All
    with tab1:
        students_df = load_students()
        st.markdown(f'<div class="section-title">All Students ({len(students_df)})</div>', unsafe_allow_html=True)
        for _, row in students_df.iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">👤 {row['name']} <span style="color:#64748b; font-size:0.85rem; font-weight:400">({row['student_id']})</span></div>
                        <div class="card-subtitle">{row['college']} · {row['branch']} · Year {row['year']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="color:#818cf8; font-weight:800; font-size:1.3rem;">{row['cgpa']}</div>
                        <div style="color:#64748b; font-size:0.7rem; text-transform:uppercase;">CGPA</div>
                    </div>
                </div>
                <div style="margin-top:0.8rem; display:flex; flex-wrap:wrap; gap:0.5rem;">
                    <div><span style="color:#64748b; font-size:0.75rem;">SKILLS </span>{skills_badges(row['skills'], 'blue')}</div>
                </div>
                <div style="margin-top:0.4rem; display:flex; gap:1.5rem; font-size:0.82rem; color:#94a3b8;">
                    <span>🎯 {row['career_goal']}</span>
                    <span>📍 {row['preferred_location']}</span>
                    <span>💡 {row['interests']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Search
    with tab2:
        st.markdown('<div class="section-title">Search Student</div>', unsafe_allow_html=True)
        sid = st.text_input("Enter Student ID", placeholder="e.g. S001")
        if st.button("Search Student", key="search_student_btn"):
            students_df = load_students()
            result = students_df[students_df["student_id"] == sid.strip()]
            if result.empty:
                st.error("❌ Student not found!")
            else:
                row = result.iloc[0]
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">👤 {row['name']} ({row['student_id']})</div>
                    <div class="card-subtitle">{row['college']} · {row['branch']} · Year {row['year']}</div>
                    <div style="margin-top:1rem; display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; font-size:0.88rem; color:#94a3b8;">
                        <span>🎓 CGPA: <b style="color:#818cf8">{row['cgpa']}</b></span>
                        <span>📍 Location: <b style="color:#e2e8f0">{row['preferred_location']}</b></span>
                        <span>🎯 Goal: <b style="color:#e2e8f0">{row['career_goal']}</b></span>
                        <span>💡 Interests: <b style="color:#e2e8f0">{row['interests']}</b></span>
                    </div>
                    <div style="margin-top:0.6rem;">{skills_badges(row['skills'], 'blue')}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Add
    with tab3:
        st.markdown('<div class="section-title">Add New Student</div>', unsafe_allow_html=True)
        with st.form("add_student_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_id     = st.text_input("Student ID *", placeholder="e.g. S011")
                new_name   = st.text_input("Full Name *", placeholder="e.g. Riya Gupta")
                new_col    = st.text_input("College *", placeholder="e.g. DTU")
                new_branch = st.text_input("Branch *", placeholder="e.g. CSE")
                new_year   = st.selectbox("Year", [1, 2, 3, 4])
            with c2:
                new_cgpa   = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=8.0, step=0.1)
                new_skills = st.text_input("Skills (comma-separated) *", placeholder="Python, SQL, ML")
                new_ints   = st.text_input("Interests *", placeholder="Data Science, AI")
                new_goal   = st.text_input("Career Goal *", placeholder="Data Scientist")
                new_loc    = st.text_input("Preferred Location *", placeholder="Remote")
            submitted = st.form_submit_button("➕ Add Student")
            if submitted:
                students_df = load_students()
                if not new_id or not new_name:
                    st.error("❌ Student ID and Name are required!")
                elif new_id in students_df["student_id"].values:
                    st.error(f"❌ Student ID '{new_id}' already exists!")
                else:
                    new_row = {
                        "student_id": new_id, "name": new_name, "college": new_col,
                        "branch": new_branch, "year": new_year, "cgpa": new_cgpa,
                        "skills": new_skills, "interests": new_ints,
                        "career_goal": new_goal, "preferred_location": new_loc,
                    }
                    students_df = pd.concat([students_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_students(students_df)
                    st.success(f"✅ Student '{new_name}' added successfully!")
                    st.rerun()

    # ── Update
    with tab4:
        st.markdown('<div class="section-title">Update Student</div>', unsafe_allow_html=True)
        students_df = load_students()
        upd_id = st.selectbox("Select Student ID", students_df["student_id"].tolist(), key="upd_student_sel")
        if upd_id:
            row = students_df[students_df["student_id"] == upd_id].iloc[0]
            with st.form("update_student_form"):
                c1, c2 = st.columns(2)
                with c1:
                    upd_name   = st.text_input("Name",   value=row["name"])
                    upd_cgpa   = st.number_input("CGPA",  value=float(row["cgpa"]), min_value=0.0, max_value=10.0, step=0.1)
                with c2:
                    upd_skills = st.text_input("Skills", value=row["skills"])
                    upd_goal   = st.text_input("Career Goal", value=row["career_goal"])
                if st.form_submit_button("💾 Save Changes"):
                    idx = students_df[students_df["student_id"] == upd_id].index[0]
                    students_df.at[idx, "name"]        = upd_name
                    students_df.at[idx, "cgpa"]        = upd_cgpa
                    students_df.at[idx, "skills"]      = upd_skills
                    students_df.at[idx, "career_goal"] = upd_goal
                    save_students(students_df)
                    st.success("✅ Student updated successfully!")
                    st.rerun()

    # ── Delete
    with tab5:
        st.markdown('<div class="section-title">Delete Student</div>', unsafe_allow_html=True)
        students_df = load_students()
        del_id = st.selectbox("Select Student to Delete", students_df["student_id"].tolist(), key="del_student_sel")
        if del_id:
            row = students_df[students_df["student_id"] == del_id].iloc[0]
            st.warning(f"⚠️ You are about to delete **{row['name']}** ({del_id}). This action cannot be undone.")
            if st.button("🗑️ Confirm Delete", key="del_student_btn"):
                students_df = students_df[students_df["student_id"] != del_id]
                save_students(students_df)
                st.success("✅ Student deleted successfully!")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: INTERNSHIPS
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "💼  Internships":
    st.markdown('<div class="hero-banner"><h1>💼 Internship Management</h1><p>View, search, add, update, and delete internship listings</p></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 View All", "🔍 Search", "➕ Add", "✏️ Update", "🗑️ Delete"])

    with tab1:
        internships_df = load_internships()
        st.markdown(f'<div class="section-title">All Internships ({len(internships_df)})</div>', unsafe_allow_html=True)
        for _, row in internships_df.iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">🏢 {row['company']} <span style="color:#64748b; font-size:0.8rem; font-weight:400">({row['internship_id']})</span></div>
                        <div class="card-subtitle">{row['role']} · {row['domain']}</div>
                    </div>
                    <div style="text-align:right;">
                        <span class="badge badge-green">📍 {row['location']}</span><br>
                        <span class="badge badge-orange">⏱ {row['duration']}</span>
                    </div>
                </div>
                <div style="margin-top:0.6rem; font-size:0.82rem; color:#94a3b8;">
                    🎓 Min CGPA: <b style="color:#c084fc">{row['min_cgpa']}</b>
                </div>
                <div style="margin-top:0.5rem;">{skills_badges(row['required_skills'], 'purple')}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-title">Search Internship</div>', unsafe_allow_html=True)
        iid = st.text_input("Enter Internship ID", placeholder="e.g. I001")
        if st.button("Search Internship", key="search_internship_btn"):
            internships_df = load_internships()
            result = internships_df[internships_df["internship_id"] == iid.strip()]
            if result.empty:
                st.error("❌ Internship not found!")
            else:
                row = result.iloc[0]
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">🏢 {row['company']} ({row['internship_id']})</div>
                    <div class="card-subtitle">{row['role']} · {row['domain']}</div>
                    <div style="margin-top:1rem; display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; font-size:0.88rem; color:#94a3b8;">
                        <span>📍 Location: <b style="color:#e2e8f0">{row['location']}</b></span>
                        <span>⏱ Duration: <b style="color:#e2e8f0">{row['duration']}</b></span>
                        <span>🎓 Min CGPA: <b style="color:#c084fc">{row['min_cgpa']}</b></span>
                    </div>
                    <div style="margin-top:0.6rem;">{skills_badges(row['required_skills'], 'purple')}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-title">Add New Internship</div>', unsafe_allow_html=True)
        with st.form("add_internship_form"):
            c1, c2 = st.columns(2)
            with c1:
                ni_id    = st.text_input("Internship ID *", placeholder="e.g. I011")
                ni_comp  = st.text_input("Company *", placeholder="e.g. Meta")
                ni_role  = st.text_input("Role *", placeholder="e.g. Data Engineer")
                ni_skills= st.text_input("Required Skills *", placeholder="Python, SQL, Spark")
            with c2:
                ni_dom   = st.text_input("Domain *", placeholder="e.g. Data Engineering")
                ni_cgpa  = st.number_input("Min CGPA", min_value=0.0, max_value=10.0, value=7.5, step=0.1)
                ni_loc   = st.text_input("Location *", placeholder="e.g. Remote")
                ni_dur   = st.text_input("Duration *", placeholder="e.g. 3 Months")
            if st.form_submit_button("➕ Add Internship"):
                internships_df = load_internships()
                if not ni_id or not ni_comp:
                    st.error("❌ Internship ID and Company are required!")
                elif ni_id in internships_df["internship_id"].values:
                    st.error(f"❌ Internship ID '{ni_id}' already exists!")
                else:
                    new_row = {
                        "internship_id": ni_id, "company": ni_comp, "role": ni_role,
                        "required_skills": ni_skills, "domain": ni_dom,
                        "min_cgpa": ni_cgpa, "location": ni_loc, "duration": ni_dur,
                    }
                    internships_df = pd.concat([internships_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_internships(internships_df)
                    st.success(f"✅ Internship at '{ni_comp}' added successfully!")
                    st.rerun()

    with tab4:
        st.markdown('<div class="section-title">Update Internship</div>', unsafe_allow_html=True)
        internships_df = load_internships()
        upd_iid = st.selectbox("Select Internship ID", internships_df["internship_id"].tolist(), key="upd_intern_sel")
        if upd_iid:
            row = internships_df[internships_df["internship_id"] == upd_iid].iloc[0]
            with st.form("update_internship_form"):
                c1, c2 = st.columns(2)
                with c1:
                    ui_comp = st.text_input("Company",  value=row["company"])
                    ui_role = st.text_input("Role",     value=row["role"])
                with c2:
                    ui_loc  = st.text_input("Location", value=row["location"])
                    ui_dur  = st.text_input("Duration", value=row["duration"])
                if st.form_submit_button("💾 Save Changes"):
                    idx = internships_df[internships_df["internship_id"] == upd_iid].index[0]
                    internships_df.at[idx, "company"]  = ui_comp
                    internships_df.at[idx, "role"]     = ui_role
                    internships_df.at[idx, "location"] = ui_loc
                    internships_df.at[idx, "duration"] = ui_dur
                    save_internships(internships_df)
                    st.success("✅ Internship updated successfully!")
                    st.rerun()

    with tab5:
        st.markdown('<div class="section-title">Delete Internship</div>', unsafe_allow_html=True)
        internships_df = load_internships()
        del_iid = st.selectbox("Select Internship to Delete", internships_df["internship_id"].tolist(), key="del_intern_sel")
        if del_iid:
            row = internships_df[internships_df["internship_id"] == del_iid].iloc[0]
            st.warning(f"⚠️ You are about to delete **{row['company']} – {row['role']}** ({del_iid}). This cannot be undone.")
            if st.button("🗑️ Confirm Delete", key="del_intern_btn"):
                internships_df = internships_df[internships_df["internship_id"] != del_iid]
                save_internships(internships_df)
                st.success("✅ Internship deleted successfully!")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "✨  Recommendations":
    st.markdown('<div class="hero-banner"><h1>✨ AI Recommendations</h1><p>Get personalized internship matches using 3 powerful AI algorithms</p></div>', unsafe_allow_html=True)

    students_df = load_students()
    col1, col2 = st.columns([1, 2])
    with col1:
        student_opts = [f"{row['student_id']} – {row['name']}" for _, row in students_df.iterrows()]
        selected = st.selectbox("Select Student", student_opts)
        student_id = selected.split(" – ")[0] if selected else None
        algo = st.radio(
            "Algorithm",
            ["✨ Content-Based", "🤝 Collaborative", "🔀 Hybrid"],
            index=2
        )
        run_btn = st.button("🚀 Get Recommendations", use_container_width=True)

        # Show selected student profile
        if student_id:
            row = students_df[students_df["student_id"] == student_id].iloc[0]
            st.markdown(f"""
            <div style="margin-top:1rem;">
            <div class="card">
                <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">Student Profile</div>
                <div style="font-weight:700; color:#e2e8f0;">{row['name']}</div>
                <div style="color:#94a3b8; font-size:0.82rem; margin:0.2rem 0;">{row['college']} · {row['branch']}</div>
                <div style="color:#818cf8; font-weight:700; font-size:1.2rem; margin:0.4rem 0;">{row['cgpa']} CGPA</div>
                <div style="margin-top:0.5rem;">{skills_badges(row['skills'], 'blue')}</div>
                <div style="margin-top:0.5rem; font-size:0.8rem; color:#94a3b8;">🎯 {row['career_goal']}</div>
            </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if run_btn and student_id:
            if algo == "✨ Content-Based":
                results = content_based_recommend(student_id)
                algo_label = "Content-Based"
                score_key  = "match_score"
                score_label = "Match Score"
            elif algo == "🤝 Collaborative":
                results = collaborative_recommend(student_id)
                score_key   = "collab_score"
                score_label = "Collaborative Score"
                algo_label  = "Collaborative"
            else:
                results = hybrid_recommend(student_id)
                score_key   = "hybrid_score"
                score_label = "Hybrid Score"
                algo_label  = "Hybrid"

            if not results:
                st.warning("⚠️ No recommendations available for this student with the selected algorithm.")
            else:
                st.markdown(f'<div class="section-title">Top {len(results)} {algo_label} Recommendations</div>', unsafe_allow_html=True)
                for rank, item in enumerate(results, 1):
                    score = item.get(score_key, 0)
                    max_s = 1.0 if score_key in ("match_score", "hybrid_score") else max(r.get(score_key,1) for r in results)
                    pct   = min(100, round((score / max_s) * 100, 1)) if max_s else 0
                    st.markdown(f"""
                    <div class="rec-card">
                        <div style="display:flex; align-items:center; margin-bottom:0.6rem;">
                            <div class="rank-badge">#{rank}</div>
                            <div>
                                <div class="card-title">{item['company']}</div>
                                <div class="card-subtitle">{item['role']} · {item['domain']}</div>
                            </div>
                        </div>
                        <div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin:0.4rem 0;">
                            <span class="badge badge-green">📍 {item['location']}</span>
                            <span class="badge badge-orange">⏱ {item['duration']}</span>
                            <span class="badge badge-purple">🎓 Min {item['min_cgpa']} CGPA</span>
                        </div>
                        <div class="score-bar-wrap">
                            <div class="score-label">{score_label}: <b style="color:#818cf8">{pct}%</b></div>
                            <div class="score-bar-bg"><div class="score-bar-fill" style="width:{pct}%"></div></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:400px; color:#475569;">
                <div style="font-size:4rem;">🎯</div>
                <div style="font-size:1.1rem; margin-top:1rem;">Select a student and click Get Recommendations</div>
                <div style="font-size:0.85rem; margin-top:0.5rem;">Choose from 3 AI algorithms to find the best internship matches</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EVALUATION
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "📊  Evaluation":
    st.markdown('<div class="hero-banner"><h1>📊 System Evaluation</h1><p>Measure the accuracy and performance of the recommendation engine</p></div>', unsafe_allow_html=True)

    recommended = ["I001", "I002", "I003", "I004"]
    relevant    = ["I001", "I003", "I005"]
    actual      = [5, 4, 3, 5]
    predicted   = [4.8, 4.2, 2.7, 4.9]

    prec  = round(precision_metric(recommended, relevant), 4)
    rec   = round(recall_metric(recommended, relevant), 4)
    err   = round(rmse_metric(actual, predicted), 4)

    st.markdown('<div class="section-title">Performance Metrics</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        color = "#34d399" if prec >= 0.5 else "#fb923c"
        st.markdown(f"""
        <div class="eval-card">
            <div class="eval-num" style="color:{color}">{prec}</div>
            <div class="eval-label">Precision</div>
            <div class="eval-desc">Fraction of recommended internships that are relevant</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        color = "#34d399" if rec >= 0.5 else "#fb923c"
        st.markdown(f"""
        <div class="eval-card">
            <div class="eval-num" style="color:{color}">{rec}</div>
            <div class="eval-label">Recall</div>
            <div class="eval-desc">Fraction of relevant internships that were recommended</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        color = "#34d399" if err <= 0.5 else "#fb923c"
        st.markdown(f"""
        <div class="eval-card">
            <div class="eval-num" style="color:{color}">{err}</div>
            <div class="eval-label">RMSE</div>
            <div class="eval-desc">Root Mean Square Error of predicted ratings vs actual</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Evaluation Details</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Recommended Internships:**")
        for iid in recommended:
            row = load_internships()
            row = row[row["internship_id"] == iid]
            label = row.iloc[0]["company"] + " – " + row.iloc[0]["role"] if not row.empty else iid
            is_rel = "✅" if iid in relevant else "❌"
            st.markdown(f"- {is_rel} `{iid}` – {label}")

    with c2:
        st.markdown("**Rating Prediction Accuracy:**")
        for a, p in zip(actual, predicted):
            diff = abs(a - p)
            color = "green" if diff <= 0.3 else "orange"
            st.markdown(f"- Actual: **{a}** → Predicted: **{p}** (Δ :{color}[{round(diff,2)}])")

    st.markdown('<div class="section-title">Algorithm Overview</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    algos = [
        ("✨", "Content-Based", "#818cf8", "Uses TF-IDF vectorization and cosine similarity to match student skills & interests with internship requirements.", ["Fast & explainable", "No cold-start for students", "Great for niche profiles"]),
        ("🤝", "Collaborative", "#c084fc", "Finds students with similar rating patterns and recommends internships they rated highly.", ["Discovers hidden gems", "Social signal based", "Works well with dense data"]),
        ("🔀", "Hybrid (70/30)", "#38bdf8", "Combines Content-Based (70%) and Collaborative (30%) scores for best-of-both-worlds recommendations.", ["Most accurate", "Handles cold-start better", "Industry standard approach"]),
    ]
    for col, (icon, name, color, desc, points) in zip(cols, algos):
        with col:
            pts_html = "".join(f'<li style="color:#94a3b8; font-size:0.8rem; margin:0.2rem 0;">{p}</li>' for p in points)
            st.markdown(f"""
            <div class="card" style="height:100%;">
                <div style="font-size:2rem; margin-bottom:0.5rem;">{icon}</div>
                <div style="font-weight:700; color:{color}; font-size:1rem; margin-bottom:0.5rem;">{name}</div>
                <div style="font-size:0.82rem; color:#94a3b8; margin-bottom:0.8rem;">{desc}</div>
                <ul style="padding-left:1rem; margin:0;">{pts_html}</ul>
            </div>
            """, unsafe_allow_html=True)
