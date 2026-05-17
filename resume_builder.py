from fpdf import FPDF
import textwrap
class ResumePDF(FPDF):
    """Professional Resume PDF Generator with modern styling."""
    # Color palette
    PRIMARY = (37, 99, 235)       # Blue-600
    DARK = (17, 24, 39)           # Gray-900
    MEDIUM = (75, 85, 99)         # Gray-600
    LIGHT = (156, 163, 175)       # Gray-400
    ACCENT_BG = (239, 246, 255)   # Blue-50
    DIVIDER = (209, 213, 219)     # Gray-300
    WHITE = (255, 255, 255)
    def header(self):
        pass
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(*self.LIGHT)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
    def _draw_divider(self):
        self.set_draw_color(*self.DIVIDER)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
    def _section_heading(self, title, icon=""):
        self.ln(3)
        self.set_font('helvetica', 'B', 13)
        self.set_text_color(*self.PRIMARY)
        self.cell(0, 8, text=f"{icon}  {title.upper()}", new_x="LMARGIN", new_y="NEXT")
        self._draw_divider()
        self.set_text_color(*self.DARK)
    def _add_body_text(self, text, bold=False):
        style = 'B' if bold else ''
        self.set_font('helvetica', style, 10)
        self.set_text_color(*self.MEDIUM)
        self.multi_cell(0, 5.5, text=str(text))
        self.ln(1)
    def _add_bullet(self, text):
        self.set_font('helvetica', '', 10)
        self.set_text_color(*self.MEDIUM)
        x = self.get_x()
        self.cell(6, 5.5, text="- ")
        self.multi_cell(0, 5.5, text=str(text))
        self.ln(0.5)


