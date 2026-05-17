import streamlit as st
import fitz
import pandas as pd
import plotly.graph_objects as go
from model import JobRecommendationSystem
from career_predictor import CareerPredictor
from cover_letter import generate_cover_letter_pdf
st.set_page_config(
    page_title="Smart Career Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">', unsafe_allow_html=True)
with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Sidebar Navigation ──
NAV_PAGES = [
    "🏠 Home", "📊 Resume Analysis", "🎯 Job Recommendations",
    "🔍 Skill Gap Analysis", "🎤 Interview Prep", "✏️ Edit Resume",
    "📝 Resume Builder", "✉️ Cover Letter", "🤖 Career Chatbot",
    "📈 Analytics", "🔎 Job Filter",
]
if 'nav_index' not in st.session_state:
    st.session_state.nav_index = 0

with st.sidebar:
    st.markdown('<div style="text-align:center;padding:16px 0 8px;"><span style="font-size:28px;">🧠</span><br/><span style="font-size:18px;font-weight:800;background:linear-gradient(135deg,#6366f1,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Smart Career Assistant</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    selected = st.radio("Navigation", NAV_PAGES,
        index=st.session_state.nav_index,
        label_visibility="collapsed")
    st.session_state.nav_index = NAV_PAGES.index(selected)
    nav_page = selected
    st.markdown("---")
    st.markdown('<div style="text-align:center;font-size:11px;color:#64748b;padding:8px;">Powered by NLP & ML<br/>FAISS • SentenceTransformers<br/>TF-IDF • Logistic Regression</div>', unsafe_allow_html=True)



# ── Shared Setup ──
@st.cache_resource(show_spinner=False)
def load_model():
    return JobRecommendationSystem("JobsFE.csv")
with st.spinner("Initializing AI Engine..."):
    recommender = load_model()
@st.cache_resource(show_spinner=False)
def load_predictor():
    return CareerPredictor()
with st.spinner("Loading Career Predictor..."):
    predictor = load_predictor()
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([p.get_text("text") for p in doc])
    return text.strip()
def extract_skills(text):
    common_skills = ["Python", "SQL", "Java", "C++", "JavaScript", "Machine Learning",
                     "Data Analysis", "Deep Learning", "NLP", "TensorFlow", "AWS", "Streamlit", "React", "Angular",
                     "Docker", "Kubernetes", "Git", "MongoDB", "PostgreSQL", "TypeScript", "Node.js", "Django",
                     "Flask", "Power BI", "Tableau", "Excel", "Azure", "GCP", "Linux", "Agile", "Scrum"]
    text_lower = str(text).lower()
    return [skill for skill in common_skills if skill.lower() in text_lower]
import utils
from resume_builder import generate_pdf
# ═══════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════
if nav_page == "🏠 Home":
    st.markdown('<div class="hero-title">Smart Career Assistant</div><div class="hero-subtitle">AI-Powered Resume Screening, Skill Gap Analysis & Job Recommendation System</div>', unsafe_allow_html=True)

    # Stat cards row
    h1, h2, h3, h4 = st.columns(4)
    with h1:
        st.markdown('<div class="stat-card"><div class="stat-number">15K+</div><div class="stat-label">Jobs in Database</div></div>', unsafe_allow_html=True)
    with h2:
        st.markdown('<div class="stat-card"><div class="stat-number">10</div><div class="stat-label">Career Categories</div></div>', unsafe_allow_html=True)
    with h3:
        st.markdown('<div class="stat-card"><div class="stat-number">30+</div><div class="stat-label">Skills Tracked</div></div>', unsafe_allow_html=True)
    with h4:
        st.markdown('<div class="stat-card"><div class="stat-number">7</div><div class="stat-label">AI Modules</div></div>', unsafe_allow_html=True)

    st.markdown('---')
    st.markdown('### 🚀 What You Can Do — Click to Get Started')

    def go_to(page_name):
        nav_list = [
            "🏠 Home", "📊 Resume Analysis", "🎯 Job Recommendations",
            "🔍 Skill Gap Analysis", "🎤 Interview Prep", "✏️ Edit Resume",
            "📝 Resume Builder", "✉️ Cover Letter", "🤖 Career Chatbot",
            "📈 Analytics", "🔎 Job Filter",
        ]
        st.session_state.nav_index = nav_list.index(page_name)
        st.rerun()

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown('<div class="glass-card"><h4>📊 Resume Analysis</h4><p>Upload your resume and get an AI-powered score breakdown with strengths, weaknesses & improvement tips.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Resume Analysis →", key="home_btn_analysis", use_container_width=True):
            go_to("📊 Resume Analysis")

        st.markdown('<div class="glass-card"><h4>🎯 Job Recommendations</h4><p>Get personalized job matches from 15K+ listings using NLP semantic similarity & FAISS search.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Job Recommendations →", key="home_btn_jobs", use_container_width=True):
            go_to("🎯 Job Recommendations")

    with f2:
        st.markdown('<div class="glass-card"><h4>🔍 Skill Gap Analysis</h4><p>Visualize your skills vs market demand with radar charts and get personalized course recommendations.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Skill Gap Analysis →", key="home_btn_gap", use_container_width=True):
            go_to("🔍 Skill Gap Analysis")

        st.markdown('<div class="glass-card"><h4>🎤 Interview Prep</h4><p>Practice with tailored interview questions for 9 professional categories with answer fields.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Interview Prep →", key="home_btn_interview", use_container_width=True):
            go_to("🎤 Interview Prep")

    with f3:
        st.markdown('<div class="glass-card"><h4>✉️ Cover Letter</h4><p>Auto-generate professional cover letters customized for any job application — download as PDF.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Cover Letter →", key="home_btn_cover", use_container_width=True):
            go_to("✉️ Cover Letter")

        st.markdown('<div class="glass-card"><h4>🤖 Career Chatbot</h4><p>Ask our AI assistant about career paths, skills, resume tips & interview strategies.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Career Chatbot →", key="home_btn_chat", use_container_width=True):
            go_to("🤖 Career Chatbot")

    st.markdown('---')
    st.markdown('### 📋 How It Works')
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown('<div class="glass-card" style="text-align:center;"><div style="font-size:32px;">📄</div><strong>Step 1</strong><p>Upload Resume (PDF)</p></div>', unsafe_allow_html=True)
        if st.button("Upload Resume →", key="home_step1", use_container_width=True):
            go_to("📊 Resume Analysis")
    with s2:
        st.markdown('<div class="glass-card" style="text-align:center;"><div style="font-size:32px;">🧠</div><strong>Step 2</strong><p>AI Analyzes & Scores</p></div>', unsafe_allow_html=True)
    with s3:
        st.markdown('<div class="glass-card" style="text-align:center;"><div style="font-size:32px;">🎯</div><strong>Step 3</strong><p>Get Job Matches</p></div>', unsafe_allow_html=True)
        if st.button("View Jobs →", key="home_step3", use_container_width=True):
            go_to("🎯 Job Recommendations")
    with s4:
        st.markdown('<div class="glass-card" style="text-align:center;"><div style="font-size:32px;">🚀</div><strong>Step 4</strong><p>Improve & Apply</p></div>', unsafe_allow_html=True)
        if st.button("Edit Resume →", key="home_step4", use_container_width=True):
            go_to("✏️ Edit Resume")

    # Footer
    st.markdown('<div class="footer">Developed with ❤️ using Python, Streamlit, FAISS, SentenceTransformers & Scikit-learn<br/>Course: Artificial Intelligence | Smart Career Assistant © 2025</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: RESUME ANALYSIS
# ═══════════════════════════════════════════════════════════════
elif nav_page == "📊 Resume Analysis":
    st.markdown('<div class="hero-title">Resume Analysis</div><div class="hero-subtitle">Upload your resume for AI-powered scoring, career prediction & improvement suggestions.</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf"], key="dash_uploader")
    if st.button("🎯 Analyze & Recommend", use_container_width=True):
        if uploaded_file:
            resume_text = extract_text_from_pdf(uploaded_file)
            st.session_state['dash_resume'] = resume_text
            st.session_state['dash_results'] = recommender.recommend_jobs(resume_text, top_n=6)
            st.session_state['dash_skills'] = extract_skills(resume_text)
            st.session_state['dash_prediction'] = predictor.predict(resume_text)
        else:
            st.warning("Please upload your resume first.")

    if 'dash_resume' in st.session_state:
        resume_text = st.session_state['dash_resume']
        job_results = st.session_state['dash_results']['recommended_jobs']
        skills = st.session_state['dash_skills']
        pred = st.session_state['dash_prediction']
        contact_info = utils.extract_contact_info(resume_text)
        scoring = utils.calculate_resume_score(resume_text, skills)
        missing_skills = utils.get_missing_skills(skills, job_results)
        career_info = utils.get_career_path_and_questions(job_results[0]['position'] if job_results else 'Analyst')

        # ── MODULE 1: Career Category Prediction ──
        st.markdown('---')
        st.markdown('### 🧠 AI Career Category Prediction')
        pr1, pr2 = st.columns([1, 2])
        with pr1:
            st.markdown(f'<div style="text-align:center;padding:16px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;"><div style="font-size:14px;color:rgba(255,255,255,0.8);">Predicted Career Path</div><div style="font-size:22px;font-weight:800;color:white;margin:6px 0;">{pred["top_category"]}</div><div style="font-size:28px;font-weight:800;color:#fbbf24;">{pred["top_confidence"]}%</div></div>', unsafe_allow_html=True)
        with pr2:
            cats = [c[0] for c in pred['all_categories'][:6]]
            vals = [c[1] for c in pred['all_categories'][:6]]
            colors = ['#667eea','#764ba2','#f093fb','#4facfe','#43e97b','#fa709a']
            fig = go.Figure(go.Bar(x=vals, y=cats, orientation='h', marker_color=colors[:len(cats)]))
            fig.update_layout(title='Career Match Confidence', xaxis_title='Confidence %', yaxis=dict(autorange='reversed'), height=280, margin=dict(l=0,r=20,t=40,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        # ── MODULE 2: Score Breakdown Dashboard ──
        st.markdown('### 📊 Resume Score Breakdown')
        resume_score = scoring['score']
        # Compute sub-scores
        skills_score = min(100, len(skills) * 12)
        exp_words = ['experience','work','employment','managed','led','built','developed']
        exp_score = min(100, sum(15 for w in exp_words if w in resume_text.lower()))
        edu_words = ['education','university','bachelor','master','degree','phd','bsc','msc']
        edu_score = min(100, sum(20 for w in edu_words if w in resume_text.lower()))
        ats_score = min(100, len(skills) * 10 + (20 if contact_info['email'] != 'Not found' else 0) + (15 if contact_info['phone'] != 'Not found' else 0))
        completeness = min(100, sum([bool(contact_info['name'] != 'Unknown Candidate')*20, bool(contact_info['email'] != 'Not found')*20, len(skills)>0 and 20, exp_score>30 and 20, edu_score>30 and 20]))
        breakdown = {'Skills Match': skills_score, 'Experience Quality': exp_score, 'Education Score': edu_score, 'ATS Compatibility': ats_score, 'Resume Completeness': completeness}

        sb1, sb2 = st.columns([1, 1])
        with sb1:
            st.metric('Overall Score', f'{resume_score}/100')
            st.progress(min(resume_score, 100))
            for label, val in breakdown.items():
                color = '#22c55e' if val >= 70 else '#f59e0b' if val >= 40 else '#ef4444'
                st.markdown(f'<div style="display:flex;justify-content:space-between;padding:4px 0;"><span>{label}</span><span style="font-weight:700;color:{color};">{val}%</span></div>', unsafe_allow_html=True)
                st.progress(min(val, 100))
        with sb2:
            # Radar chart
            labels = list(breakdown.keys())
            values = list(breakdown.values())
            fig2 = go.Figure(go.Scatterpolar(r=values + [values[0]], theta=labels + [labels[0]], fill='toself', fillcolor='rgba(102,126,234,0.25)', line_color='#667eea', name='Your Score'))
            fig2.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), showlegend=False, height=320, margin=dict(l=40,r=40,t=20,b=20), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

        # ── Strengths & Weaknesses ──
        st.markdown('### 💪 Strengths & Weaknesses')
        sw1, sw2 = st.columns(2)
        with sw1:
            for s in scoring['strengths']:
                st.markdown(f"<span style='color:green;font-weight:bold;'>{s}</span>", unsafe_allow_html=True)
        with sw2:
            for w in scoring['weaknesses']:
                st.markdown(f"<span style='color:red;font-weight:bold;'>{w}</span>", unsafe_allow_html=True)

        # ── MODULE 3: Skill Gap Analysis with Visualization ──
        st.markdown('### 🔍 Skill Gap Analysis')
        sg1, sg2 = st.columns(2)
        with sg1:
            st.markdown('**✅ Your Skills:**')
            if skills:
                tags = ''.join([f'<span class="skill-tag" style="background:#dcfce7;color:#166534;">{s}</span>' for s in skills])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.info('No skills detected')
        with sg2:
            st.markdown('**❌ Missing Skills to Learn:**')
            if missing_skills:
                tags = ''.join([f'<span class="skill-tag" style="background:#fef2f2;color:#991b1b;">{s}</span>' for s in missing_skills])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.success('No skill gaps found!')
        # Skill gap bar chart
        if skills or missing_skills:
            all_sk = [(s, 100, 'Have') for s in skills[:8]] + [(s, 0, 'Missing') for s in missing_skills[:5]]
            if all_sk:
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(x=[s[0] for s in all_sk if s[2]=='Have'], y=[100]*len([s for s in all_sk if s[2]=='Have']), name='Have', marker_color='#22c55e'))
                fig3.add_trace(go.Bar(x=[s[0] for s in all_sk if s[2]=='Missing'], y=[100]*len([s for s in all_sk if s[2]=='Missing']), name='Missing', marker_color='#ef4444'))
                fig3.update_layout(title='Skill Coverage', barmode='group', height=250, margin=dict(l=0,r=0,t=40,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig3, use_container_width=True)

        # ── MODULE 4: Course Recommendations ──
        st.markdown('### 📚 Recommended Courses')
        courses = predictor.get_courses(pred['top_category'], skills)
        if courses['missing_skill_courses']:
            for skill, course in courses['missing_skill_courses'].items():
                st.markdown(f'<div style="padding:8px 14px;margin:4px 0;background:rgba(59,130,246,0.06);border-radius:10px;border-left:3px solid #3b82f6;"><strong>📖 {skill}:</strong> {course}</div>', unsafe_allow_html=True)
        else:
            st.info('Great job! You have strong skills for this career path.')

        # ── Career Path ──
        st.markdown('### 🛤️ Suggested Career Path')
        st.info(career_info['path'])

        # ── Job Cards ──
        st.markdown('### 🎯 Top Job Recommendations')
        card_colors = ['#e8f0fe','#dbeafe','#eff6ff','#e0eafc','#d4e4fc','#f0f5ff']
        for row_idx in range(0, len(job_results), 3):
            cols = st.columns(3)
            for i, job in enumerate(job_results[row_idx:row_idx+3]):
                color = card_colors[(row_idx+i) % len(card_colors)]
                req_skills = str(job.get('requisite_skill', ''))
                skill_tags = ''
                if req_skills and req_skills != 'nan':
                    skill_tags = ''.join([f'<span class="skill-tag">{s.strip()}</span>' for s in req_skills.split(',')[:8] if s.strip()])
                with cols[i]:
                    st.markdown(f'<div class="job-card" style="background:{color};"><h3>{job["position"]}</h3><p><strong>{job.get("workplace","Company")}</strong><br/>{str(job.get("job_role_and_duties",""))[:70]}...</p><div class="match-badge">{int(job.get("match_score",85))}% Match</div></div>', unsafe_allow_html=True)
                    with st.expander('View Full Details'):
                        st.markdown(f'**Company:** {job.get("workplace","N/A")}')
                        st.markdown(f'**Work Mode:** {job.get("working_mode","N/A")}')
                        st.write(str(job.get('job_role_and_duties','No description.')))
                        if skill_tags:
                            st.markdown(f'**Required Skills:**<br/>{skill_tags}', unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════
# PAGE: JOB RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════
elif nav_page == "🎯 Job Recommendations":
    st.markdown('<div class="hero-title">Job Recommendations</div><div class="hero-subtitle">AI-matched jobs based on your resume using NLP semantic similarity.</div>', unsafe_allow_html=True)
    if 'dash_resume' not in st.session_state:
        st.info("📄 Please go to **Resume Analysis** first and upload your resume to get job recommendations.")
    else:
        job_results = st.session_state['dash_results']['recommended_jobs']
        st.markdown(f'### 🎯 Top {len(job_results)} Matches')
        card_colors = ['#e8f0fe','#dbeafe','#eff6ff','#e0eafc','#d4e4fc','#f0f5ff']
        for row_idx in range(0, len(job_results), 3):
            cols = st.columns(3)
            for i, job in enumerate(job_results[row_idx:row_idx+3]):
                color = card_colors[(row_idx+i) % len(card_colors)]
                req_skills = str(job.get('requisite_skill', ''))
                skill_tags = ''
                if req_skills and req_skills != 'nan':
                    skill_tags = ''.join([f'<span class="skill-tag">{s.strip()}</span>' for s in req_skills.split(',')[:8] if s.strip()])
                with cols[i]:
                    st.markdown(f'<div class="job-card"><h3>{job["position"]}</h3><p><strong>{job.get("workplace","Company")}</strong><br/>{str(job.get("job_role_and_duties",""))[:80]}...</p><div class="match-badge">{int(job.get("match_score",85))}% Match</div></div>', unsafe_allow_html=True)
                    with st.expander('View Full Details'):
                        st.markdown(f'**Company:** {job.get("workplace","N/A")}')
                        st.markdown(f'**Work Mode:** {job.get("working_mode","N/A")}')
                        st.write(str(job.get('job_role_and_duties','No description.')))
                        if skill_tags:
                            st.markdown(f'**Required Skills:**<br/>{skill_tags}', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: SKILL GAP ANALYSIS
# ═══════════════════════════════════════════════════════════════
elif nav_page == "🔍 Skill Gap Analysis":
    st.markdown('<div class="hero-title">Skill Gap Analysis</div><div class="hero-subtitle">Identify missing skills and get personalized course recommendations.</div>', unsafe_allow_html=True)
    if 'dash_resume' not in st.session_state:
        st.info("📄 Please go to **Resume Analysis** first and upload your resume.")
    else:
        skills = st.session_state['dash_skills']
        job_results = st.session_state['dash_results']['recommended_jobs']
        pred = st.session_state['dash_prediction']
        missing_skills = utils.get_missing_skills(skills, job_results)

        sg1, sg2 = st.columns(2)
        with sg1:
            st.markdown('### ✅ Your Skills')
            if skills:
                tags = ''.join([f'<span class="skill-tag skill-have">{s}</span>' for s in skills])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.info('No skills detected')
        with sg2:
            st.markdown('### ❌ Missing Skills')
            if missing_skills:
                tags = ''.join([f'<span class="skill-tag skill-missing">{s}</span>' for s in missing_skills])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.success('No skill gaps!')

        # Radar chart
        if skills:
            skills_score = min(100, len(skills) * 12)
            resume_text = st.session_state['dash_resume']
            exp_words = ['experience','work','managed','led','built','developed']
            exp_score = min(100, sum(15 for w in exp_words if w in resume_text.lower()))
            edu_words = ['education','university','bachelor','master','degree']
            edu_score = min(100, sum(20 for w in edu_words if w in resume_text.lower()))
            contact = utils.extract_contact_info(resume_text)
            ats_score = min(100, len(skills)*10 + (20 if contact['email']!='Not found' else 0))
            labels = ['Skills','Experience','Education','ATS','Completeness']
            values = [skills_score, exp_score, edu_score, ats_score, min(100, skills_score//2+exp_score//2+20)]
            fig = go.Figure(go.Scatterpolar(r=values+[values[0]], theta=labels+[labels[0]], fill='toself', fillcolor='rgba(102,126,234,0.25)', line_color='#6366f1'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), showlegend=False, height=350, margin=dict(l=40,r=40,t=20,b=20), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#334155'))
            st.plotly_chart(fig, use_container_width=True)

        # Course recommendations
        st.markdown('### 📚 Recommended Courses')
        courses = predictor.get_courses(pred['top_category'], skills)
        if courses['missing_skill_courses']:
            for skill, course in courses['missing_skill_courses'].items():
                st.markdown(f'<div class="course-card"><strong>📖 {skill}:</strong> {course}</div>', unsafe_allow_html=True)
        else:
            st.success('You have strong skills for this career path!')


# ═══════════════════════════════════════════════════════════════
# PAGE: RESUME BUILDER (from scratch)
# ═══════════════════════════════════════════════════════════════
elif nav_page == "📝 Resume Builder":
    st.markdown('<div class="hero-title">Resume Builder</div><div class="hero-subtitle">Build a professional resume from scratch and download as PDF.</div>', unsafe_allow_html=True)

    st.markdown('<div class="rb-section"><h3>👤 Personal Information</h3>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        rb_name = st.text_input("Full Name *", key="rb_name", placeholder="John Doe")
        rb_email = st.text_input("Email *", key="rb_email", placeholder="john@email.com")
        rb_phone = st.text_input("Phone", key="rb_phone", placeholder="+1 234-567-8900")
    with b2:
        rb_loc = st.text_input("Location", key="rb_loc", placeholder="New York, NY")
        rb_li = st.text_input("LinkedIn", key="rb_li", placeholder="linkedin.com/in/johndoe")
        rb_web = st.text_input("Website", key="rb_web", placeholder="johndoe.com")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="rb-section"><h3>💡 Professional Summary</h3>', unsafe_allow_html=True)
    rb_summary = st.text_area("Write a 2-4 sentence summary", key="rb_sum", height=80, placeholder="Experienced software engineer with 5+ years...")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="rb-section"><h3>🛠️ Skills</h3>', unsafe_allow_html=True)
    rb_skills = st.text_input("Skills (comma-separated)", key="rb_skills", placeholder="Python, React, AWS, SQL, Docker")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="rb-section"><h3>💼 Experience</h3>', unsafe_allow_html=True)
    rb_exp = st.text_area("Work experience (separate entries with blank lines)", key="rb_exp", height=120, placeholder="Software Engineer at Google (2020-2023)\nBuilt scalable APIs serving 1M+ users")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="rb-section"><h3>🎓 Education</h3>', unsafe_allow_html=True)
    rb_edu = st.text_area("Education", key="rb_edu", height=80, placeholder="B.Sc. Computer Science, MIT (2016-2020)")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("📄 Generate Resume PDF", use_container_width=True, key="rb_gen"):
        if rb_name:
            resume_data = {
                'name': rb_name, 'email': rb_email, 'phone': rb_phone,
                'location': rb_loc, 'linkedin': rb_li, 'website': rb_web,
                'summary': rb_summary, 'skills': rb_skills,
                'experience': [{'title': rb_exp, 'company': '', 'dates': '', 'description': ''}] if rb_exp else None,
                'education': [{'degree': rb_edu, 'institution': '', 'dates': '', 'details': ''}] if rb_edu else None,
            }
            try:
                pdf_bytes = generate_pdf(resume_data)
                st.session_state['rb_pdf'] = pdf_bytes
                st.success("✅ Resume generated!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter your name.")

    if 'rb_pdf' in st.session_state:
        st.download_button("⬇️ Download Resume PDF", data=st.session_state['rb_pdf'], file_name=f"{rb_name or 'resume'}_Resume.pdf", mime="application/pdf", use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: INTERVIEW PREP QUESTIONS
# ═══════════════════════════════════════════════════════════════
elif nav_page == "🎤 Interview Prep":
    st.markdown("""
    <div class="hero-title">🎤 Interview Prep Questions</div>
    <div class="hero-subtitle">Select a job category to get tailored interview preparation questions.</div>
    """, unsafe_allow_html=True)

    category = st.selectbox("Choose a job category:", [
        "Software Engineering", "Data Science / Analytics",
        "Marketing / Sales", "Finance", "Healthcare",
        "Education", "HR / Talent", "Product & Design", "General"
    ])

    if "show_questions" not in st.session_state:
        st.session_state.show_questions = False

    if st.button("📝 Generate Questions", use_container_width=True):
        st.session_state.show_questions = True

    if st.session_state.show_questions:
        questions_map = {
            "Software Engineering": [
                "1. Explain the SOLID principles of OOP.",
                "2. What is the difference between a REST API and GraphQL?",
                "3. How would you optimize a slow database query?",
                "4. Describe your experience with CI/CD pipelines.",
                "5. How do you handle merge conflicts in Git?",
            ],
            "Data Science / Analytics": [
                "1. Explain the difference between supervised and unsupervised learning.",
                "2. How do you handle missing values in a dataset?",
                "3. Write a SQL query to find the second highest salary.",
                "4. What is cross-validation and why is it important?",
                "5. Explain the bias-variance tradeoff.",
            ],
            "Marketing / Sales": [
                "1. How do you measure the ROI of a marketing campaign?",
                "2. Describe a successful campaign you led.",
                "3. How do you approach market segmentation?",
                "4. What tools do you use for analytics?",
                "5. How do you handle a declining sales pipeline?",
            ],
            "Finance": [
                "1. Walk me through a DCF analysis.",
                "2. What is the difference between NPV and IRR?",
                "3. How do you assess credit risk?",
                "4. Explain the three financial statements.",
                "5. How would you value a company with no revenue?",
            ],
            "Healthcare": [
                "1. How do you ensure patient data privacy (HIPAA)?",
                "2. Describe your experience with EHR systems.",
                "3. How do you stay current with medical regulations?",
                "4. Explain a challenging patient case you managed.",
                "5. How do you handle high-pressure clinical situations?",
            ],
            "Education": [
                "1. How do you differentiate instruction for diverse learners?",
                "2. Describe your classroom management strategy.",
                "3. How do you integrate technology in teaching?",
                "4. How do you measure student outcomes?",
                "5. How do you handle a difficult parent meeting?",
            ],
            "HR / Talent": [
                "1. How do you source candidates for hard-to-fill roles?",
                "2. Describe your approach to employee retention.",
                "3. How do you handle workplace conflict?",
                "4. What ATS systems have you used?",
                "5. How do you ensure diversity in hiring?",
            ],
            "Product & Design": [
                "1. Walk me through your design process.",
                "2. How do you prioritize features in a product roadmap?",
                "3. Describe a time you used data to inform a design decision.",
                "4. How do you handle stakeholder disagreements?",
                "5. What metrics do you track for product success?",
            ],
            "General": [
                "1. Tell me about yourself.",
                "2. What are your greatest professional strengths?",
                "3. Describe a challenge you faced and how you overcame it.",
                "4. Where do you see yourself in 5 years?",
                "5. Why should we hire you?",
            ],
        }
        qs = questions_map.get(category, questions_map["General"])
        st.markdown(f'<div class="rb-section"><h3>📋 {category} Interview Questions</h3>', unsafe_allow_html=True)
        user_answers = {}
        for q in qs:
            st.markdown(f"**{q}**")
            ans_key = f"ans_{category}_{q[:20]}"
            user_ans = st.text_area(f"Your answer for Q{q[0]}", height=60, key=ans_key, placeholder="Type your practice answer here...")
            user_answers[q] = user_ans
            st.markdown("<hr style='margin:16px 0; border-color:#e2e8f0;'>", unsafe_allow_html=True)
            
        if st.button("🚀 Evaluate All Answers", use_container_width=True, type="primary"):
            st.markdown("### 📊 Evaluation Results")
            total_score = 0
            answered_count = 0
            
            for q, ans in user_answers.items():
                ideal_explanation = utils.get_ideal_answer_explanation(q)
                
                if ans.strip():
                    answered_count += 1
                    evaluation = utils.evaluate_interview_answer(q, ans)
                    total_score += evaluation['score']
                    feedback_html = "<br>".join([f"{f}" for f in evaluation["feedback"]])
                    
                    st.markdown(f"""
                    <div style="padding:16px; border-left:4px solid {evaluation['color']}; background:#ffffff; margin-bottom:16px; border-radius:12px; font-size:14px; border:1px solid #e2e8f0; box-shadow:0 2px 4px rgba(0,0,0,0.02);">
                        <div style="font-weight:800; color:#0f172a; margin-bottom:8px; font-size:16px;">{q}</div>
                        <div style="color:#475569; margin-bottom:12px; font-style:italic; padding:8px; background:#f8fafc; border-radius:8px;"><strong>Your Answer:</strong> {ans}</div>
                        <div style="font-weight:700; color:{evaluation['color']}; margin-bottom:8px;">Score: {evaluation['score']}/100</div>
                        <div style="color:#334155; line-height:1.6; margin-bottom:16px;">{feedback_html}</div>
                        <div style="padding:12px; background:#eff6ff; border-radius:8px; color:#1e3a8a; border-left:3px solid #3b82f6;">{ideal_explanation}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="padding:16px; border-left:4px solid #94a3b8; background:#ffffff; margin-bottom:16px; border-radius:12px; font-size:14px; border:1px solid #e2e8f0;">
                        <div style="font-weight:800; color:#0f172a; margin-bottom:8px; font-size:16px;">{q}</div>
                        <div style="color:#ef4444; margin-bottom:16px;">❌ No answer provided.</div>
                        <div style="padding:12px; background:#eff6ff; border-radius:8px; color:#1e3a8a; border-left:3px solid #3b82f6;">{ideal_explanation}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if answered_count > 0:
                avg_score = total_score // answered_count
                color = "#22c55e" if avg_score >= 80 else "#3b82f6" if avg_score >= 60 else "#f59e0b"
                st.markdown(f"""
                <div style="text-align:center; padding:24px; background:linear-gradient(135deg, #eff6ff, #dbeafe); border-radius:16px; border:1px solid #bfdbfe; margin-top:24px; box-shadow:0 4px 12px rgba(37,99,235,0.08);">
                    <div style="font-size:16px; color:#1e3a8a; font-weight:700; text-transform:uppercase; letter-spacing:1px;">Overall Performance</div>
                    <div style="font-size:48px; font-weight:800; color:{color}; margin:8px 0;">{avg_score}%</div>
                    <div style="font-size:15px; color:#1e40af; font-weight:500;">You answered {answered_count} out of {len(qs)} questions.</div>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: EDIT RESUME
# ═══════════════════════════════════════════════════════════════
elif nav_page == "✏️ Edit Resume":
    st.markdown("""
    <div class="hero-title">✏️ AI Resume Editor</div>
    <div class="hero-subtitle">Upload your existing resume and our AI will parse it into editable sections. Edit, improve, and download your polished resume.</div>
    """, unsafe_allow_html=True)

    # Initialize edit session state
    if 'edit_parsed' not in st.session_state:
        st.session_state.edit_parsed = None
    if 'edit_exp_count' not in st.session_state:
        st.session_state.edit_exp_count = 1
    if 'edit_edu_count' not in st.session_state:
        st.session_state.edit_edu_count = 1
    if 'edit_proj_count' not in st.session_state:
        st.session_state.edit_proj_count = 1

    # ── Step 1: Upload ──
    st.markdown('<div class="rb-section"><h3><span class="rb-icon">📄</span>Step 1: Upload Your Resume</h3>', unsafe_allow_html=True)
    edit_file = st.file_uploader("Upload your resume PDF to get started", type=["pdf"], key="edit_uploader")

    if st.button("🤖 Parse Resume with AI", key="parse_btn", use_container_width=True):
        if edit_file:
            with st.spinner("AI is analyzing your resume..."):
                raw_text = extract_text_from_pdf(edit_file)
                parsed = utils.parse_resume_sections(raw_text)
                st.session_state.edit_parsed = parsed
                st.session_state.edit_raw_text = raw_text
                st.session_state.edit_exp_count = max(len(parsed.get('experience', [])), 1)
                st.session_state.edit_edu_count = max(len(parsed.get('education', [])), 1)
                st.session_state.edit_proj_count = max(len(parsed.get('projects', [])), 1)
            st.success("✅ Resume parsed successfully! Edit the sections below.")
        else:
            st.warning("Please upload a PDF file first.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── AI Analysis Panel (shown after parsing) ──
    if st.session_state.edit_parsed is not None and 'edit_raw_text' in st.session_state:
        p = st.session_state.edit_parsed
        analysis = utils.analyze_resume(st.session_state.edit_raw_text, p)

        st.markdown(f"""
        <div class="rb-section" style="border-left:4px solid {analysis['grade_color']};">
            <h3><span class="rb-icon">🔍</span>AI Resume Analysis</h3>
        """, unsafe_allow_html=True)

        # Score row
        sc1, sc2, sc3 = st.columns([1, 1, 2])
        with sc1:
            st.metric("Resume Score", f"{analysis['score']}/100")
            st.progress(min(analysis['score'], 100))
        with sc2:
            st.markdown(f"""
            <div style="text-align:center;padding:10px;">
                <div style="font-size:48px;font-weight:800;color:{analysis['grade_color']};">{analysis['grade']}</div>
                <div style="font-size:13px;color:#64748b;font-weight:600;">Grade</div>
            </div>
            """, unsafe_allow_html=True)
        with sc3:
            st.markdown(f"""
            <div style="padding:14px 18px;background:rgba(29,78,216,0.04);border-radius:12px;border:1px solid rgba(29,78,216,0.1);">
                <div style="font-size:14px;font-weight:600;color:#0f172a;margin-bottom:4px;">{analysis['grade_msg']}</div>
                <div style="font-size:12px;color:#64748b;">Word count: {analysis['word_count']} words</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Strengths & Weaknesses side by side
        sw1, sw2 = st.columns(2)
        with sw1:
            st.markdown("**💪 Strengths**")
            for s in analysis['strengths']:
                st.markdown(f"<div style='padding:4px 0;font-size:13px;color:#15803d;'>{s}</div>", unsafe_allow_html=True)
            if not analysis['strengths']:
                st.markdown("<div style='color:#94a3b8;font-size:13px;'>No major strengths detected yet</div>", unsafe_allow_html=True)
        with sw2:
            st.markdown("**⚠️ Weaknesses**")
            for w in analysis['weaknesses']:
                st.markdown(f"<div style='padding:4px 0;font-size:13px;color:#dc2626;'>{w}</div>", unsafe_allow_html=True)
            if not analysis['weaknesses']:
                st.markdown("<div style='color:#94a3b8;font-size:13px;'>No weaknesses found — great job!</div>", unsafe_allow_html=True)

        # Improvement Suggestions
        if analysis['suggestions']:
            st.markdown("---")
            st.markdown("**🚀 Improvement Suggestions**")
            for idx, sug in enumerate(analysis['suggestions'], 1):
                st.markdown(f"""
                <div style="padding:8px 14px;margin:6px 0;background:rgba(59,130,246,0.05);border-radius:10px;border-left:3px solid #3b82f6;font-size:13px;color:#1e293b;">
                    {sug}
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 2: Edit (only shown after parsing) ──
    if st.session_state.edit_parsed is not None:
        p = st.session_state.edit_parsed

        st.markdown('<div class="rb-section"><h3><span class="rb-icon">👤</span>Step 2: Edit Your Details</h3>', unsafe_allow_html=True)
        st.markdown("**Personal Information**")
        ep1, ep2 = st.columns(2)
        with ep1:
            ed_name = st.text_input("Full Name", value=p.get('name', ''), key="ed_name")
            ed_email = st.text_input("Email", value=p.get('email', ''), key="ed_email")
            ed_phone = st.text_input("Phone", value=p.get('phone', ''), key="ed_phone")
        with ep2:
            ed_location = st.text_input("Location", value=p.get('location', ''), key="ed_location")
            ed_linkedin = st.text_input("LinkedIn", value=p.get('linkedin', ''), key="ed_linkedin")
            ed_website = st.text_input("Website", value=p.get('website', ''), key="ed_website")
        st.markdown('</div>', unsafe_allow_html=True)

        # Summary
        st.markdown('<div class="rb-section"><h3><span class="rb-icon">💡</span>Professional Summary</h3>', unsafe_allow_html=True)
        ed_summary = st.text_area("Edit your summary", value=p.get('summary', ''), height=100, key="ed_summary")
        st.markdown('</div>', unsafe_allow_html=True)

        # Experience
        st.markdown('<div class="rb-section"><h3><span class="rb-icon">💼</span>Work Experience</h3>', unsafe_allow_html=True)
        edit_exp_entries = []
        for idx in range(st.session_state.edit_exp_count):
            st.markdown(f"**Experience #{idx+1}**")
            existing = p.get('experience', [])
            ex = existing[idx] if idx < len(existing) else {}
            xe1, xe2 = st.columns(2)
            with xe1:
                et = st.text_input("Job Title", value=ex.get('title', ''), key=f"ed_exp_title_{idx}")
                ec = st.text_input("Company", value=ex.get('company', ''), key=f"ed_exp_comp_{idx}")
            with xe2:
                ed = st.text_input("Duration", value=ex.get('dates', ''), key=f"ed_exp_dates_{idx}")
            edesc = st.text_area("Responsibilities", value=ex.get('description', ''), height=80, key=f"ed_exp_desc_{idx}")
            if et:
                edit_exp_entries.append({'title': et, 'company': ec, 'dates': ed, 'description': edesc})
            if idx < st.session_state.edit_exp_count - 1:
                st.markdown("---")
        if st.button("➕ Add Experience", key="ed_add_exp"):
            st.session_state.edit_exp_count += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Education
        st.markdown('<div class="rb-section"><h3><span class="rb-icon">🎓</span>Education</h3>', unsafe_allow_html=True)
        edit_edu_entries = []
        for idx in range(st.session_state.edit_edu_count):
            st.markdown(f"**Education #{idx+1}**")
            existing = p.get('education', [])
            edu = existing[idx] if idx < len(existing) else {}
            eu1, eu2 = st.columns(2)
            with eu1:
                edeg = st.text_input("Degree", value=edu.get('degree', ''), key=f"ed_edu_deg_{idx}")
                einst = st.text_input("Institution", value=edu.get('institution', ''), key=f"ed_edu_inst_{idx}")
            with eu2:
                edates = st.text_input("Years", value=edu.get('dates', ''), key=f"ed_edu_dates_{idx}")
                edet = st.text_input("GPA/Honors", value=edu.get('details', ''), key=f"ed_edu_det_{idx}")
            if edeg:
                edit_edu_entries.append({'degree': edeg, 'institution': einst, 'dates': edates, 'details': edet})
            if idx < st.session_state.edit_edu_count - 1:
                st.markdown("---")
        if st.button("➕ Add Education", key="ed_add_edu"):
            st.session_state.edit_edu_count += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Skills
        st.markdown('<div class="rb-section"><h3><span class="rb-icon">🛠️</span>Skills</h3>', unsafe_allow_html=True)
        esk1, esk2 = st.columns(2)
        with esk1:
            ed_tech = st.text_area("Technical Skills", value=p.get('skills_technical', ''), height=80, key="ed_tech")
        with esk2:
            ed_soft = st.text_area("Soft Skills", value=p.get('skills_soft', ''), height=80, key="ed_soft")
        ed_all_skills = ""
        skill_parts = []
        if ed_tech:
            skill_parts.append(f"Technical: {ed_tech}")
        if ed_soft:
            skill_parts.append(f"Soft Skills: {ed_soft}")
        ed_all_skills = "  |  ".join(skill_parts)
        st.markdown('</div>', unsafe_allow_html=True)

        # Certifications
        st.markdown('<div class="rb-section"><h3><span class="rb-icon">🏅</span>Certifications</h3>', unsafe_allow_html=True)
        ed_certs = st.text_area("Certifications (one per line)", value=p.get('certifications', ''), height=80, key="ed_certs")
        st.markdown('</div>', unsafe_allow_html=True)

        # Projects
        st.markdown('<div class="rb-section"><h3><span class="rb-icon">🚀</span>Projects</h3>', unsafe_allow_html=True)
        edit_proj_entries = []
        for idx in range(st.session_state.edit_proj_count):
            st.markdown(f"**Project #{idx+1}**")
            existing = p.get('projects', [])
            proj = existing[idx] if idx < len(existing) else {}
            pp1, pp2 = st.columns(2)
            with pp1:
                pname = st.text_input("Project Name", value=proj.get('name', ''), key=f"ed_proj_name_{idx}")
            with pp2:
                ptech = st.text_input("Technologies", value=proj.get('technologies', ''), key=f"ed_proj_tech_{idx}")
            pdesc = st.text_area("Description", value=proj.get('description', ''), height=60, key=f"ed_proj_desc_{idx}")
            if pname:
                edit_proj_entries.append({'name': pname, 'technologies': ptech, 'description': pdesc})
            if idx < st.session_state.edit_proj_count - 1:
                st.markdown("---")
        if st.button("➕ Add Project", key="ed_add_proj"):
            st.session_state.edit_proj_count += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Languages & References
        st.markdown('<div class="rb-section"><h3><span class="rb-icon">🌍</span>Languages & References</h3>', unsafe_allow_html=True)
        elr1, elr2 = st.columns(2)
        with elr1:
            ed_langs = st.text_input("Languages", value=p.get('languages', ''), key="ed_langs")
        with elr2:
            ed_refs = st.text_input("References", value=p.get('references', ''), key="ed_refs")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Step 3: Generate & Download ──
        st.markdown('<div class="rb-section"><h3><span class="rb-icon">📥</span>Step 3: Save & Download</h3>', unsafe_allow_html=True)
        if st.button("📄 Generate Updated Resume PDF", key="ed_gen_pdf", use_container_width=True):
            if not ed_name:
                st.error("Please enter your name.")
            else:
                cert_list = [c.strip() for c in ed_certs.strip().split('\n') if c.strip()] if ed_certs else []
                lang_list = [l.strip() for l in ed_langs.split(',') if l.strip()] if ed_langs else []
                resume_data = {
                    'name': ed_name, 'email': ed_email, 'phone': ed_phone,
                    'location': ed_location, 'linkedin': ed_linkedin, 'website': ed_website,
                    'summary': ed_summary,
                    'experience': edit_exp_entries if edit_exp_entries else None,
                    'education': edit_edu_entries if edit_edu_entries else None,
                    'skills': ed_all_skills if ed_all_skills else None,
                    'certifications': cert_list if cert_list else None,
                    'projects': edit_proj_entries if edit_proj_entries else None,
                    'languages': lang_list if lang_list else None,
                    'references': ed_refs if ed_refs else None,
                }
                try:
                    pdf_bytes = generate_pdf(resume_data)
                    st.session_state['edit_pdf_bytes'] = pdf_bytes
                    st.session_state['edit_pdf_filename'] = f"{ed_name.replace(' ', '_')}_Edited_Resume.pdf"
                    st.success("✅ Resume generated! Click download below.")
                except Exception as e:
                    st.error(f"Error: {e}")

        if 'edit_pdf_bytes' in st.session_state and st.session_state['edit_pdf_bytes']:
            st.download_button(
                label="⬇️ Download Edited Resume PDF",
                data=st.session_state['edit_pdf_bytes'],
                file_name=st.session_state.get('edit_pdf_filename', 'Resume.pdf'),
                mime="application/pdf",
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: FILTER (job search/filter)
# ═══════════════════════════════════════════════════════════════
elif nav_page == "🔎 Job Filter":
    st.markdown("""
    <div class="hero-title">🔍 Filter Jobs</div>
    <div class="hero-subtitle">Search and filter through our database of 15,000+ job listings.</div>
    """, unsafe_allow_html=True)

    df = pd.read_csv("JobsFE.csv")

    st.markdown('<div class="rb-section"><h3><span class="rb-icon">🎛️</span>Filter Options</h3>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        search_keyword = st.text_input("🔎 Search by keyword", placeholder="e.g. Python, Manager, Designer")
    with fc2:
        locations = ["All"] + sorted(df['workplace'].dropna().unique().tolist())
        selected_location = st.selectbox("📍 Location", locations)
    with fc3:
        modes = ["All"] + sorted(df['working_mode'].dropna().unique().tolist())
        selected_mode = st.selectbox("🏢 Work Mode", modes)
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply filters
    filtered = df.copy()
    if search_keyword:
        mask = filtered.apply(lambda row: search_keyword.lower() in str(row).lower(), axis=1)
        filtered = filtered[mask]
    if selected_location != "All":
        filtered = filtered[filtered['workplace'] == selected_location]
    if selected_mode != "All":
        filtered = filtered[filtered['working_mode'] == selected_mode]

    st.markdown(f"**Showing {len(filtered)} jobs**")

    # Display results
    for row_idx in range(0, min(len(filtered), 12), 3):
        cols = st.columns(3)
        for i in range(3):
            if row_idx + i < len(filtered):
                job = filtered.iloc[row_idx + i]
                color = ["#e8f0fe", "#dbeafe", "#eff6ff"][i]
                with cols[i]:
                    st.markdown(f"""
                    <div class="job-card" style="background:{color};">
                        <h3>{job['position']}</h3>
                        <p><strong>{job.get('workplace', 'N/A')}</strong><br/>{str(job.get('job_role_and_duties', ''))[:70]}...</p>
                        <div class="match-badge">{job.get('working_mode', 'N/A')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("View Details"):
                        st.markdown(f"**Company:** {job.get('workplace', 'N/A')}")
                        st.markdown(f"**Work Mode:** {job.get('working_mode', 'N/A')}")
                        st.markdown(f"**Salary:** {job.get('salary', 'N/A')}")
                        st.write(str(job.get('job_role_and_duties', 'No description.')))
                        req = str(job.get('requisite_skill', ''))
                        if req and req != 'nan':
                            tags = ''.join([f'<span class="skill-tag">{s.strip()}</span>' for s in req.split(',')[:8] if s.strip()])
                            st.markdown(f'**Skills:** {tags}', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ═══════════════════════════════════════════════════════════════
elif nav_page == "📈 Analytics":
    st.markdown('<div class="hero-title">📈 Analytics Dashboard</div><div class="hero-subtitle">Visual insights from our job database of 15,000+ listings.</div>', unsafe_allow_html=True)
    df = pd.read_csv("JobsFE.csv")

    a1, a2 = st.columns(2)
    with a1:
        # Jobs by work mode pie chart
        mode_counts = df['working_mode'].value_counts().head(6)
        fig_pie = go.Figure(go.Pie(labels=mode_counts.index, values=mode_counts.values, hole=0.4, marker_colors=['#667eea','#764ba2','#f093fb','#4facfe','#43e97b','#fa709a']))
        fig_pie.update_layout(title='Jobs by Work Mode', height=350, margin=dict(l=20,r=20,t=50,b=20), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#334155'))
        st.plotly_chart(fig_pie, use_container_width=True)

    with a2:
        # Top positions bar chart
        pos_counts = df['position'].value_counts().head(10)
        fig_bar = go.Figure(go.Bar(x=pos_counts.values, y=pos_counts.index, orientation='h', marker_color='#667eea'))
        fig_bar.update_layout(title='Top 10 Job Positions', yaxis=dict(autorange='reversed'), height=350, margin=dict(l=0,r=20,t=50,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#334155'))
        st.plotly_chart(fig_bar, use_container_width=True)

    a3, a4 = st.columns(2)
    with a3:
        # Top companies
        comp_counts = df['workplace'].value_counts().head(10)
        fig_comp = go.Figure(go.Bar(y=comp_counts.index, x=comp_counts.values, orientation='h', marker_color='#43e97b'))
        fig_comp.update_layout(title='Top 10 Employers', yaxis=dict(autorange='reversed'), height=350, margin=dict(l=0,r=20,t=50,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#334155'))
        st.plotly_chart(fig_comp, use_container_width=True)

    with a4:
        # Most in-demand skills
        all_skills_text = ' '.join(df['requisite_skill'].dropna().astype(str).tolist())
        skill_list = [s.strip() for s in all_skills_text.replace(';', ',').split(',') if s.strip() and len(s.strip()) > 1]
        skill_series = pd.Series(skill_list).value_counts().head(12)
        fig_sk = go.Figure(go.Bar(x=skill_series.values, y=skill_series.index, orientation='h', marker_color='#f093fb'))
        fig_sk.update_layout(title='Most In-Demand Skills', yaxis=dict(autorange='reversed'), height=350, margin=dict(l=0,r=20,t=50,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#334155'))
        st.plotly_chart(fig_sk, use_container_width=True)

    # Key metrics
    st.markdown('### 📊 Key Metrics')
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Jobs", f"{len(df):,}")
    m2.metric("Companies", f"{df['workplace'].nunique():,}")
    m3.metric("Positions", f"{df['position'].nunique():,}")
    m4.metric("Work Modes", f"{df['working_mode'].nunique()}")


# ═══════════════════════════════════════════════════════════════
# PAGE: COVER LETTER
# ═══════════════════════════════════════════════════════════════
elif nav_page == "✉️ Cover Letter":
    st.markdown('<div class="hero-title">✉️ Cover Letter Generator</div><div class="hero-subtitle">Generate a professional cover letter tailored to any job in seconds.</div>', unsafe_allow_html=True)

    st.markdown('<div class="rb-section"><h3><span class="rb-icon">📝</span>Fill in Your Details</h3>', unsafe_allow_html=True)
    cl1, cl2 = st.columns(2)
    with cl1:
        cl_name = st.text_input("Your Full Name *", placeholder="e.g. John Doe", key="cl_name")
        cl_email = st.text_input("Your Email *", placeholder="e.g. john@email.com", key="cl_email")
        cl_phone = st.text_input("Your Phone", placeholder="e.g. +1 234-567-8900", key="cl_phone")
    with cl2:
        cl_job = st.text_input("Target Job Title *", placeholder="e.g. Software Engineer", key="cl_job")
        cl_company = st.text_input("Target Company *", placeholder="e.g. Google", key="cl_company")
    cl_skills = st.text_input("Your Key Skills (comma-separated)", placeholder="e.g. Python, React, Machine Learning, AWS", key="cl_skills")
    cl_exp = st.text_area("Brief Experience Summary", placeholder="e.g. 3+ years of full-stack development experience building scalable web apps", height=80, key="cl_exp")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✉️ Generate Cover Letter", use_container_width=True, key="cl_gen"):
        if cl_name and cl_job and cl_company:
            skills_list = [s.strip() for s in cl_skills.split(',') if s.strip()] if cl_skills else []
            pdf = generate_cover_letter_pdf(cl_name, cl_email or "", cl_phone or "", cl_job, cl_company, skills_list, cl_exp or "")
            st.session_state['cl_pdf'] = pdf
            st.session_state['cl_fname'] = f"{cl_name.replace(' ', '_')}_Cover_Letter.pdf"
            st.success("✅ Cover letter generated!")
        else:
            st.warning("Please fill in name, job title, and company.")

    if 'cl_pdf' in st.session_state and st.session_state['cl_pdf']:
        st.download_button("⬇️ Download Cover Letter PDF", data=st.session_state['cl_pdf'], file_name=st.session_state.get('cl_fname', 'Cover_Letter.pdf'), mime="application/pdf", use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: CAREER CHATBOT
# ═══════════════════════════════════════════════════════════════
elif nav_page == "🤖 Career Chatbot":
    st.markdown('<div class="hero-title">🤖 Career Assistant Chatbot</div><div class="hero-subtitle">Ask me anything about your career, resume, skills, or job search!</div>', unsafe_allow_html=True)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "Hello! 👋 I'm your Career Assistant. Ask me anything about:\n- Resume improvement tips\n- Skills for specific roles\n- Interview preparation\n- Career path advice\n\nWhat would you like to know?"}]

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask me about your career...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Rule-based chatbot responses
        q = user_input.lower()
        if any(w in q for w in ['resume', 'cv', 'improve resume']):
            reply = """📝 **Resume Improvement Tips:**
1. **Use action verbs** — Led, Built, Designed, Improved, Automated
2. **Quantify achievements** — "Increased sales by 25%" not "Improved sales"
3. **Add a professional summary** — 2-4 sentences at the top
4. **Include relevant skills** — Match keywords from job descriptions
5. **Keep it concise** — 1-2 pages maximum
6. **Add LinkedIn URL** — 87% of recruiters check LinkedIn
7. **List projects** — Show practical abilities with tech stacks
8. **Include certifications** — AWS, Google, Coursera certificates stand out"""
        elif any(w in q for w in ['data scientist', 'data science', 'data analyst']):
            reply = """📊 **Skills Needed for Data Science:**
- **Must have:** Python, SQL, Statistics, Pandas, NumPy
- **Machine Learning:** Scikit-learn, TensorFlow/PyTorch
- **Visualization:** Tableau, Power BI, Matplotlib
- **Big Data:** Spark, Hadoop (for senior roles)
- **Career Path:** Junior Analyst → Data Analyst → Senior Analyst → Data Scientist → Lead/Manager"""
        elif any(w in q for w in ['software engineer', 'developer', 'web developer', 'programming']):
            reply = """💻 **Skills for Software Engineering:**
- **Languages:** Python, JavaScript, Java, TypeScript
- **Frontend:** React, Angular, Vue.js, Next.js
- **Backend:** Node.js, Django, Flask, Spring Boot
- **DevOps:** Docker, Kubernetes, CI/CD, AWS/Azure
- **Career Path:** Junior Dev → Software Engineer → Senior Engineer → Tech Lead → CTO"""
        elif any(w in q for w in ['interview', 'prepare', 'question']):
            reply = """🎤 **Interview Preparation Tips:**
1. **Research the company** — Know their mission, products, culture
2. **Practice STAR method** — Situation, Task, Action, Result
3. **Prepare technical questions** — Use our Interview Prep page!
4. **Have questions ready** — Ask about team, growth, challenges
5. **Mock interviews** — Practice with a friend or online tools
6. **Review your resume** — Be ready to discuss every item"""
        elif any(w in q for w in ['ai', 'machine learning', 'ml engineer', 'artificial intelligence']):
            reply = """🧠 **Skills for AI/ML Engineering:**
- **Core:** Python, Linear Algebra, Probability, Statistics
- **ML Frameworks:** TensorFlow, PyTorch, Scikit-learn
- **Specializations:** NLP, Computer Vision, Reinforcement Learning
- **MLOps:** MLflow, Kubeflow, Docker, Model Deployment
- **Trending:** LLMs, Transformers, RAG, Fine-tuning"""
        elif any(w in q for w in ['skill', 'learn', 'course', 'certification']):
            reply = """📚 **Top Skills to Learn in 2025:**
1. **AI/ML** — Most in-demand across industries
2. **Cloud (AWS/Azure/GCP)** — Every company needs cloud skills
3. **Python** — Universal language for tech roles
4. **SQL** — Essential for any data role
5. **Docker/Kubernetes** — Modern deployment standard

🎓 **Recommended Platforms:** Coursera, Udemy, DataCamp, freeCodeCamp"""
        elif any(w in q for w in ['salary', 'pay', 'compensation', 'money']):
            reply = """💰 **Salary Tips:**
- **Research market rates** on Glassdoor, Levels.fyi, Payscale
- **Negotiate!** — Most offers have 10-20% room
- **Consider total compensation** — Stock, bonus, benefits, remote flexibility
- **Location matters** — Adjust expectations for cost of living"""
        elif any(w in q for w in ['hello', 'hi', 'hey', 'good']):
            reply = "Hello! 👋 How can I help with your career today? Ask me about resume tips, skills for specific roles, interview prep, or career paths!"
        elif any(w in q for w in ['thank', 'thanks', 'bye']):
            reply = "You're welcome! 😊 Good luck with your career journey! Feel free to come back anytime."
        else:
            reply = f"""🤔 Great question! Here's general career advice:

1. **Keep learning** — Technology evolves fast, stay current
2. **Build a portfolio** — GitHub projects, personal website
3. **Network** — LinkedIn, meetups, conferences
4. **Get certified** — Industry certifications boost your resume
5. **Use our tools** — Try the Dashboard for AI-powered resume analysis and job matching!

Try asking me about specific roles like "What skills do I need for data science?" or "How to improve my resume?" """

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
