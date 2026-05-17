"""
Career Category Predictor using TF-IDF + Logistic Regression
Predicts the best job category for a given resume text.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import re


# Define career categories and their keyword signatures for training
CAREER_CATEGORIES = {
    "Software Engineer": [
        "python java javascript react angular vue node express django flask api rest graphql frontend backend fullstack devops docker kubernetes ci cd git github agile scrum software developer engineer web application microservices",
        "built scalable web applications using react and node managed ci cd pipelines with jenkins and docker containers deployed microservices on aws kubernetes cluster",
        "software engineer with experience in python javascript typescript react angular fullstack development rest api design database management agile methodologies",
        "developed maintained web applications using modern frameworks implemented automated testing pipelines code review pull requests version control git",
        "experience with cloud services aws azure gcp serverless architecture lambda functions api gateway dynamodb postgresql mongodb redis",
    ],
    "Data Scientist": [
        "python r sql machine learning deep learning tensorflow pytorch pandas numpy scikit-learn statistics data analysis visualization tableau power bi jupyter notebook data mining nlp artificial intelligence neural network",
        "built predictive models using scikit-learn and tensorflow performed statistical analysis on large datasets created interactive dashboards with tableau and plotly",
        "data scientist with expertise in machine learning natural language processing computer vision deep learning model training evaluation deployment",
        "experience with data preprocessing feature engineering model selection hyperparameter tuning cross validation a b testing experimental design",
        "worked with big data technologies spark hadoop hive distributed computing created etl pipelines data warehousing solutions",
    ],
    "AI/ML Engineer": [
        "machine learning deep learning neural network tensorflow pytorch keras nlp computer vision reinforcement learning gan transformer bert gpt model training deployment mlops",
        "designed and deployed production ml models using tensorflow serving and kubernetes implemented real-time inference pipelines with low latency",
        "ai engineer specializing in large language models transformer architectures attention mechanisms fine-tuning transfer learning model optimization",
        "experience with mlops tools mlflow kubeflow airflow model monitoring drift detection automated retraining pipelines feature stores",
        "built computer vision systems using convolutional neural networks yolo resnet efficientnet image classification object detection segmentation",
    ],
    "Mobile Developer": [
        "android ios swift kotlin flutter react native mobile app development xcode android studio firebase push notifications ui ux mobile design responsive",
        "developed cross-platform mobile applications using flutter and react native published apps on google play store and apple app store",
        "mobile developer with experience in native android kotlin java and ios swift development restful api integration offline storage",
        "implemented push notifications in-app purchases analytics tracking crash reporting performance optimization for mobile applications",
        "experience with mobile ci cd fastlane testflight app distribution mobile security authentication biometrics",
    ],
    "Web Developer": [
        "html css javascript typescript react angular vue nextjs nuxt tailwind bootstrap sass webpack vite frontend web development responsive design",
        "built responsive websites using html css javascript react and nextjs implemented seo optimization and performance improvements",
        "web developer with expertise in modern frontend frameworks component-based architecture state management routing client-side rendering",
        "experience with cms systems wordpress shopify headless cms jamstack static site generation server side rendering progressive web apps",
        "implemented accessibility standards wcag cross-browser compatibility responsive design mobile-first approach web performance optimization",
    ],
    "Business Analyst": [
        "business analysis requirements gathering stakeholder management project management documentation process improvement data analysis excel sql reporting kpi metrics",
        "conducted business requirements analysis created functional specifications managed stakeholder expectations delivered project documentation",
        "business analyst with experience in agile waterfall methodology user story mapping process flow diagrams gap analysis feasibility studies",
        "experience with business intelligence tools tableau power bi looker created dashboards reports for executive decision making",
        "performed market research competitive analysis swot analysis cost-benefit analysis risk assessment change management",
    ],
    "Product Manager": [
        "product management roadmap strategy user research market analysis competitive analysis feature prioritization a b testing metrics growth analytics sprint planning backlog",
        "led product strategy and roadmap for saas platform managed cross-functional teams of engineers designers and marketers",
        "product manager with experience in agile product development user-centered design data-driven decision making go-to-market strategy",
        "defined product requirements user stories acceptance criteria conducted user interviews usability testing and feedback analysis",
        "experience with product analytics tools mixpanel amplitude google analytics funnel analysis retention metrics conversion optimization",
    ],
    "DevOps Engineer": [
        "devops cloud aws azure gcp docker kubernetes terraform ansible jenkins gitlab ci cd pipeline infrastructure automation monitoring prometheus grafana linux",
        "designed and implemented cloud infrastructure on aws using terraform managed kubernetes clusters with helm charts and istio service mesh",
        "devops engineer with expertise in infrastructure as code configuration management continuous integration deployment automation monitoring alerting",
        "experience with containerization docker podman orchestration kubernetes ecs serverless computing lambda functions api gateway",
        "implemented observability solutions logging elk stack metrics prometheus grafana tracing jaeger incident response on-call rotation",
    ],
    "Cybersecurity Analyst": [
        "cybersecurity information security network security vulnerability assessment penetration testing siem firewall ids ips encryption compliance gdpr soc",
        "conducted vulnerability assessments penetration testing for web applications and network infrastructure implemented security policies and procedures",
        "security analyst with experience in threat detection incident response forensic analysis malware analysis risk assessment compliance auditing",
        "experience with security tools splunk nessus burp suite wireshark metasploit kali linux owasp top 10 vulnerability remediation",
        "implemented zero trust architecture identity access management multi-factor authentication security awareness training phishing simulation",
    ],
    "UI/UX Designer": [
        "ui ux design figma sketch adobe xd prototyping wireframing user research usability testing design system typography color theory interaction design",
        "designed user interfaces for web and mobile applications created design systems component libraries maintained brand consistency",
        "ui ux designer with expertise in user-centered design thinking information architecture interaction design visual design accessibility",
        "conducted user research interviews surveys usability testing created personas journey maps wireframes mockups high-fidelity prototypes",
        "experience with design tools figma sketch invision zeplin abstract collaborated with engineers on design implementation and handoff",
    ],
}

# Course recommendations per category
COURSE_RECOMMENDATIONS = {
    "Software Engineer": {
        "Python": "Python for Everybody — Coursera (University of Michigan)",
        "JavaScript": "The Complete JavaScript Course — Udemy (Jonas Schmedtmann)",
        "React": "React — The Complete Guide — Udemy (Academind)",
        "Docker": "Docker Mastery — Udemy (Bret Fisher)",
        "AWS": "AWS Certified Solutions Architect — Udemy (Stephane Maarek)",
        "System Design": "Grokking System Design — Educative.io",
        "Git": "Git & GitHub Bootcamp — Udemy (Colt Steele)",
    },
    "Data Scientist": {
        "Python": "Python for Data Science — Coursera (IBM)",
        "SQL": "SQL for Data Science — Coursera (UC Davis)",
        "Machine Learning": "Machine Learning Specialization — Coursera (Andrew Ng)",
        "TensorFlow": "Deep Learning Specialization — Coursera (DeepLearning.AI)",
        "Statistics": "Statistics with Python — Coursera (University of Michigan)",
        "Tableau": "Tableau A-Z — Udemy (Kirill Eremenko)",
        "Power BI": "Microsoft Power BI Desktop — Udemy (Maven Analytics)",
    },
    "AI/ML Engineer": {
        "Deep Learning": "Deep Learning Specialization — Coursera (Andrew Ng)",
        "NLP": "Natural Language Processing — Coursera (DeepLearning.AI)",
        "Computer Vision": "Deep Learning for Computer Vision — CS231n (Stanford)",
        "MLOps": "Machine Learning Engineering for Production — Coursera",
        "PyTorch": "PyTorch for Deep Learning — Udemy (Daniel Bourke)",
        "TensorFlow": "TensorFlow Developer Certificate — Coursera",
        "LLMs": "LangChain & LLM App Development — DeepLearning.AI",
    },
    "Mobile Developer": {
        "Flutter": "Flutter & Dart Complete Guide — Udemy (Maximilian)",
        "React Native": "React Native — The Practical Guide — Udemy",
        "Swift": "iOS & Swift Bootcamp — Udemy (Angela Yu)",
        "Kotlin": "Android Kotlin Developer — Udacity Nanodegree",
        "Firebase": "Firebase in a Weekend — Udacity",
    },
    "Web Developer": {
        "HTML/CSS": "The Web Developer Bootcamp — Udemy (Colt Steele)",
        "JavaScript": "JavaScript: The Complete Guide — Udemy",
        "React": "React — The Complete Guide — Udemy (Academind)",
        "Next.js": "Next.js & React — Udemy (Maximilian)",
        "TypeScript": "Understanding TypeScript — Udemy (Academind)",
    },
    "Business Analyst": {
        "SQL": "SQL for Business Analysts — DataCamp",
        "Excel": "Excel Skills for Business — Coursera (Macquarie University)",
        "Tableau": "Tableau A-Z — Udemy (Kirill Eremenko)",
        "Agile": "Agile with Atlassian Jira — Coursera (Atlassian)",
        "CBAP": "CBAP Certification Prep — LinkedIn Learning",
    },
    "Product Manager": {
        "Product Strategy": "Digital Product Management — Coursera (University of Virginia)",
        "Agile": "Agile Product Management — LinkedIn Learning",
        "Analytics": "Product Analytics Micro-Certification — Pendo/Mind the Product",
        "SQL": "SQL for Product Managers — DataCamp",
        "UX Research": "UX Research and Design — Coursera (University of Michigan)",
    },
    "DevOps Engineer": {
        "AWS": "AWS Certified DevOps Engineer — Udemy (Stephane Maarek)",
        "Docker": "Docker & Kubernetes Complete Guide — Udemy",
        "Terraform": "HashiCorp Certified Terraform Associate — Udemy",
        "Kubernetes": "Certified Kubernetes Administrator — KodeKloud",
        "Linux": "Linux Administration Bootcamp — Udemy",
    },
    "Cybersecurity Analyst": {
        "CompTIA Security+": "CompTIA Security+ — Udemy (Jason Dion)",
        "Ethical Hacking": "Practical Ethical Hacking — TCM Security",
        "CISSP": "CISSP Certification — Coursera (ISC²)",
        "Network Security": "Network Security — Coursera (Palo Alto Networks)",
        "SIEM": "Splunk Fundamentals — Splunk Free Training",
    },
    "UI/UX Designer": {
        "Figma": "Figma UI/UX Design Essentials — Udemy (Daniel Scott)",
        "UX Research": "Google UX Design Certificate — Coursera",
        "Design Systems": "Design Systems with Figma — Designlab",
        "Prototyping": "Interaction Design Specialization — Coursera",
        "Accessibility": "Web Accessibility — Udacity",
    },
}


class CareerPredictor:
    """Predicts career category from resume text using TF-IDF + Logistic Regression."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
        self.classifier = LogisticRegression(max_iter=1000, C=1.0)
        self.label_encoder = LabelEncoder()
        self._train()

    def _train(self):
        """Train the classifier on the category keyword signatures."""
        texts = []
        labels = []
        for category, samples in CAREER_CATEGORIES.items():
            for sample in samples:
                texts.append(sample)
                labels.append(category)

        self.label_encoder.fit(labels)
        y = self.label_encoder.transform(labels)
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, y)

    def predict(self, resume_text):
        """Predict career category with confidence scores."""
        X = self.vectorizer.transform([resume_text.lower()])
        probas = self.classifier.predict_proba(X)[0]
        classes = self.label_encoder.classes_

        # Sort by probability descending
        ranked = sorted(zip(classes, probas), key=lambda x: x[1], reverse=True)

        return {
            'top_category': ranked[0][0],
            'top_confidence': round(ranked[0][1] * 100, 1),
            'all_categories': [(cat, round(prob * 100, 1)) for cat, prob in ranked],
            'top_3': [(cat, round(prob * 100, 1)) for cat, prob in ranked[:3]],
        }

    def get_courses(self, category, user_skills=None):
        """Get course recommendations for a career category, optionally filtering by missing skills."""
        courses = COURSE_RECOMMENDATIONS.get(category, {})
        if user_skills:
            user_skills_lower = [s.lower() for s in user_skills]
            # Prioritize courses for skills the user DOESN'T have
            missing = {k: v for k, v in courses.items() if k.lower() not in user_skills_lower}
            known = {k: v for k, v in courses.items() if k.lower() in user_skills_lower}
            return {'missing_skill_courses': missing, 'advancement_courses': known}
        return {'missing_skill_courses': courses, 'advancement_courses': {}}