def generate_pdf(data):
    """
    Generate a professional resume PDF from structured data.

    Expected data dict keys:
        name, email, phone, location, linkedin, website,
        summary, experience (list of dicts or text),
        education (list of dicts or text), skills,
        certifications, languages, projects (list of dicts or text),
        references
    """
    pdf = ResumePDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── Header: Name ──
    pdf.set_font('helvetica', 'B', 26)
    pdf.set_text_color(*ResumePDF.DARK)
    name = data.get('name', 'Your Name')
    pdf.cell(0, 12, text=name, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(1)

    # ── Header: Contact line ──
    contact_parts = []
    if data.get('email'):
        contact_parts.append(data['email'])
    if data.get('phone'):
        contact_parts.append(data['phone'])
    if data.get('location'):
        contact_parts.append(data['location'])
    if data.get('linkedin'):
        contact_parts.append(data['linkedin'])
    if data.get('website'):
        contact_parts.append(data['website'])

    if contact_parts:
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(*ResumePDF.MEDIUM)
        contact_line = "  |  ".join(contact_parts)
        pdf.cell(0, 6, text=contact_line, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(4)

    # ── Professional Summary ──
    if data.get('summary'):
        pdf._section_heading("Professional Summary", icon=">>")
        pdf._add_body_text(data['summary'])

    # ── Work Experience ──
    experience = data.get('experience')
    if experience:
        pdf._section_heading("Work Experience", icon=">>")
        if isinstance(experience, list):
            for exp in experience:
                if isinstance(exp, dict):
                    title_line = exp.get('title', '')
                    company = exp.get('company', '')
                    dates = exp.get('dates', '')
                    description = exp.get('description', '')

                    pdf.set_font('helvetica', 'B', 11)
                    pdf.set_text_color(*ResumePDF.DARK)
                    pdf.cell(0, 6, text=title_line, new_x="LMARGIN", new_y="NEXT")

                    if company or dates:
                        pdf.set_font('helvetica', 'I', 10)
                        pdf.set_text_color(*ResumePDF.PRIMARY)
                        info_line = f"{company}"
                        if dates:
                            info_line += f"  |  {dates}"
                        pdf.cell(0, 5, text=info_line, new_x="LMARGIN", new_y="NEXT")

                    if description:
                        pdf.ln(1)
                        for line in description.strip().split('\n'):
                            line = line.strip()
                            if line:
                                pdf._add_bullet(line)
                    pdf.ln(3)
                else:
                    pdf._add_body_text(str(exp))
        else:
            for line in str(experience).strip().split('\n'):
                line = line.strip()
                if line:
                    pdf._add_bullet(line)
            pdf.ln(2)

    # ── Education ──
    education = data.get('education')
    if education:
        pdf._section_heading("Education", icon=">>")
        if isinstance(education, list):
            for edu in education:
                if isinstance(edu, dict):
                    degree = edu.get('degree', '')
                    institution = edu.get('institution', '')
                    dates = edu.get('dates', '')
                    details = edu.get('details', '')

                    pdf.set_font('helvetica', 'B', 11)
                    pdf.set_text_color(*ResumePDF.DARK)
                    pdf.cell(0, 6, text=degree, new_x="LMARGIN", new_y="NEXT")

                    if institution or dates:
                        pdf.set_font('helvetica', 'I', 10)
                        pdf.set_text_color(*ResumePDF.PRIMARY)
                        info_line = institution
                        if dates:
                            info_line += f"  |  {dates}"
                        pdf.cell(0, 5, text=info_line, new_x="LMARGIN", new_y="NEXT")

                    if details:
                        pdf.ln(1)
                        pdf._add_body_text(details)
                    pdf.ln(3)
                else:
                    pdf._add_body_text(str(edu))
        else:
            pdf._add_body_text(str(education))

    # ── Skills ──
    if data.get('skills'):
        pdf._section_heading("Skills", icon=">>")
        skills_text = data['skills']
        if isinstance(skills_text, list):
            skills_text = ", ".join(skills_text)
        # Wrap skills in a styled block
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(*ResumePDF.DARK)
        pdf.multi_cell(0, 5.5, text=skills_text)
        pdf.ln(2)

    # ── Certifications ──
    if data.get('certifications'):
        pdf._section_heading("Certifications", icon=">>")
        certs = data['certifications']
        if isinstance(certs, list):
            for cert in certs:
                pdf._add_bullet(str(cert))
        else:
            for line in str(certs).strip().split('\n'):
                line = line.strip()
                if line:
                    pdf._add_bullet(line)
        pdf.ln(2)

    # ── Projects ──
    projects = data.get('projects')
    if projects:
        pdf._section_heading("Projects", icon=">>")
        if isinstance(projects, list):
            for proj in projects:
                if isinstance(proj, dict):
                    proj_name = proj.get('name', '')
                    proj_desc = proj.get('description', '')
                    proj_tech = proj.get('technologies', '')

                    pdf.set_font('helvetica', 'B', 11)
                    pdf.set_text_color(*ResumePDF.DARK)
                    pdf.cell(0, 6, text=proj_name, new_x="LMARGIN", new_y="NEXT")

                    if proj_tech:
                        pdf.set_font('helvetica', 'I', 9)
                        pdf.set_text_color(*ResumePDF.PRIMARY)
                        pdf.cell(0, 5, text=f"Technologies: {proj_tech}", new_x="LMARGIN", new_y="NEXT")

                    if proj_desc:
                        pdf.ln(1)
                        pdf._add_body_text(proj_desc)
                    pdf.ln(2)
                else:
                    pdf._add_bullet(str(proj))
        else:
            pdf._add_body_text(str(projects))

    # ── Languages ──
    if data.get('languages'):
        pdf._section_heading("Languages", icon=">>")
        langs = data['languages']
        if isinstance(langs, list):
            langs = ", ".join(langs)
        pdf._add_body_text(langs)

    # ── References ──
    if data.get('references'):
        pdf._section_heading("References", icon=">>")
        refs = data['references']
        if isinstance(refs, list):
            for ref in refs:
                pdf._add_bullet(str(ref))
        else:
            pdf._add_body_text(str(refs))

    return bytes(pdf.output())  # Returns bytes for Streamlit download
