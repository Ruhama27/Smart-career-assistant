"""
prepare_dataset.py
==================
Download and prepare a job dataset for the AI recommendation system.
Two modes:
  1. KAGGLE MODE:  Download real job data from Kaggle (requires API key)
  2. GENERATE MODE: Create a rich synthetic dataset (no API key needed)

Usage:
  python prepare_dataset.py --mode kaggle
  python prepare_dataset.py --mode generate --count 15000
"""

import pandas as pd
import argparse
import random
import os
import sys


# ═══════════════════════════════════════════════════
# MODE 1: Download from Kaggle
# ═══════════════════════════════════════════════════

def download_from_kaggle(dataset_slug="arshkon/linkedin-job-postings"):
    """
    Download a dataset from Kaggle and convert it to JobsFE.csv format.
    
    Popular dataset slugs:
      - arshkon/linkedin-job-postings  (1.3M LinkedIn jobs)
      - rashikrahmanpritom/real-life-jobs-dataset
      - promptcloud/jobs-on-naukricom
      - ravindrasinghrana/job-description-dataset
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("ERROR: kaggle package not installed. Run: pip install kaggle")
        return False

    print(f"📥 Downloading dataset: {dataset_slug}")
    print("   (Make sure your kaggle.json API key is in ~/.kaggle/)")
    print()

    api = KaggleApi()
    api.authenticate()

    download_dir = "kaggle_download"
    os.makedirs(download_dir, exist_ok=True)

    api.dataset_download_files(dataset_slug, path=download_dir, unzip=True)
    print(f"✅ Downloaded to {download_dir}/")

    # Find CSV files
    csv_files = []
    for root, dirs, files in os.walk(download_dir):
        for f in files:
            if f.endswith('.csv'):
                csv_files.append(os.path.join(root, f))

    if not csv_files:
        print("❌ No CSV files found in download. Check the dataset.")
        return False

    print(f"📄 Found CSV files: {csv_files}")
    print()

    # Try to load and convert the main file
    for csv_path in csv_files:
        df = pd.read_csv(csv_path, nrows=5)
        print(f"  {csv_path}: {list(df.columns)}")

    # Use the largest file
    main_csv = max(csv_files, key=os.path.getsize)
    print(f"\n📊 Using: {main_csv}")

    df = pd.read_csv(main_csv, low_memory=False)
    print(f"   Loaded {len(df)} rows")

    # Auto-detect and map columns
    cols = [c.lower() for c in df.columns]
    col_map = {c: c for c in df.columns}

    prepared = convert_to_jobsfe_format(df)
    if prepared is not None:
        backup_and_save(prepared)
        return True

    print("\n⚠️  Could not auto-detect column mapping.")
    print("   Please edit the convert_to_jobsfe_format() function for your dataset.")
    return False


def convert_to_jobsfe_format(df):
    """
    Try to auto-map common column names to JobsFE format.
    Edit this function if your dataset has different column names.
    """
    cols_lower = {c.lower(): c for c in df.columns}

    # Try to find matching columns
    def find_col(keywords):
        for kw in keywords:
            for cl, orig in cols_lower.items():
                if kw in cl:
                    return orig
        return None

    title_col = find_col(['title', 'position', 'job_title', 'designation'])
    company_col = find_col(['company', 'workplace', 'employer', 'organization'])
    location_col = find_col(['location', 'city', 'place', 'country'])
    desc_col = find_col(['description', 'duties', 'role', 'responsibilities', 'job_description'])
    skills_col = find_col(['skill', 'requirement', 'qualification', 'competenc'])
    mode_col = find_col(['work_type', 'working_mode', 'remote', 'schedule', 'employment_type'])
    salary_col = find_col(['salary', 'pay', 'compensation', 'wage'])
    benefits_col = find_col(['benefit', 'offer', 'perk'])

    if not title_col or not desc_col:
        print(f"  Could not find title column (tried: title, position, job_title)")
        print(f"  Could not find description column (tried: description, duties, role)")
        print(f"  Available columns: {list(df.columns)}")
        return None

    print(f"\n  Mapped columns:")
    print(f"    position        <- {title_col}")
    print(f"    workplace       <- {company_col or 'N/A'} + {location_col or 'N/A'}")
    print(f"    job_description <- {desc_col}")
    print(f"    skills          <- {skills_col or 'N/A'}")
    print(f"    working_mode    <- {mode_col or 'N/A'}")
    print(f"    salary          <- {salary_col or 'N/A'}")

    workplace = ""
    if company_col:
        workplace = df[company_col].fillna("").astype(str)
    if location_col:
        loc = df[location_col].fillna("").astype(str)
        workplace = workplace + " " + loc if len(workplace) > 0 else loc

    prepared = pd.DataFrame({
        "Job Id": range(1, len(df) + 1),
        "workplace": workplace if len(workplace) > 0 else "Not specified",
        "working_mode": df[mode_col].fillna("full-time").astype(str) if mode_col else "full-time",
        "salary": pd.to_numeric(df[salary_col], errors='coerce').fillna(0) if salary_col else 0,
        "position": df[title_col].fillna("").astype(str),
        "job_role_and_duties": df[desc_col].fillna("").astype(str),
        "requisite_skill": df[skills_col].fillna("").astype(str) if skills_col else "",
        "offer_details": df[benefits_col].fillna("").astype(str) if benefits_col else "",
    })

    # Clean: remove rows with empty position or description
    prepared = prepared[
        (prepared["position"].str.strip() != "") &
        (prepared["job_role_and_duties"].str.strip() != "")
    ]

    return prepared


# ═══════════════════════════════════════════════════
# MODE 2: Generate Rich Synthetic Dataset
# ═══════════════════════════════════════════════════

def generate_dataset(count=15000):
    """Generate a diverse, realistic job dataset."""
    print(f"🔨 Generating {count} realistic job entries...")

    # ── Job Categories ──
    categories = {
        "Software Engineering": {
            "titles": ["Software Engineer", "Frontend Developer", "Backend Developer",
                       "Full-Stack Developer", "DevOps Engineer", "Mobile Developer",
                       "Cloud Architect", "Site Reliability Engineer", "QA Engineer",
                       "Embedded Systems Engineer", "Blockchain Developer"],
            "skills": ["Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
                       "React", "Angular", "Vue.js", "Node.js", "Docker", "Kubernetes",
                       "AWS", "Azure", "GCP", "Git", "CI/CD", "REST APIs", "GraphQL",
                       "PostgreSQL", "MongoDB", "Redis", "Terraform", "Linux"],
            "duties": [
                "Design and develop scalable web applications and microservices",
                "Write clean, maintainable, and well-tested code",
                "Collaborate with cross-functional teams to define and ship new features",
                "Participate in code reviews and contribute to engineering best practices",
                "Debug and resolve production issues with quick turnaround",
                "Implement CI/CD pipelines and automate deployment processes",
                "Optimize application performance and scalability",
                "Mentor junior developers and contribute to technical documentation",
                "Architect cloud-native solutions using modern frameworks",
                "Integrate third-party APIs and services",
            ],
        },
        "Data Science": {
            "titles": ["Data Scientist", "Data Analyst", "ML Engineer",
                       "AI Research Scientist", "Data Engineer", "Business Intelligence Analyst",
                       "NLP Engineer", "Computer Vision Engineer", "Quantitative Analyst"],
            "skills": ["Python", "R", "SQL", "TensorFlow", "PyTorch", "Scikit-learn",
                       "Pandas", "NumPy", "Spark", "Hadoop", "Tableau", "Power BI",
                       "Statistics", "Machine Learning", "Deep Learning", "NLP",
                       "Computer Vision", "A/B Testing", "Data Modeling", "ETL"],
            "duties": [
                "Develop and deploy machine learning models for production use",
                "Analyze large datasets to extract actionable business insights",
                "Build and maintain data pipelines and ETL processes",
                "Create interactive dashboards and data visualizations",
                "Conduct A/B tests and statistical analyses to drive decision-making",
                "Collaborate with stakeholders to define KPIs and metrics",
                "Research and implement state-of-the-art ML algorithms",
                "Clean, preprocess, and transform raw data for analysis",
                "Present findings and recommendations to technical and non-technical audiences",
                "Monitor model performance and implement retraining strategies",
            ],
        },
        "Product & Design": {
            "titles": ["Product Manager", "UX Designer", "UI Designer",
                       "Product Designer", "UX Researcher", "Interaction Designer",
                       "Visual Designer", "Design System Lead"],
            "skills": ["Figma", "Sketch", "Adobe XD", "Prototyping", "User Research",
                       "Wireframing", "A/B Testing", "Agile", "JIRA", "Analytics",
                       "HTML/CSS", "Design Systems", "Accessibility", "Information Architecture"],
            "duties": [
                "Define product strategy and roadmap based on user needs and business goals",
                "Conduct user research interviews and usability testing",
                "Create wireframes, prototypes, and high-fidelity mockups",
                "Collaborate with engineering teams to ensure design implementation quality",
                "Analyze user behavior data to identify improvement opportunities",
                "Develop and maintain design systems and component libraries",
                "Lead design reviews and provide constructive feedback",
                "Champion user-centered design practices across the organization",
            ],
        },
        "Marketing & Sales": {
            "titles": ["Marketing Manager", "Digital Marketing Specialist",
                       "Content Marketing Manager", "SEO Specialist", "Sales Manager",
                       "Growth Hacker", "Brand Manager", "Social Media Manager",
                       "Email Marketing Specialist", "Performance Marketing Manager"],
            "skills": ["Google Analytics", "SEO", "SEM", "Social Media Marketing",
                       "Content Strategy", "Email Marketing", "CRM", "Salesforce",
                       "HubSpot", "Copywriting", "PPC", "Marketing Automation",
                       "Brand Strategy", "Market Research", "Lead Generation"],
            "duties": [
                "Develop and execute comprehensive marketing campaigns across channels",
                "Manage social media presence and create engaging content",
                "Analyze campaign performance metrics and optimize ROI",
                "Conduct market research and competitive analysis",
                "Build and nurture client relationships to drive sales growth",
                "Create compelling copy for advertisements, emails, and landing pages",
                "Manage marketing budgets and allocate resources effectively",
                "Collaborate with design teams to produce marketing collateral",
            ],
        },
        "Finance & Accounting": {
            "titles": ["Financial Analyst", "Accountant", "Auditor",
                       "Investment Banker", "Risk Analyst", "Tax Consultant",
                       "Controller", "Treasury Analyst", "Compliance Officer"],
            "skills": ["Financial Modeling", "Excel", "SAP", "QuickBooks",
                       "Bloomberg Terminal", "Financial Reporting", "GAAP", "IFRS",
                       "Risk Management", "Budgeting", "Forecasting", "SQL",
                       "VBA", "Regulatory Compliance", "Taxation"],
            "duties": [
                "Prepare financial statements and reports in compliance with GAAP/IFRS",
                "Conduct financial analysis and forecasting to support strategic decisions",
                "Manage accounts payable, receivable, and general ledger entries",
                "Perform internal audits and ensure regulatory compliance",
                "Develop financial models for valuation and investment analysis",
                "Monitor cash flow and manage treasury operations",
                "Prepare tax returns and ensure compliance with tax regulations",
                "Assess and mitigate financial risks across the organization",
            ],
        },
        "Healthcare": {
            "titles": ["Registered Nurse", "Medical Doctor", "Pharmacist",
                       "Healthcare Administrator", "Medical Lab Technician",
                       "Physical Therapist", "Clinical Research Coordinator",
                       "Health Informatics Specialist", "Biomedical Engineer"],
            "skills": ["Patient Care", "EMR Systems", "HIPAA Compliance",
                       "Clinical Research", "Medical Terminology", "CPR/BLS",
                       "Lab Analysis", "Pharmacology", "Diagnostics",
                       "Healthcare Management", "Epic Systems", "Medical Coding"],
            "duties": [
                "Provide patient care and administer treatments as prescribed",
                "Maintain accurate medical records using EMR systems",
                "Collaborate with multidisciplinary healthcare teams",
                "Conduct clinical assessments and diagnostic evaluations",
                "Ensure compliance with healthcare regulations and standards",
                "Educate patients and families about treatment plans and wellness",
                "Coordinate clinical research studies and data collection",
                "Manage healthcare facility operations and staff scheduling",
            ],
        },
        "Education": {
            "titles": ["Teacher", "Professor", "Curriculum Designer",
                       "Education Coordinator", "Academic Advisor",
                       "Instructional Designer", "School Administrator",
                       "Training Specialist", "Education Technology Specialist"],
            "skills": ["Curriculum Development", "Lesson Planning", "Classroom Management",
                       "Educational Technology", "Assessment Design", "LMS Platforms",
                       "Student Engagement", "Special Education", "Mentoring",
                       "Public Speaking", "Research Methods", "Grant Writing"],
            "duties": [
                "Develop and deliver engaging lesson plans and course materials",
                "Assess student performance and provide constructive feedback",
                "Create inclusive learning environments for diverse student populations",
                "Integrate educational technology to enhance learning outcomes",
                "Mentor and advise students on academic and career paths",
                "Collaborate with colleagues on curriculum development initiatives",
                "Conduct educational research and publish findings",
                "Manage classroom activities and maintain student records",
            ],
        },
        "Human Resources": {
            "titles": ["HR Manager", "Recruiter", "Talent Acquisition Specialist",
                       "HR Business Partner", "Compensation Analyst",
                       "Employee Relations Manager", "Learning & Development Manager",
                       "HR Generalist", "Diversity & Inclusion Coordinator"],
            "skills": ["Recruitment", "HRIS Systems", "Employee Relations",
                       "Performance Management", "Compensation & Benefits",
                       "Labor Laws", "Onboarding", "Training Development",
                       "Conflict Resolution", "Organizational Development",
                       "Workday", "ADP", "Diversity & Inclusion"],
            "duties": [
                "Manage full-cycle recruitment process from sourcing to onboarding",
                "Develop and implement HR policies and procedures",
                "Conduct employee engagement surveys and action planning",
                "Administer compensation, benefits, and performance review programs",
                "Handle employee relations issues and conflict resolution",
                "Design and deliver training and development programs",
                "Ensure compliance with employment laws and regulations",
                "Partner with leadership to align HR strategy with business goals",
            ],
        },
    }

    # ── Locations ──
    locations = [
        "New York, USA", "San Francisco, USA", "London, UK", "Berlin, Germany",
        "Toronto, Canada", "Sydney, Australia", "Singapore", "Tokyo, Japan",
        "Amsterdam, Netherlands", "Paris, France", "Dubai, UAE", "Mumbai, India",
        "Stockholm, Sweden", "Seoul, South Korea", "Sao Paulo, Brazil",
        "Austin, USA", "Seattle, USA", "Chicago, USA", "Boston, USA",
        "Remote", "Hybrid - Various Locations", "Bangalore, India",
        "Dublin, Ireland", "Zurich, Switzerland", "Hong Kong",
        "Addis Ababa, Ethiopia", "Nairobi, Kenya", "Lagos, Nigeria",
        "Cape Town, South Africa", "Cairo, Egypt",
    ]

    companies = [
        "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix",
        "Spotify", "Uber", "Airbnb", "Stripe", "Shopify", "Salesforce",
        "Adobe", "Oracle", "SAP", "IBM", "Intel", "NVIDIA", "Tesla",
        "JPMorgan Chase", "Goldman Sachs", "McKinsey", "Deloitte",
        "PwC", "Accenture", "Unilever", "Procter & Gamble",
        "Johnson & Johnson", "Pfizer", "Novartis", "Mayo Clinic",
        "Stanford Health", "MIT", "Harvard University", "World Bank",
        "United Nations", "WHO", "TechStartup Inc", "InnovateCo",
        "DataDriven Labs", "CloudScale Systems", "FinTech Solutions",
        "HealthTech Global", "EduLearn Platform", "GreenEnergy Corp",
        "CyberSecure Ltd", "BlockchainVentures", "AI Research Lab",
        "SmartCity Solutions", "BioGenesis", "QuantumCompute",
    ]

    work_modes = ["full-time", "part-time", "contract", "remote", "hybrid", "internship"]

    benefits_pool = [
        "Health insurance", "Dental and vision coverage", "401k matching",
        "Remote work options", "Flexible hours", "Unlimited PTO",
        "Stock options", "Annual bonus", "Professional development budget",
        "Gym membership", "Parental leave", "Tuition reimbursement",
        "Company laptop", "Relocation assistance", "Free meals",
        "Mental health support", "Retirement plan", "Life insurance",
    ]

    education_levels = [
        "Bachelor's degree", "Master's degree", "MBA", "PhD",
        "Associate's degree", "High school diploma", "Professional certification",
    ]

    experience_ranges = [
        "0-1 years", "1-3 years", "2-5 years", "3-7 years",
        "5-8 years", "5-10 years", "7-12 years", "10+ years",
    ]

    # ── Generate entries ──
    jobs = []
    for i in range(count):
        cat_name = random.choice(list(categories.keys()))
        cat = categories[cat_name]

        title = random.choice(cat["titles"])
        company = random.choice(companies)
        location = random.choice(locations)
        mode = random.choice(work_modes)

        # Select random duties (3-6)
        num_duties = random.randint(3, 6)
        duties = random.sample(cat["duties"], min(num_duties, len(cat["duties"])))
        duties_text = " ".join(duties)

        # Select random skills (4-8)
        num_skills = random.randint(4, 8)
        skills = random.sample(cat["skills"], min(num_skills, len(cat["skills"])))

        # Add education and experience to skills
        edu = random.choice(education_levels)
        exp = random.choice(experience_ranges)
        skills_text = ", ".join(skills) + f", {edu}, {exp} experience"

        # Salary based on title seniority
        base_salary = random.randint(35000, 180000)
        if "senior" in title.lower() or "lead" in title.lower() or "manager" in title.lower():
            base_salary = random.randint(80000, 220000)
        if "director" in title.lower() or "architect" in title.lower():
            base_salary = random.randint(120000, 280000)

        # Benefits (3-6)
        num_benefits = random.randint(3, 6)
        benefits = random.sample(benefits_pool, num_benefits)

        jobs.append({
            "Job Id": i + 1,
            "workplace": f"{company} {location}",
            "working_mode": mode,
            "salary": float(base_salary),
            "position": title,
            "job_role_and_duties": duties_text,
            "requisite_skill": skills_text,
            "offer_details": ", ".join(benefits),
        })

    df = pd.DataFrame(jobs)
    print(f"✅ Generated {len(df)} jobs across {len(categories)} categories")
    print(f"   Categories: {', '.join(categories.keys())}")
    return df


# ═══════════════════════════════════════════════════
# Save & Retrain
# ═══════════════════════════════════════════════════

def backup_and_save(df):
    """Backup old dataset, save new one, delete old embeddings."""
    # Backup existing
    if os.path.exists("JobsFE.csv"):
        backup = "JobsFE_backup.csv"
        os.rename("JobsFE.csv", backup)
        print(f"📦 Backed up old dataset to {backup}")

    # Save new
    df.to_csv("JobsFE.csv", index=False)
    print(f"💾 Saved {len(df)} jobs to JobsFE.csv")

    # Delete old embeddings so they regenerate
    if os.path.exists("job_embeddings.npy"):
        os.remove("job_embeddings.npy")
        print("🗑️  Deleted old job_embeddings.npy (will regenerate on next run)")

    print()
    print("=" * 50)
    print("✅ DONE! Your new dataset is ready.")
    print()
    print("Next steps:")
    print("  1. Run: streamlit run app.py")
    print("  2. Wait 2-5 min for embeddings to regenerate")
    print("  3. Upload a resume and test recommendations!")
    print("=" * 50)


# ═══════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare job dataset for AI recommendation system")
    parser.add_argument("--mode", choices=["kaggle", "generate"], default="generate",
                        help="'kaggle' to download from Kaggle, 'generate' to create synthetic data")
    parser.add_argument("--dataset", default="arshkon/linkedin-job-postings",
                        help="Kaggle dataset slug (for kaggle mode)")
    parser.add_argument("--count", type=int, default=15000,
                        help="Number of jobs to generate (for generate mode)")

    args = parser.parse_args()

    if args.mode == "kaggle":
        print("=" * 50)
        print("📥 KAGGLE DOWNLOAD MODE")
        print("=" * 50)
        print()
        print("Prerequisites:")
        print("  1. Go to kaggle.com → Settings → API → Create New Token")
        print("  2. Save kaggle.json to: C:\\Users\\<you>\\.kaggle\\kaggle.json")
        print()
        download_from_kaggle(args.dataset)
    else:
        print("=" * 50)
        print("🔨 DATASET GENERATION MODE")
        print("=" * 50)
        print()
        df = generate_dataset(args.count)
        backup_and_save(df)
