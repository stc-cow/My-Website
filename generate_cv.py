"""
Modern ATS-friendly CV — Bannaga Altieb Abdul Muhsin
Uses ReportLab multi-frame layout: header frame + sidebar frame + main frame
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, FrameBreak,
    Paragraph, Spacer, HRFlowable, KeepTogether, Flowable, Table, TableStyle
)

W, H = A4

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = colors.HexColor("#0d1117")
BG_HDR   = colors.HexColor("#161b27")
BG_SB    = colors.HexColor("#13182a")
INDIGO   = colors.HexColor("#6366f1")
PURPLE   = colors.HexColor("#8b5cf6")
CYAN     = colors.HexColor("#22d3ee")
GREEN    = colors.HexColor("#4ade80")
ORANGE   = colors.HexColor("#fb923c")
PINK     = colors.HexColor("#f472b6")
WHITE    = colors.HexColor("#f1f5f9")
SL3      = colors.HexColor("#cbd5e1")
SL4      = colors.HexColor("#94a3b8")
SL5      = colors.HexColor("#64748b")
SL6      = colors.HexColor("#334155")

# ── Dimensions ────────────────────────────────────────────────────────────────
HDR_H  = 42 * mm
SB_W   = 64 * mm
PAD    = 6  * mm
BODY_H = H - HDR_H - 2 * mm
MN_W   = W - SB_W - 3 * mm        # main col usable width
SB_IW  = SB_W - 2 * PAD           # sidebar inner width
MN_IW  = MN_W - PAD - 8 * mm      # main inner width

# ── Custom Flowables ──────────────────────────────────────────────────────────
class SkillBar(Flowable):
    def __init__(self, label, pct, bar_color, width):
        super().__init__()
        self.label = label; self.pct = pct
        self.bar_color = bar_color; self.width = width
        self._height = 16

    def draw(self):
        c = self.canv
        c.setFont("Helvetica", 7.5); c.setFillColor(SL3)
        c.drawString(0, 8, self.label)
        c.setFillColor(SL5)
        c.drawRightString(self.width, 8, f"{self.pct}%")
        c.setFillColor(SL6)
        c.roundRect(0, 2, self.width, 4, 2, fill=1, stroke=0)
        c.setFillColor(self.bar_color)
        c.roundRect(0, 2, self.width * self.pct / 100, 4, 2, fill=1, stroke=0)


class PillHeader(Flowable):
    def __init__(self, text, accent, width):
        super().__init__()
        self.text = text; self.accent = accent
        self.width = width; self._height = 17

    def draw(self):
        c = self.canv
        c.setFillColor(self.accent)
        c.roundRect(0, 0, self.width, self._height, 4, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 8); c.setFillColor(WHITE)
        c.drawCentredString(self.width / 2, 5, self.text.upper())


class AccentHeader(Flowable):
    def __init__(self, text, accent, width):
        super().__init__()
        self.text = text; self.accent = accent
        self.width = width; self._height = 20

    def draw(self):
        c = self.canv
        c.setFillColor(self.accent)
        c.rect(0, 17, self.width, 2, fill=1, stroke=0)
        c.rect(0, 0, 24, 2, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 10); c.setFillColor(WHITE)
        c.drawString(0, 3, self.text.upper())


# ── Style helpers ─────────────────────────────────────────────────────────────
def ps(name, **kw):
    d = dict(fontName="Helvetica", fontSize=8.5, textColor=SL3, leading=12)
    d.update(kw)
    return ParagraphStyle(name, **d)

def sp(h=4):
    return Spacer(1, h)

def sbsec(txt, col, w):
    return [PillHeader(txt, col, w), sp(5)]

def mnsec(txt, col, w):
    return [AccentHeader(txt, col, w), sp(5)]


# ── Page template ─────────────────────────────────────────────────────────────
def make_template(doc):
    # Frame 1: header (full width)
    f_hdr = Frame(0, H - HDR_H, W, HDR_H,
                  leftPadding=10*mm, rightPadding=10*mm,
                  topPadding=6*mm, bottomPadding=3*mm, id="header")
    # Frame 2: sidebar
    f_sb = Frame(0, 0, SB_W, BODY_H,
                 leftPadding=PAD, rightPadding=PAD,
                 topPadding=4*mm, bottomPadding=4*mm, id="sidebar")
    # Frame 3: main
    f_mn = Frame(SB_W + 2*mm, 0, W - SB_W - 2*mm, BODY_H,
                 leftPadding=PAD, rightPadding=8*mm,
                 topPadding=4*mm, bottomPadding=4*mm, id="main")

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BG)
        canvas.rect(0, 0, W, H, fill=1, stroke=0)
        # header bg
        canvas.setFillColor(BG_HDR)
        canvas.rect(0, H - HDR_H, W, HDR_H, fill=1, stroke=0)
        # top accent line
        canvas.setFillColor(INDIGO)
        canvas.rect(0, H - 2.5, W * 0.55, 2.5, fill=1, stroke=0)
        canvas.setFillColor(PURPLE)
        canvas.rect(W * 0.55, H - 2.5, W * 0.45, 2.5, fill=1, stroke=0)
        # sidebar bg
        canvas.setFillColor(BG_SB)
        canvas.rect(0, 0, SB_W, BODY_H, fill=1, stroke=0)
        # divider
        canvas.setStrokeColor(SL6)
        canvas.setLineWidth(0.5)
        canvas.line(SB_W, 0, SB_W, BODY_H)
        canvas.restoreState()

    return PageTemplate(id="cv", frames=[f_hdr, f_sb, f_mn], onPage=on_page)


# ── Build ─────────────────────────────────────────────────────────────────────
def build():
    doc = BaseDocTemplate("assets/Bannaga_CV.pdf", pagesize=A4,
                          leftMargin=0, rightMargin=0,
                          topMargin=0, bottomMargin=0)
    doc.addPageTemplates([make_template(doc)])

    N  = ps("n",  fontName="Helvetica-Bold", fontSize=21, textColor=WHITE, leading=25, alignment=TA_CENTER)
    TL = ps("tl", fontName="Helvetica",      fontSize=10, textColor=INDIGO, leading=14, alignment=TA_CENTER)
    CR = ps("cr", fontName="Helvetica",      fontSize=7.5, textColor=SL4, leading=11, alignment=TA_CENTER)
    CN = ps("cn", fontName="Helvetica",      fontSize=7,   textColor=SL4, leading=11, alignment=TA_CENTER)
    BD = ps("bd", fontName="Helvetica",      fontSize=8.2, textColor=SL3, leading=12)
    BU = ps("bu", fontName="Helvetica",      fontSize=8.2, textColor=SL3, leading=12, leftIndent=8)
    LB = ps("lb", fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE, leading=12)
    SM = ps("sm", fontName="Helvetica",      fontSize=7.5, textColor=SL4, leading=11)
    JT = ps("jt", fontName="Helvetica-Bold", fontSize=9,   textColor=WHITE, leading=13)
    JC = ps("jc", fontName="Helvetica-Bold", fontSize=8,   textColor=INDIGO, leading=12)
    JD = ps("jd", fontName="Helvetica-Oblique", fontSize=7.5, textColor=SL5, leading=11)
    PT = ps("pt", fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE, leading=12)
    PD = ps("pd", fontName="Helvetica",      fontSize=8,   textColor=SL4, leading=11, leftIndent=8)
    CT = ps("ct", fontName="Helvetica",      fontSize=7.5, textColor=SL3, leading=11, leftIndent=4)
    QT = ps("qt", fontName="Helvetica-Oblique", fontSize=7.5, textColor=SL5, leading=12, alignment=TA_CENTER)
    AC = ps("ac", fontName="Helvetica",      fontSize=8,   textColor=SL3, leading=12)

    story = []

    # ══════════════════════ HEADER FRAME ══════════════════════════════════════
    story += [
        Paragraph("Bannaga Altieb Abdul Muhsin", N),
        sp(3),
        Paragraph("Electrical Project Engineer  ·  Riyadh, Saudi Arabia", TL),
        sp(2),
        Paragraph("CEM®  ·  CMVP®  ·  LEED Green Associate  ·  Telecom &amp; Industrial Infrastructure  ·  Energy Optimization  ·  O&amp;M Excellence", CR),
        sp(4),
        Paragraph(
            "+966 54 296 6343  ·  eng.altieb@gmail.com  ·  LinkedIn: bannaga-abdalmuhsin  ·  "
            "WhatsApp: +966 54 296 6343  ·  Facebook: bannga.altieb  ·  X: AltiebBannaga  ·  "
            "Instagram: bannga.altieb  ·  TikTok: bannagaaltieb94", CN),
        FrameBreak(),
    ]

    # ══════════════════════ SIDEBAR FRAME ═════════════════════════════════════
    W2 = SB_IW

    def sb(*items): story.extend(items)

    def skill_group(title, col, skills):
        sb(*sbsec(title, col, W2))
        for lbl, pct in skills:
            sb(SkillBar(lbl, pct, col, W2), sp(3))
        sb(sp(7))

    skill_group("Power Systems", INDIGO, [
        ("HV/MV/LV Engineering", 95), ("SCADA / DCS / PLC", 92),
        ("Energy Auditing (CEM®)", 90), ("Commissioning & Testing", 88),
        ("Power System Protection", 85),
    ])
    skill_group("AI & Data", PURPLE, [
        ("Power BI / DAX", 92), ("Python / ML", 88),
        ("SQL Server", 85), ("Data Dashboards", 87),
    ])
    skill_group("Frontend", CYAN, [
        ("React / Next.js", 95), ("TypeScript", 90), ("Tailwind CSS", 98),
    ])
    skill_group("Backend", GREEN, [
        ("Node.js", 88), ("PostgreSQL", 85), ("GraphQL", 82),
    ])
    skill_group("Design", PINK, [
        ("Figma", 96), ("Power BI Visuals", 92), ("UI Systems", 94),
    ])

    # Education
    sb(*sbsec("Education", ORANGE, W2))
    sb(Paragraph("B.Sc. Electronic Engineering", LB),
       Paragraph("(Control Engineering)", SM),
       Paragraph("El Neelain University · 2007–2012", SM),
       sp(7))

    # Certifications
    sb(*sbsec("Certifications", INDIGO, W2))
    for c in [
        "CMVP® — Measurement & Verification",
        "CEM® — Certified Energy Manager",
        "Machine Learning with Python",
        "Power BI Essential Training",
        "LEED Green Associate",
        "Learning Excel: Data Analysis",
        "Quality Engineering",
        "SCADA / PLC / DCS / RTU",
        "Non-Technical Skills of Data Scientists",
    ]:
        sb(Paragraph(f"✓ {c}", CT), sp(1))
    sb(sp(7))

    # Languages
    sb(*sbsec("Languages", CYAN, W2))
    sb(Paragraph("Arabic — Native", LB),
       Paragraph("English — Professional", LB),
       sp(7))

    # Memberships
    sb(*sbsec("Memberships", PURPLE, W2))
    sb(Paragraph("Saudi Council of Engineers (SCE)", SM),
       Paragraph("Sudanese Engineers Association (SEA)", SM),
       sp(7))

    # Availability
    sb(*sbsec("Availability", GREEN, W2))
    sb(Paragraph("Sun–Thu: 8:00 AM – 6:00 PM", SM),
       Paragraph("Weekends: On-call for urgent needs", SM),
       Paragraph("Open to short-notice regional travel", SM),
       sp(7))

    # Interests
    sb(*sbsec("Interests", ORANGE, W2))
    for h in ["Electrical Power Systems", "Energy Efficiency",
              "Automation & Control", "Data Analysis",
              "Innovation & New Tech"]:
        sb(Paragraph(f"· {h}", CT), sp(1))

    story.append(FrameBreak())

    # ══════════════════════ MAIN FRAME ════════════════════════════════════════
    W3 = MN_IW

    def mn(*items): story.extend(items)

    # Stats row inside main frame
    stats = Table([[
        Paragraph("12+",  ps("sn", fontName="Helvetica-Bold", fontSize=14, textColor="#6366f1", leading=16, alignment=TA_CENTER)),
        Paragraph("Years\nExp.", ps("sl", fontSize=7, textColor=SL4, leading=9, alignment=TA_CENTER)),
        Paragraph("15+",  ps("sn", fontName="Helvetica-Bold", fontSize=14, textColor="#8b5cf6", leading=16, alignment=TA_CENTER)),
        Paragraph("Certs\n& Training", ps("sl", fontSize=7, textColor=SL4, leading=9, alignment=TA_CENTER)),
        Paragraph("60+",  ps("sn", fontName="Helvetica-Bold", fontSize=14, textColor="#22d3ee", leading=16, alignment=TA_CENTER)),
        Paragraph("MV/LV\nAssets", ps("sl", fontSize=7, textColor=SL4, leading=9, alignment=TA_CENTER)),
        Paragraph("18%",  ps("sn", fontName="Helvetica-Bold", fontSize=14, textColor="#4ade80", leading=16, alignment=TA_CENTER)),
        Paragraph("Cost\nReduction", ps("sl", fontSize=7, textColor=SL4, leading=9, alignment=TA_CENTER)),
    ]], colWidths=[16*mm, 22*mm, 16*mm, 22*mm, 16*mm, 22*mm, 16*mm, 22*mm])
    stats.setStyle(TableStyle([
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",  (0,0), (-1,-1), 1),
        ("RIGHTPADDING", (0,0), (-1,-1), 1),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ("BACKGROUND",   (0,0), (-1,-1), colors.HexColor("#1e2638")),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [4,4,4,4]),
    ]))
    mn(stats, sp(8))

    # Professional Summary
    mn(*mnsec("Professional Summary", INDIGO, W3))
    mn(Paragraph(
        "A Certified Energy Manager (CEM®) and Certified Measurement &amp; Verification Professional (CMVP®) "
        "with over a decade of experience in electrical and energy engineering. Specializes in project management, "
        "telecom power systems, energy-efficient solutions, and technical operations across diverse infrastructure. "
        "Strong expertise in data collection, energy analysis, facilities management, structured reporting, and AI-driven "
        "dashboards. Holds a B.Sc. in Electronic Control Engineering with certifications in LEED Green Associate, "
        "SCADA systems, Machine Learning, and Power BI. Fluent in English and Arabic. Committed to driving operational "
        "excellence, improving system reliability, and delivering measurable results through disciplined engineering.",
        BD), sp(8))

    # AI & Development
    mn(*mnsec("AI & Development", PURPLE, W3))
    mn(Paragraph("<b>AI &amp; Automation</b>", LB))
    for b in [
        "Designed Python-based automation to streamline energy performance reporting and KPI tracking.",
        "Developed ML-based anomaly alerts for telecom site power consumption behavior.",
        "Built governance-ready Energy &amp; Environmental dashboards for CO2 footprint monitoring.",
        "Applied Power BI, SQL Server, and DAX to model operational trends across multi-site networks.",
    ]:
        mn(Paragraph(f"▸ {b}", BU))
    mn(sp(4), Paragraph("<b>Development &amp; Tools</b>", LB))
    for b in [
        "Created troubleshooting guides and diagnostic scripts for SCADA / PLC / DCS systems.",
        "Documented API-style checklists to standardize field data capture and site integrations.",
        "Version-controlled documentation and engineering templates using Git/GitHub workflows.",
    ]:
        mn(Paragraph(f"▸ {b}", BU))
    mn(sp(8))

    # Experience
    mn(*mnsec("Experience", INDIGO, W3))
    exp = [
        ("2019 – Present", "Electrical Project Engineer", "ACES · Riyadh", [
            "Energy Manager &amp; efficiency designer across STC COW and Mobily ENM networks.",
            "O&amp;M Engineer for Mobily ENM Managed Services — full facility &amp; CAFM/BMS oversight.",
            "O&amp;M Engineer for STC COW Managed Services — 600+ nationwide telecom sites.",
            "Developed technical troubleshooting &amp; preventive maintenance documentation.",
            "Designed energy optimization initiatives achieving up to 18% utility cost reduction.",
            "Mentored junior engineers and standardized field engineering practices.",
        ]),
        ("2018 – 2019", "Electrical Project Engineer", "Absar · Riyadh", [
            "Executed SEC unified-contract builds for 60+ MV/LV electrical assets.",
            "Installed RMUs, transformers, LV switchgear, and mini-pillars.",
            "Full commissioning, testing, and zero-defect SEC handover documentation.",
            "SCADA monitoring, integration, and control system setup.",
        ]),
        ("2017 – 2018", "Electrical Engineer", "BEMCO", [
            "Preventive and corrective maintenance for 11kV distribution networks.",
            "Developed standardized testing, inspection, and commissioning manuals.",
            "Managed NCR resolutions and technical documentation workflows.",
        ]),
        ("2012 – 2017", "Electrical Engineer", "SEC Thermal Generation · Sudan", [
            "Operations and maintenance for a 200 MW thermal generation block.",
            "Managed wastewater treatment systems (PH meters / OC 4000 DCS).",
            "Preventive maintenance and fault management for 11kV distribution systems.",
        ]),
    ]
    for date, title, co, bullets in exp:
        mn(KeepTogether([
            Paragraph(date, JD),
            Paragraph(title, JT),
            Paragraph(co, JC),
            sp(2),
            *[Paragraph(f"▸ {b}", BU) for b in bullets],
            sp(7),
        ]))

    # Key Projects
    mn(*mnsec("Key Projects", PURPLE, W3))
    projects = [
        ("STC COW Network — O&amp;M + Energy Optimization",
         "End-to-end O&amp;M for 600+ telecom sites. Achieved up to 18% utility cost reduction through systematic energy auditing."),
        ("Mobily ENM Managed Services",
         "Full O&amp;M and facility operations including CAFM/BMS integration and outage prevention."),
        ("Mobily Data Center Energy Audit",
         "Comprehensive energy audit delivering measurable PUE improvements across critical DC infrastructure."),
        ("SEC Unified Contract — MV/LV Commissioning",
         "Installation and commissioning of 60+ MV/LV assets with full SCADA integration and SEC handover."),
        ("PP12 Thermal Generation — 200 MW Plant Operations",
         "Day-to-day operations including 11kV switching, safety routines, and DCS-based environmental monitoring."),
        ("AI CO2 Dashboard — Energy &amp; Environmental Monitoring",
         "ML anomaly detection and CO2 footprint tracking dashboards using Python, Power BI, and SQL Server."),
    ]
    for title, desc in projects:
        mn(KeepTogether([
            Paragraph(f"▸ <b>{title}</b>", PT),
            Paragraph(desc, PD),
            sp(4),
        ]))
    mn(sp(4))

    # Key Accomplishments
    mn(*mnsec("Key Accomplishments", GREEN, W3))
    for a in [
        "Reduced nationwide telecom utility costs by up to <b>18%</b> through multi-phase energy optimization.",
        "Delivered O&amp;M for STC COW &amp; Mobily ENM networks with proactive outage prevention.",
        "Authored automation routines reducing incident resolution time by <b>30%</b>.",
        "Commissioned <b>60+ MV/LV assets</b> under SEC unified contracts with zero-defect SCADA handover.",
        "Built AI-driven CO2 &amp; power efficiency dashboard across all STC COW sites.",
        "Version-controlled all engineering templates using Git/GitHub workflows.",
    ]:
        mn(Paragraph(f"✦ {a}", AC), sp(3))

    mn(sp(8))
    mn(HRFlowable(width=W3, thickness=0.5, color=SL6))
    mn(sp(5))
    mn(Paragraph(
        '"You never change things by fighting the existing reality. '
        'Build a new model that makes the old one obsolete." — R. Buckminster Fuller', QT))
    mn(sp(3))
    mn(Paragraph("© 2025 Eng. Bannaga Altieb Abdul Muhsin · eng.altieb@gmail.com · +966 54 296 6343", QT))

    doc.build(story)
    print("✓ PDF saved: assets/Bannaga_CV.pdf")


if __name__ == "__main__":
    build()
