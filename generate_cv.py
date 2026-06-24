from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Flowable
from reportlab.pdfgen import canvas as pdfcanvas

W, H = A4

# ── Palette ──────────────────────────────────────────────────────────────────
DARK_BG   = colors.HexColor("#0f1117")
CARD_BG   = colors.HexColor("#1a1d2e")
INDIGO    = colors.HexColor("#6366f1")
PURPLE    = colors.HexColor("#a855f7")
SLATE_300 = colors.HexColor("#cbd5e1")
SLATE_400 = colors.HexColor("#94a3b8")
SLATE_500 = colors.HexColor("#64748b")
WHITE     = colors.HexColor("#f8fafc")
CYAN      = colors.HexColor("#22d3ee")
GREEN     = colors.HexColor("#4ade80")
PINK      = colors.HexColor("#f472b6")

# ── Custom flowables ──────────────────────────────────────────────────────────
class SkillBar(Flowable):
    def __init__(self, label, pct, color=INDIGO, width=170*mm, height=5):
        super().__init__()
        self.label  = label
        self.pct    = pct
        self.color  = color
        self.bw     = width
        self.height = height
        self.width  = width
        self._height = 18

    def draw(self):
        c = self.canv
        y = 4
        # label
        c.setFont("Helvetica", 8)
        c.setFillColor(SLATE_300)
        c.drawString(0, y + 6, self.label)
        # pct text
        c.setFillColor(SLATE_400)
        c.drawRightString(self.bw, y + 6, f"{self.pct}%")
        # track
        c.setFillColor(colors.HexColor("#1e293b"))
        c.roundRect(0, y, self.bw, self.height, 2, fill=1, stroke=0)
        # fill
        c.setFillColor(self.color)
        fill_w = self.bw * self.pct / 100
        c.roundRect(0, y, fill_w, self.height, 2, fill=1, stroke=0)


