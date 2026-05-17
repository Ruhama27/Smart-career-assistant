"""
Cover Letter Generator — creates personalized cover letters as PDF.
"""
from fpdf import FPDF
import io
import textwrap


def generate_cover_letter_text(name, email, phone, job_title, company, skills, experience_summary):
    """Generate a professional cover letter text."""
    skills_str = ", ".join(skills[:6]) if skills else "relevant technical and professional skills"
    exp_str = experience_summary if experience_summary else "several years of progressive experience in the field"

    letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. With {exp_str}, I am confident that my background and passion make me an excellent candidate for this role.

Throughout my career, I have developed expertise in {skills_str}. These competencies have enabled me to deliver measurable results, drive innovation, and contribute meaningfully to cross-functional teams. I am particularly drawn to {company} because of its reputation for excellence and commitment to pushing boundaries in the industry.

In my previous roles, I have consistently demonstrated the ability to tackle complex challenges, collaborate effectively with diverse teams, and deliver projects on time and within scope. I am eager to bring this same dedication and proven track record to {company} as your next {job_title}.

I am excited about the opportunity to contribute to your team and would welcome the chance to discuss how my skills and experiences align with your needs. I am available for an interview at your earliest convenience and can be reached at {email} or {phone}.

Thank you for considering my application. I look forward to the opportunity to discuss this position further.

Sincerely,
{name}"""
    return letter


def generate_cover_letter_pdf(name, email, phone, job_title, company, skills, experience_summary):
    """Generate a professional cover letter PDF."""
    letter_text = generate_cover_letter_text(name, email, phone, job_title, company, skills, experience_summary)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    # Header — Name
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 12, name, ln=True, align="C")

    # Contact line
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    contact_parts = [p for p in [email, phone] if p]
    pdf.cell(0, 6, " | ".join(contact_parts), ln=True, align="C")

    # Divider
    pdf.ln(4)
    pdf.set_draw_color(29, 78, 216)
    pdf.set_line_width(0.5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)

    # Date
    from datetime import datetime
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, datetime.now().strftime("%B %d, %Y"), ln=True)
    pdf.ln(4)

    # Body
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)

    for paragraph in letter_text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if paragraph.startswith("Dear") or paragraph.startswith("Sincerely"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, paragraph)
            pdf.set_font("Helvetica", "", 11)
        else:
            pdf.multi_cell(0, 6, paragraph)
        pdf.ln(4)

    return bytes(pdf.output())
