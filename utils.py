import re


def parse_resume_sections(text):
    """Parse raw resume text into structured editable sections using AI heuristics."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    result = {
        'name': '', 'email': '', 'phone': '', 'location': '',
        'linkedin': '', 'website': '', 'summary': '',
        'experience': [], 'education': [], 'skills_technical': '',
        'skills_soft': '', 'certifications': '', 'projects': [],
        'languages': '', 'references': ''
    }

    # Extract contact info
    contact = extract_contact_info(text)
    result['name'] = contact['name'] if contact['name'] != 'Unknown Candidate' else (lines[0] if lines else '')
    result['email'] = contact['email'] if contact['email'] != 'Not found' else ''
    result['phone'] = contact['phone'] if contact['phone'] != 'Not found' else ''

    # Location
    loc_patterns = [r'(?:Location|Address|City)[:\s]+(.+)', r'(\w+,\s*\w[\w\s]*,?\s*\w*)']
    for pat in loc_patterns[:1]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            result['location'] = m.group(1).strip()
            break

    # LinkedIn & Website
    linkedin = re.search(r'((?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+)', text, re.IGNORECASE)
    if linkedin:
        result['linkedin'] = linkedin.group(1)
    website = re.search(r'((?:https?://)?(?:www\.)?(?!linkedin)[\w-]+\.(?:com|dev|io|org|net)/?\S*)', text, re.IGNORECASE)
    if website and '@' not in website.group(1):
        result['website'] = website.group(1)

    # Split text into sections by common headings
    section_keywords = {
        'summary': r'(?:summary|objective|profile|about\s*me)',
        'experience': r'(?:experience|employment|work\s*history|professional\s*experience)',
        'education': r'(?:education|academic|qualification)',
        'skills': r'(?:skills|competencies|technical\s*skills|expertise)',
        'certifications': r'(?:certification|certificate|license|accreditation)',
        'projects': r'(?:projects|portfolio|personal\s*projects)',
        'languages': r'(?:languages|language\s*proficiency)',
        'references': r'(?:references|referees)',
    }

    # Build section boundaries
    section_positions = []
    for sec_name, pattern in section_keywords.items():
        for m in re.finditer(r'(?:^|\n)\s*' + pattern + r'\s*[:\n]?', text, re.IGNORECASE | re.MULTILINE):
            section_positions.append((m.start(), sec_name, m.end()))
    section_positions.sort(key=lambda x: x[0])

    # Extract section texts
    section_texts = {}
    for i, (start, name, content_start) in enumerate(section_positions):
        end = section_positions[i+1][0] if i+1 < len(section_positions) else len(text)
        section_texts[name] = text[content_start:end].strip()

    # Summary
    if 'summary' in section_texts:
        result['summary'] = section_texts['summary'][:500]

    # Skills
    if 'skills' in section_texts:
        skills_text = section_texts['skills']
        tech_kw = ['python', 'java', 'sql', 'javascript', 'react', 'docker', 'aws', 'c++', 'html', 'css',
                    'git', 'linux', 'node', 'angular', 'vue', 'typescript', 'kubernetes', 'tensorflow']
        soft_kw = ['leadership', 'communication', 'teamwork', 'problem solving', 'management', 'collaboration']
        tech_found = [s.strip() for s in re.split(r'[,\n;|]', skills_text) if any(k in s.lower() for k in tech_kw)]
        soft_found = [s.strip() for s in re.split(r'[,\n;|]', skills_text) if any(k in s.lower() for k in soft_kw)]
        remaining = [s.strip() for s in re.split(r'[,\n;|]', skills_text) if s.strip() and s.strip() not in soft_found]
        result['skills_technical'] = ', '.join(tech_found if tech_found else remaining)
        result['skills_soft'] = ', '.join(soft_found)

    # Certifications
    if 'certifications' in section_texts:
        result['certifications'] = section_texts['certifications']

    # Languages
    if 'languages' in section_texts:
        result['languages'] = section_texts['languages'].replace('\n', ', ')

    # References
    if 'references' in section_texts:
        result['references'] = section_texts['references'].replace('\n', ' ')

    # Experience - parse into entries
    if 'experience' in section_texts:
        exp_text = section_texts['experience']
        exp_blocks = re.split(r'\n(?=\S)', exp_text)
        for block in exp_blocks:
            block = block.strip()
            if not block or len(block) < 10:
                continue
            block_lines = [l.strip() for l in block.split('\n') if l.strip()]
            title = block_lines[0] if block_lines else ''
            company = ''
            dates = ''
            desc_lines = []
            for ln in block_lines[1:]:
                date_match = re.search(r'(\w+\s*\d{4}\s*[-–]\s*(?:\w+\s*\d{4}|present|current))', ln, re.IGNORECASE)
                if date_match and not dates:
                    dates = date_match.group(1)
                    rest = ln.replace(dates, '').strip(' -|,')
                    if rest and not company:
                        company = rest
                elif not company and len(ln) < 60:
                    company = ln
                else:
                    desc_lines.append(ln)
            result['experience'].append({
                'title': title, 'company': company,
                'dates': dates, 'description': '\n'.join(desc_lines)
            })

    # Education
    if 'education' in section_texts:
        edu_text = section_texts['education']
        edu_blocks = re.split(r'\n(?=\S)', edu_text)
        for block in edu_blocks:
            block = block.strip()
            if not block or len(block) < 5:
                continue
            block_lines = [l.strip() for l in block.split('\n') if l.strip()]
            degree = block_lines[0] if block_lines else ''
            institution = ''
            dates = ''
            details = ''
            for ln in block_lines[1:]:
                date_match = re.search(r'(\d{4}\s*[-–]\s*\d{4})', ln)
                if date_match and not dates:
                    dates = date_match.group(1)
                elif not institution:
                    institution = ln
                else:
                    details = ln
            result['education'].append({
                'degree': degree, 'institution': institution,
                'dates': dates, 'details': details
            })

    # Projects
    if 'projects' in section_texts:
        proj_text = section_texts['projects']
        proj_blocks = re.split(r'\n(?=\S)', proj_text)
        for block in proj_blocks:
            block = block.strip()
            if not block or len(block) < 5:
                continue
            block_lines = [l.strip() for l in block.split('\n') if l.strip()]
            name = block_lines[0]
            tech = ''
            desc = '\n'.join(block_lines[1:])
            tech_match = re.search(r'(?:Technologies?|Tech|Tools?|Stack)[:\s]+(.+)', desc, re.IGNORECASE)
            if tech_match:
                tech = tech_match.group(1).strip()
            result['projects'].append({
                'name': name, 'technologies': tech, 'description': desc
            })

    # Fallback: if no sections detected, put text as summary
    if not section_texts and lines:
        result['summary'] = '\n'.join(lines[1:6])

    return result

def extract_contact_info(text):
    # Email
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    email = re.findall(email_pattern, text)
    
    # Phone (basic)
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone = re.findall(phone_pattern, text)
    
    # Name (heuristic: assume first line or early text with 2-3 words)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    name = lines[0] if lines else "Unknown Candidate"
    
    return {
        "name": name,
        "email": email[0] if email else "Not found",
        "phone": phone[0] if phone else "Not found"
    }

def calculate_resume_score(text, extracted_skills):
    text_lower = text.lower()
    score = 0
    strengths = []
    weaknesses = []
    
    # Skills (35%)
    if len(extracted_skills) >= 5:
        score += 35
        strengths.append("✓ Strong technical skills detected")
    elif len(extracted_skills) > 0:
        score += 15
        weaknesses.append("✗ Consider adding more industry-standard skills")
    else:
        weaknesses.append("✗ No technical skills detected")
        
    # Experience (25%)
    if any(word in text_lower for word in ['experience', 'work', 'employment', 'history']):
        years_found = re.findall(r'(\d+)\s+(?:years?|yrs?)', text_lower)
        if years_found and max(map(int, years_found)) > 2:
            score += 25
            strengths.append("✓ Good amount of experience found")
        else:
            score += 15
            strengths.append("✓ Experience section present")
    else:
        weaknesses.append("✗ Missing dedicated experience section")
        
    # Education (20%)
    if any(word in text_lower for word in ['education', 'university', 'bachelor', 'degree', 'master', 'phd', 'bsc', 'msc']):
        score += 20
        strengths.append("✓ Solid education background verified")
    else:
        weaknesses.append("✗ Education details not prominent")
        
    # Projects (10%)
    if any(word in text_lower for word in ['project', 'portfolio', 'github']):
        score += 10
        strengths.append("✓ Project/Portfolio links found")
    else:
        weaknesses.append("✗ Missing projects or portfolio")
        
    # Certifications (10%)
    if any(word in text_lower for word in ['certificat', 'certified', 'coursera', 'udemy', 'aws', 'gcp']):
        score += 10
        strengths.append("✓ Professional certifications found")
    else:
        weaknesses.append("✗ No certifications detected")
        
    # Baseline
    if score == 0: score = 45
    
    return {
        "score": score,
        "strengths": strengths,
        "weaknesses": weaknesses
    }

def get_missing_skills(user_skills, recommended_jobs):
    job_skills_text = " ".join([str(job.get('requisite_skill', '')) for job in recommended_jobs]).lower()
    industry_skills = ["python", "sql", "java", "c++", "javascript", "machine learning", "data analysis", "deep learning", "nlp", "tensorflow", "aws", "azure", "gcp", "react", "angular", "docker", "kubernetes", "tableau", "power bi", "statistics", "git", "agile", "scrum"]
    
    user_skills_lower = [s.lower() for s in user_skills]
    missing = []
    
    for skill in industry_skills:
        if skill in job_skills_text and skill not in user_skills_lower:
            missing.append(skill.title())
            
    # Sort by how frequently they appear in the job descriptions
    missing = sorted(missing, key=lambda s: job_skills_text.count(s.lower()), reverse=True)
    return missing[:5]

def get_career_path_and_questions(job_title):
    job_title = str(job_title).lower()
    
    if "data" in job_title or "analyst" in job_title or "scientist" in job_title:
        path = "Junior Data Analyst → Data Analyst → Senior Data Analyst → Analytics Manager"
        questions = [
            "1. Explain the difference between supervised and unsupervised learning.",
            "2. How do you handle missing values in a dataset?",
            "3. Write a SQL query to find the second highest salary."
        ]
    elif "software" in job_title or "developer" in job_title or "engineer" in job_title:
        path = "Junior Engineer → Software Engineer → Senior Engineer → Tech Lead"
        questions = [
            "1. Explain Object-Oriented Programming (OOP) concepts.",
            "2. What is the difference between a REST API and GraphQL?",
            "3. Describe how you would optimize a slow database query."
        ]
    elif "market" in job_title or "sales" in job_title:
        path = "Marketing Coordinator → Marketing Specialist → Marketing Manager → Director of Marketing"
        questions = [
            "1. How do you measure the ROI of a marketing campaign?",
            "2. Describe a successful campaign you led.",
            "3. How do you approach market segmentation?"
        ]
    else:
        path = f"Entry-level {job_title.title()} → {job_title.title()} → Senior {job_title.title()} → Manager"
        questions = [
            "1. What are your greatest professional strengths?",
            "2. Describe a challenge you faced at work and how you overcame it.",
            "3. Where do you see your career progressing in the next 5 years?"
        ]
        
    return {"path": path, "questions": questions}


def analyze_resume(text, parsed_sections):
    """Deep analysis of resume: score, strengths, weaknesses, improvement suggestions."""
    text_lower = text.lower()
    words = text.split()
    word_count = len(words)
    strengths = []
    weaknesses = []
    suggestions = []
    score = 0

    # 1. Contact Info (10 pts)
    has_email = bool(re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text))
    has_phone = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
    has_linkedin = 'linkedin' in text_lower
    contact_score = sum([has_email, has_phone, has_linkedin])
    if contact_score >= 3:
        score += 10
        strengths.append("✅ Complete contact info (email, phone, LinkedIn)")
    elif contact_score >= 2:
        score += 7
        strengths.append("✅ Good contact information provided")
        if not has_linkedin:
            suggestions.append("💡 Add your LinkedIn profile URL — recruiters check it 87% of the time")
    else:
        score += 3
        weaknesses.append("❌ Missing key contact details")
        suggestions.append("💡 Add email, phone number, and LinkedIn URL at the top of your resume")

    # 2. Professional Summary (10 pts)
    summary = parsed_sections.get('summary', '')
    if len(summary) > 50:
        score += 10
        strengths.append("✅ Strong professional summary present")
    elif len(summary) > 10:
        score += 5
        weaknesses.append("⚠️ Summary is too short")
        suggestions.append("💡 Expand your summary to 2-4 sentences highlighting your key value proposition and years of experience")
    else:
        weaknesses.append("❌ No professional summary detected")
        suggestions.append("💡 Add a 2-4 sentence professional summary at the top — it's the first thing recruiters read")

    # 3. Work Experience (20 pts)
    experiences = parsed_sections.get('experience', [])
    if len(experiences) >= 3:
        score += 20
        strengths.append(f"✅ Solid work history ({len(experiences)} positions)")
    elif len(experiences) >= 1:
        score += 12
        strengths.append(f"✅ Work experience included ({len(experiences)} position{'s' if len(experiences)>1 else ''})")
        suggestions.append("💡 Add more work experience entries — aim for 2-4 relevant positions")
    else:
        weaknesses.append("❌ No work experience section found")
        suggestions.append("💡 Add work experience with job titles, companies, dates, and bullet-point responsibilities")

    # 4. Action Verbs & Quantifiable Results (10 pts)
    action_verbs = ['led', 'managed', 'developed', 'built', 'designed', 'implemented',
                    'improved', 'increased', 'reduced', 'created', 'launched', 'optimized',
                    'delivered', 'achieved', 'automated', 'streamlined', 'mentored', 'coordinated']
    found_verbs = [v for v in action_verbs if v in text_lower]
    has_numbers = bool(re.search(r'\d+[%+]|\$[\d,]+|\d+\s*(?:users|customers|clients|projects|team|people|members)', text_lower))

    if len(found_verbs) >= 5 and has_numbers:
        score += 10
        strengths.append("✅ Excellent use of action verbs and quantified achievements")
    elif len(found_verbs) >= 3:
        score += 6
        strengths.append("✅ Good use of action verbs")
        if not has_numbers:
            suggestions.append("💡 Quantify your achievements with numbers (e.g., 'Increased sales by 25%', 'Managed a team of 8')")
    else:
        score += 2
        weaknesses.append("⚠️ Weak action verbs in descriptions")
        suggestions.append("💡 Start bullet points with strong action verbs: Led, Built, Designed, Improved, Delivered, Automated")

    # 5. Technical Skills (15 pts)
    tech_skills = parsed_sections.get('skills_technical', '')
    skill_count = len([s for s in re.split(r'[,;|]', tech_skills) if s.strip()]) if tech_skills else 0
    if skill_count >= 8:
        score += 15
        strengths.append(f"✅ Rich technical skill set ({skill_count} skills)")
    elif skill_count >= 4:
        score += 10
        strengths.append(f"✅ Good technical skills ({skill_count} listed)")
        suggestions.append("💡 Add more relevant technical skills — aim for 8-12 to pass ATS screening")
    elif skill_count >= 1:
        score += 5
        weaknesses.append("⚠️ Limited technical skills listed")
        suggestions.append("💡 List at least 6-8 technical skills relevant to your target role (tools, languages, frameworks)")
    else:
        weaknesses.append("❌ No technical skills section found")
        suggestions.append("💡 Add a dedicated skills section — ATS systems scan for specific keywords")

    # 6. Education (10 pts)
    education = parsed_sections.get('education', [])
    if len(education) >= 1:
        score += 10
        strengths.append("✅ Education background included")
    else:
        weaknesses.append("⚠️ No education section detected")
        suggestions.append("💡 Add your educational background with degree, institution, and graduation year")

    # 7. Certifications (5 pts)
    certs = parsed_sections.get('certifications', '')
    if certs and len(certs) > 5:
        score += 5
        strengths.append("✅ Professional certifications listed")
    else:
        suggestions.append("💡 Add relevant certifications (AWS, Google, Coursera, etc.) to stand out from other candidates")

    # 8. Projects (5 pts)
    projects = parsed_sections.get('projects', [])
    if len(projects) >= 2:
        score += 5
        strengths.append(f"✅ Portfolio projects included ({len(projects)} projects)")
    elif len(projects) == 1:
        score += 3
        suggestions.append("💡 Add 1-2 more projects to showcase your practical abilities")
    else:
        suggestions.append("💡 Include 2-3 relevant projects with technologies used and impact/outcome")

    # 9. Resume Length (5 pts)
    if 300 <= word_count <= 800:
        score += 5
        strengths.append(f"✅ Good resume length ({word_count} words)")
    elif word_count < 300:
        score += 2
        weaknesses.append(f"⚠️ Resume is too short ({word_count} words)")
        suggestions.append("💡 Expand your resume — aim for 400-700 words for a 1-page resume")
    else:
        score += 3
        weaknesses.append(f"⚠️ Resume may be too long ({word_count} words)")
        suggestions.append("💡 Trim to the most relevant content — recruiters spend ~7 seconds on initial screening")

    # 10. Formatting & Soft Skills (10 pts)
    soft_skills = parsed_sections.get('skills_soft', '')
    has_soft = bool(soft_skills and len(soft_skills) > 5)
    has_languages = bool(parsed_sections.get('languages', ''))
    bonus = sum([has_soft, has_languages])
    if bonus == 2:
        score += 10
        strengths.append("✅ Well-rounded profile with soft skills and languages")
    elif bonus == 1:
        score += 5
        if not has_soft:
            suggestions.append("💡 Add soft skills (Leadership, Communication, Problem-solving) to show versatility")
        if not has_languages:
            suggestions.append("💡 Add language proficiencies if you speak multiple languages")
    else:
        suggestions.append("💡 Add soft skills and language proficiencies for a more complete profile")

    # Ensure minimum score
    score = max(score, 15)

    # Grade
    if score >= 85:
        grade = "A"
        grade_color = "#22c55e"
        grade_msg = "Excellent! Your resume is highly competitive."
    elif score >= 70:
        grade = "B"
        grade_color = "#3b82f6"
        grade_msg = "Good resume with room for improvement."
    elif score >= 50:
        grade = "C"
        grade_color = "#f59e0b"
        grade_msg = "Average — apply the suggestions below to boost your chances."
    else:
        grade = "D"
        grade_color = "#ef4444"
        grade_msg = "Needs work — follow the improvement suggestions carefully."

    return {
        'score': score,
        'grade': grade,
        'grade_color': grade_color,
        'grade_msg': grade_msg,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'suggestions': suggestions,
        'word_count': word_count,
    }

def evaluate_interview_answer(question, answer):
    """Evaluates an interview answer using heuristics and NLP techniques."""
    if not answer or len(answer.strip()) < 10:
        return {"score": 0, "feedback": ["❌ Answer is too short. Please provide more detail."], "color": "#ef4444"}
    
    answer_lower = answer.lower()
    words = answer_lower.split()
    word_count = len(words)
    
    score = 50 # Base score for providing an answer
    feedback = []
    
    # 1. Length check
    if word_count > 40:
        score += 20
        feedback.append("✅ Good length and detail. The STAR method seems well-applied.")
    elif word_count > 20:
        score += 10
        feedback.append("⚠️ Consider elaborating more. Try using the STAR method (Situation, Task, Action, Result).")
    else:
        feedback.append("❌ Answer is quite brief. Provide specific examples to back up your points.")
        
    # 2. Action verbs
    action_verbs = ['led', 'managed', 'developed', 'built', 'designed', 'implemented', 'improved', 'increased', 'reduced', 'created', 'resolved', 'collaborated', 'analyzed', 'delivered']
    found_verbs = list(set([v for v in action_verbs if v in answer_lower]))
    if len(found_verbs) >= 2:
        score += 15
        feedback.append("✅ Great use of action verbs (" + ", ".join(found_verbs[:3]) + ").")
    elif len(found_verbs) == 1:
        score += 5
        feedback.append("💡 Try using more action verbs to describe your impact.")
    else:
        feedback.append("💡 Use action verbs (e.g., managed, developed, improved) to make your answer stronger and more dynamic.")
        
    # 3. Use of "I" vs "We" (Accountability)
    if ' i ' in f" {answer_lower} ":
        score += 10
        feedback.append("✅ Good personal accountability (using 'I' to describe your specific role).")
    
    # 4. Relevance (matching question words)
    question_words = set([w.strip('?.(),') for w in question.lower().split() if len(w) > 4])
    relevance_matches = [w for w in question_words if w in answer_lower]
    if len(relevance_matches) > 0:
        score += 5
        
    score = min(score, 100)
    
    if score >= 80:
        color = "#22c55e" # Green
    elif score >= 60:
        color = "#3b82f6" # Blue
    else:
        color = "#f59e0b" # Orange
        
    return {"score": score, "feedback": feedback, "color": color}

def get_ideal_answer_explanation(question):
    """Provides a brief explanation or ideal approach for common interview questions."""
    q_lower = question.lower()
    
    # Software Engineering
    if "solid principles" in q_lower:
        return "💡 **Ideal Approach:** Explain Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion briefly with a 1-sentence example for each."
    elif "rest api" in q_lower and "graphql" in q_lower:
        return "💡 **Ideal Approach:** Mention that REST has multiple endpoints returning fixed data structures (over/under-fetching), while GraphQL has a single endpoint allowing the client to request exactly what they need."
    elif "slow database query" in q_lower:
        return "💡 **Ideal Approach:** Discuss using EXPLAIN to analyze the query plan, adding missing indexes, avoiding SELECT *, and caching frequently accessed data."
    elif "ci/cd" in q_lower:
        return "💡 **Ideal Approach:** Explain Continuous Integration (automated testing on commit) and Continuous Deployment (automated deployment to production), mentioning tools like Jenkins, GitHub Actions, or GitLab."
    elif "merge conflicts" in q_lower:
        return "💡 **Ideal Approach:** Mention communicating with the team, pulling the latest main branch, using a visual diff tool, resolving conflicts locally, testing, and then committing."
        
    # Data Science
    elif "supervised" in q_lower and "unsupervised" in q_lower:
        return "💡 **Ideal Approach:** Supervised learning uses labeled data to predict outcomes (e.g., classification, regression). Unsupervised learning uses unlabeled data to find hidden patterns (e.g., clustering, PCA)."
    elif "missing values" in q_lower:
        return "💡 **Ideal Approach:** Discuss options like dropping rows/columns (if missing data is minimal), imputation (mean/median/mode), or using predictive models to estimate missing values based on context."
    elif "cross-validation" in q_lower:
        return "💡 **Ideal Approach:** Explain k-fold cross-validation. It's important because it helps prevent overfitting and provides a better estimate of model performance on unseen data."
        
    # General
    elif "tell me about yourself" in q_lower:
        return "💡 **Ideal Approach:** Use the Present-Past-Future formula. Briefly state your current role, highlight key past experiences/achievements, and explain why you're excited about this specific opportunity."
    elif "greatest professional strengths" in q_lower:
        return "💡 **Ideal Approach:** Pick 1-2 strengths highly relevant to the job description. Back them up with specific, quantifiable examples using the STAR method."
    elif "challenge" in q_lower and "overcame" in q_lower:
        return "💡 **Ideal Approach:** Choose a professional challenge (not a personal conflict). Focus 20% on the problem and 80% on the steps you took to resolve it and what you learned."
    elif "5 years" in q_lower:
        return "💡 **Ideal Approach:** Show ambition but be realistic. Express a desire to grow your skills, take on more responsibility, and align your goals with the company's trajectory."
    elif "why should we hire you" in q_lower:
        return "💡 **Ideal Approach:** Summarize how your unique combination of skills, experience, and cultural fit directly solves the specific problems this role is trying to address."
        
    # Fallback
    return "💡 **Ideal Approach:** Use the STAR method (Situation, Task, Action, Result) to structure your answer. Be concise, highlight your specific contributions using 'I', and quantify your impact where possible."