class SectionHeader(Flowable):
    def __init__(self, text, accent=INDIGO, width=170*mm):
        super().__init__()
        self.text   = text
        self.accent = accent
        self.width  = width
        self._height = 22

    def draw(self):
        c = self.canv
        c.setFillColor(self.accent)
        c.rect(0, 14, 28, 3, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(WHITE)
        c.drawString(0, 0, self.text.upper())


class ColorBar(Flowable):
    """Gradient-ish top header bar."""
    def __init__(self, width, height):
        super().__init__()
        self.width  = width
        self._height = height

    def draw(self):
        c = self.canv
        c.setFillColor(CARD_BG)
        c.rect(0, 0, self.width, self._height, fill=1, stroke=0)
        c.setFillColor(INDIGO)
        c.rect(0, self._height - 4, self.width * 0.55, 4, fill=1, stroke=0)
        c.setFillColor(PURPLE)
        c.rect(self.width * 0.55, self._height - 4, self.width * 0.45, 4, fill=1, stroke=0)


class StatBox(Flowable):
    def __init__(self, number, label, color=INDIGO, w=52*mm):
        super().__init__()
        self.number = str(number)
        self.label  = label
        self.color  = color
        self.width  = w
        self._height = 36

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#1e293b"))
        c.roundRect(0, 0, self.width, self._height, 6, fill=1, stroke=0)
        c.setFillColor(self.color)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(self.width / 2, 18, self.number + "+")
        c.setFillColor(SLATE_400)
        c.setFont("Helvetica", 7)
        c.drawCentredString(self.width / 2, 6, self.label)


# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    base = dict(fontName="Helvetica", textColor=SLATE_300, leading=13)
    return {
        "name": ParagraphStyle("name",
            fontName="Helvetica-Bold", fontSize=22,
            textColor=WHITE, leading=26, alignment=TA_CENTER),
        "title": ParagraphStyle("title",
            fontName="Helvetica", fontSize=11,
            textColor=INDIGO, leading=14, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("sub",
            fontName="Helvetica", fontSize=8.5,
            textColor=SLATE_400, leading=12, alignment=TA_CENTER),
        "contact": ParagraphStyle("contact",
            fontName="Helvetica", fontSize=8,
            textColor=SLATE_400, leading=11, alignment=TA_CENTER),
        "body": ParagraphStyle("body", fontSize=8.5, leading=13,
            textColor=SLATE_300, **{k: v for k, v in base.items() if k != "textColor" and k != "leading"}),
        "bullet": ParagraphStyle("bullet", fontSize=8.5, leading=13,
            textColor=SLATE_300, leftIndent=10, bulletIndent=0,
            fontName="Helvetica"),
        "job_title": ParagraphStyle("jt", fontName="Helvetica-Bold", fontSize=9.5,
            textColor=WHITE, leading=13),
        "job_company": ParagraphStyle("jc", fontName="Helvetica", fontSize=8.5,
            textColor=INDIGO, leading=12),
        "job_date": ParagraphStyle("jd", fontName="Helvetica-Oblique", fontSize=8,
            textColor=SLATE_500, leading=11),
        "tag": ParagraphStyle("tag", fontName="Helvetica-Bold", fontSize=7.5,
            textColor=CYAN, leading=10),
        "label": ParagraphStyle("lbl", fontName="Helvetica-Bold", fontSize=8,
            textColor=WHITE, leading=11),
        "small": ParagraphStyle("sm", fontName="Helvetica", fontSize=7.5,
            textColor=SLATE_400, leading=10),
        "quote": ParagraphStyle("quote", fontName="Helvetica-Oblique", fontSize=8,
            textColor=SLATE_500, leading=12, alignment=TA_CENTER),
    }


def hr(color=SLATE_500, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=4, spaceBefore=4)


def sp(h=4):
    return Spacer(1, h)


# ── Build ─────────────────────────────────────────────────────────────────────
def build_cv():
    doc = SimpleDocTemplate(
        "assets/Bannaga_CV.pdf",
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=12*mm, bottomMargin=12*mm,
    )

    S = make_styles()
    story = []
    PW = W - 30*mm  # usable width

    # ── Background canvas callback ────────────────────────────────────────────
    def dark_bg(c, doc):
        c.saveState()
        c.setFillColor(DARK_BG)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.restoreState()

    doc.build(story, onFirstPage=dark_bg, onLaterPages=dark_bg)

    # rebuild with real content
    story = []

    # ── HEADER ────────────────────────────────────────────────────────────────
    story.append(ColorBar(PW, 6))
    story.append(sp(8))
    story.append(Paragraph("Bannaga Altieb Abdul Muhsin", S["name"]))
    story.append(sp(3))
    story.append(Paragraph("Electrical Project Engineer — Riyadh, Saudi Arabia", S["title"]))
    story.append(sp(2))
    story.append(Paragraph(
        "CEM®  ·  CMVP®  ·  LEED Green Associate  ·  Telecom &amp; Industrial Infrastructure  ·  Energy Optimization  ·  O&amp;M Excellence",
        S["subtitle"]))
    story.append(sp(5))

    # contact row
    contacts = [
        ("📞", "+966 54 296 6343"),
        ("✉", "eng.altieb@gmail.com"),
        ("in", "LinkedIn"),
        ("wa", "WhatsApp"),
        ("f",  "Facebook"),
        ("𝕏",  "X / Twitter"),
        ("📸", "Instagram"),
        ("♪",  "TikTok"),
    ]
    contact_data = [[
        Paragraph(f'<font color="#94a3b8">{v}</font>', S["contact"])
        for _, v in contacts
    ]]
    ct = Table(contact_data, colWidths=[PW / len(contacts)] * len(contacts))
    ct.setStyle(TableStyle([("ALIGN", (0,0), (-1,-1), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
    story.append(ct)
    story.append(sp(6))
    story.append(hr(INDIGO, 1))
    story.append(sp(8))

    # ── STATS ROW ─────────────────────────────────────────────────────────────
    stats = [
        StatBox("12", "Years Experience", INDIGO),
        StatBox("15", "Certifications & Training", PURPLE),
        StatBox("60", "MV/LV Assets Commissioned", CYAN),
        StatBox("18", "% Utility Cost Reduction", GREEN),
    ]
    stat_w = PW / 4 - 3*mm
    stat_row = Table([[s for s in stats]], colWidths=[stat_w + 2*mm] * 4)
    stat_row.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 2),
        ("RIGHTPADDING", (0,0), (-1,-1), 2),
    ]))
    story.append(stat_row)
    story.append(sp(10))

    # ── TWO-COLUMN LAYOUT ─────────────────────────────────────────────────────
    left_col  = []
    right_col = []

    # ── LEFT: Professional Summary ─────────────────────────────────────────────
    left_col.append(SectionHeader("Professional Summary", INDIGO, 100*mm))
    left_col.append(sp(6))
    left_col.append(Paragraph(
        "A Certified Energy Manager (CEM®) and Certified Measurement &amp; Verification Professional (CMVP®) "
        "with over a decade of experience in electrical and energy engineering. I specialize in project management, "
        "telecom power systems, energy-efficient solutions, and technical operations across diverse infrastructure "
        "environments. Fluent in English and Arabic, committed to driving operational excellence and delivering "
        "measurable results through disciplined engineering practices.",
        ParagraphStyle("body2", fontName="Helvetica", fontSize=8.2, textColor=SLATE_300, leading=13)
    ))
    left_col.append(sp(10))

    # ── LEFT: Experience ──────────────────────────────────────────────────────
    left_col.append(SectionHeader("Experience", INDIGO, 100*mm))
    left_col.append(sp(6))

    exp = [
        ("2019 – Present", "Electrical Project Engineer", "ACES · Riyadh", [
            "Energy Manager &amp; efficiency designer",
            "O&amp;M Engineer for Mobily ENM Managed Services",
            "O&amp;M Engineer for STC COW Managed Services",
            "Developed technical troubleshooting &amp; maintenance documentation",
            "Improved telecom passive infrastructure performance",
            "Mentored junior engineers",
        ]),
        ("2018 – 2019", "Electrical Project Engineer", "Absar · Riyadh", [
            "Executed SEC unified-contract builds for 60+ MV/LV assets",
            "Installed RMUs, transformers, and mini-pillars",
            "Full commissioning &amp; SEC handover",
            "SCADA monitoring &amp; integration",
        ]),
        ("2017 – 2018", "Electrical Engineer", "BEMCO", [
            "Preventive maintenance for 11kV distribution networks",
            "Developed standardized testing &amp; inspection manuals",
            "Handled NCR resolutions &amp; technical documentation",
        ]),
        ("2012 – 2017", "Electrical Engineer", "SEC Thermal Generation · Sudan", [
            "Operations for 200 MW thermal generation block",
            "Wastewater treatment (PH meters / OC 4000 DCS)",
            "Maintenance for 11kV distribution systems",
        ]),
    ]

    for date, title, company, bullets in exp:
        left_col.append(Paragraph(date, S["job_date"]))
        left_col.append(Paragraph(title, S["job_title"]))
        left_col.append(Paragraph(company, S["job_company"]))
        left_col.append(sp(2))
        for b in bullets:
            left_col.append(Paragraph(f"· {b}", S["bullet"]))
        left_col.append(sp(7))

    # ── LEFT: Key Projects ────────────────────────────────────────────────────
    left_col.append(SectionHeader("Key Projects", PURPLE, 100*mm))
    left_col.append(sp(6))

    projects = [
        ("STC COW Network", "O&amp;M + energy optimization across 600+ telecom sites nationwide", "#6366f1"),
        ("Mobily ENM Managed Services", "Full O&amp;M, facility support &amp; CAFM/BMS integration", "#a855f7"),
        ("Data Center Energy Audit", "PUE improvement &amp; energy savings assessment", "#22d3ee"),
        ("SEC Unified Contract", "60+ MV/LV installations &amp; full SCADA commissioning", "#4ade80"),
        ("PP12 Thermal Generation", "Operations of 200 MW plant with 11kV switching &amp; DCS control", "#fb923c"),
        ("AI CO2 Dashboard", "ML anomaly detection &amp; CO2 footprint tracking dashboards", "#f472b6"),
    ]

    for pname, pdesc, pcol in projects:
        left_col.append(Paragraph(f'<font color="{pcol}">&#9658;</font> <b>{pname}</b>',
            ParagraphStyle("pb", fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE, leading=12)))
        left_col.append(Paragraph(pdesc, 
            ParagraphStyle("pd", fontName="Helvetica", fontSize=8, textColor=SLATE_400, leading=11, leftIndent=10)))
        left_col.append(sp(5))

    # ── RIGHT: Skills ─────────────────────────────────────────────────────────
    bar_w = 78*mm

    right_col.append(SectionHeader("Power Systems", INDIGO, 78*mm))
    right_col.append(sp(6))
    ps_skills = [("HV/MV/LV Engineering", 95), ("SCADA / DCS / PLC", 92), ("Energy Auditing (CEM®)", 90), ("Commissioning & Testing", 88)]
    for label, pct in ps_skills:
        right_col.append(SkillBar(label, pct, INDIGO, bar_w))
        right_col.append(sp(4))
    right_col.append(sp(8))

    right_col.append(SectionHeader("AI & Data", PURPLE, 78*mm))
    right_col.append(sp(6))
    ai_skills = [("Power BI / DAX", 92), ("Python / ML", 88), ("SQL Server", 85), ("Data Dashboards", 87)]
    for label, pct in ai_skills:
        right_col.append(SkillBar(label, pct, PURPLE, bar_w))
        right_col.append(sp(4))
    right_col.append(sp(8))

    right_col.append(SectionHeader("Frontend", CYAN, 78*mm))
    right_col.append(sp(6))
    fe_skills = [("React / Next.js", 95), ("TypeScript", 90), ("Tailwind CSS", 98)]
    for label, pct in fe_skills:
        right_col.append(SkillBar(label, pct, CYAN, bar_w))
        right_col.append(sp(4))
    right_col.append(sp(8))

    right_col.append(SectionHeader("Backend", GREEN, 78*mm))
    right_col.append(sp(6))
    be_skills = [("Node.js", 88), ("PostgreSQL", 85), ("GraphQL", 82)]
    for label, pct in be_skills:
        right_col.append(SkillBar(label, pct, GREEN, bar_w))
        right_col.append(sp(4))
    right_col.append(sp(8))

    right_col.append(SectionHeader("Design", PINK, 78*mm))
    right_col.append(sp(6))
    ds_skills = [("Figma", 96), ("Power BI", 92), ("UI Systems", 94)]
    for label, pct in ds_skills:
        right_col.append(SkillBar(label, pct, PINK, bar_w))
        right_col.append(sp(4))
    right_col.append(sp(8))

    # ── RIGHT: Certifications ─────────────────────────────────────────────────
    right_col.append(SectionHeader("Certifications", colors.HexColor("#fb923c"), 78*mm))
    right_col.append(sp(6))
    certs = [
        "CMVP® — Certified Measurement & Verification Professional",
        "CEM® — Certified Energy Manager",
        "Machine Learning with Python",
        "Power BI Essential Training",
        "LEED Green Associate",
        "Learning Excel: Data Analysis",
        "Quality Engineering",
        "SCADA / PLC / DCS / RTU",
    ]
    for cert in certs:
        right_col.append(Paragraph(f"✦ {cert}", 
            ParagraphStyle("cert", fontName="Helvetica", fontSize=7.8, textColor=SLATE_300, leading=12, leftIndent=6)))
        right_col.append(sp(1))
    right_col.append(sp(8))

    # ── RIGHT: Education ──────────────────────────────────────────────────────
    right_col.append(SectionHeader("Education", INDIGO, 78*mm))
    right_col.append(sp(6))
    right_col.append(Paragraph("B.Sc. Electronic Engineering (Control)", S["job_title"]))
    right_col.append(Paragraph("El Neelain University", S["job_company"]))
    right_col.append(Paragraph("2007 – 2012", S["job_date"]))
    right_col.append(sp(8))

    # ── RIGHT: Languages & Memberships ───────────────────────────────────────
    right_col.append(SectionHeader("Languages", CYAN, 78*mm))
    right_col.append(sp(6))
    right_col.append(Paragraph("Arabic — Native", S["label"]))
    right_col.append(Paragraph("English — Professional", S["label"]))
    right_col.append(sp(8))

    right_col.append(SectionHeader("Memberships", PURPLE, 78*mm))
    right_col.append(sp(6))
    right_col.append(Paragraph("Saudi Council of Engineers (SCE)", S["label"]))
    right_col.append(Paragraph("Sudanese Engineers Association (SEA)", S["label"]))
    right_col.append(sp(8))

    # ── RIGHT: Availability ───────────────────────────────────────────────────
    right_col.append(SectionHeader("Availability", GREEN, 78*mm))
    right_col.append(sp(6))
    right_col.append(Paragraph("Sun–Thu: 8:00 AM – 6:00 PM", S["label"]))
    right_col.append(Paragraph("Weekends: On-call for urgent interventions", S["small"]))
    right_col.append(Paragraph("Ready for short-notice regional travel", S["small"]))

    # ── Combine columns ───────────────────────────────────────────────────────
    col_table = Table(
        [[left_col, right_col]],
        colWidths=[103*mm, 82*mm],
    )
    col_table.setStyle(TableStyle([
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING",(0,0), (-1,-1), 0),
        ("RIGHTPADDING",(0,0), (0,-1), 6),
    ]))
    story.append(col_table)

    # ── Key Accomplishments (full width) ──────────────────────────────────────
    story.append(sp(8))
    story.append(hr(INDIGO, 1))
    story.append(sp(8))
    story.append(SectionHeader("Key Accomplishments", INDIGO, PW))
    story.append(sp(6))
    accomplishments = [
        "Reduced nationwide telecom site utility costs by up to <b>18%</b> through multi-phase energy optimization.",
        "Delivered O&amp;M coverage for STC COW &amp; Mobily ENM networks with proactive outage prevention.",
        "Authored troubleshooting guides and automation routines reducing incident resolution time by <b>30%</b>.",
        "Commissioned <b>60+ MV/LV assets</b> under SEC unified contracts with full SCADA integration.",
        "Developed AI-driven Energy &amp; Environmental Dashboard tracking CO₂ emissions and power efficiency.",
        "Version-controlled documentation and templates using Git/GitHub workflows across multi-site networks.",
    ]
    acc_data = [[
        Paragraph(f"✦ {a}", ParagraphStyle("acc", fontName="Helvetica", fontSize=8.5,
            textColor=SLATE_300, leading=13))
        for a in accomplishments[:3]
    ], [
        Paragraph(f"✦ {a}", ParagraphStyle("acc", fontName="Helvetica", fontSize=8.5,
            textColor=SLATE_300, leading=13))
        for a in accomplishments[3:]
    ]]
    acc_table = Table(
        list(zip(
            [Paragraph(f"✦ {a}", ParagraphStyle("acc", fontName="Helvetica", fontSize=8.5, textColor=SLATE_300, leading=13)) for a in accomplishments[:3]],
            [Paragraph(f"✦ {a}", ParagraphStyle("acc", fontName="Helvetica", fontSize=8.5, textColor=SLATE_300, leading=13)) for a in accomplishments[3:]],
        )),
        colWidths=[PW/2 - 3*mm, PW/2 - 3*mm],
    )
    acc_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (0,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(acc_table)

    # ── Footer quote ──────────────────────────────────────────────────────────
    story.append(sp(10))
    story.append(hr(SLATE_500))
    story.append(sp(6))
    story.append(Paragraph(
        '"You never change things by fighting the existing reality. '
        'To change something, build a new model that makes the old one obsolete."',
        S["quote"]
    ))
    story.append(Paragraph("— R. Buckminster Fuller", S["quote"]))
    story.append(sp(4))
    story.append(Paragraph("© 2025 Eng. Bannaga Altieb Abdul Muhsin · eng.altieb@gmail.com · +966 54 296 6343", S["quote"]))

    # ── Final build ───────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=dark_bg, onLaterPages=dark_bg)
    print("PDF generated: assets/Bannaga_CV.pdf")


if __name__ == "__main__":
    build_cv()
