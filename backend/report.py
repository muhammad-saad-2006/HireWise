import os
import io
import tempfile
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image
)

import plotly.graph_objects as go

_BRAND_BLUE   = colors.HexColor("#1A56DB")
_BRAND_DARK   = colors.HexColor("#1E2A3A")
_PASS_GREEN   = colors.HexColor("#0E9F6E")
_FAIL_RED     = colors.HexColor("#F05252")
_LIGHT_GREY   = colors.HexColor("#F3F4F6")
_MID_GREY     = colors.HexColor("#9CA3AF")
_WHITE        = colors.white

# CHART GENERATION
def _make_bar_chart(engine_result: dict, role: str) -> str:
    passed = engine_result.get("rules_passed", [])
    failed = engine_result.get("rules_failed", [])

    labels  = []
    values  = []
    bar_colors = []

    for r in passed:
        labels.append(r["description"][:45])
        values.append(r["weight"])
        bar_colors.append("#0E9F6E")

    for r in failed:
        labels.append(r["description"][:45])
        values.append(r["weight"])
        bar_colors.append("#F05252")

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=bar_colors,
        text=[f"{v:.0%}" for v in values],
        textposition="outside",
    ))

    fig.update_layout(
        title=f"Rule Evaluation — {role.title()}",
        title_font_size=14,
        xaxis_title="Rule Weight",
        xaxis=dict(range=[0, 1.15], tickformat=".0%"),
        height=max(350, len(labels) * 28),
        width=700,
        margin=dict(l=20, r=40, t=50, b=30),
        paper_bgcolor="white",
        plot_bgcolor="#F9FAFB",
        font=dict(size=11),
    )

    # Save to temp PNG
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.write_image(tmp.name)
    tmp.close()
    return tmp.name


def _make_score_gauge(score: float) -> str:
    color = "#0E9F6E" if score >= 0.90 else "#F05252" if score < 0.65 else "#F59E0B"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score * 100, 1),
        title={"text": "Final Score", "font": {"size": 16}},
        number={"suffix": "%", "font": {"size": 28}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color},
            "bgcolor": "white",
            "steps": [
                {"range": [0,  65], "color": "#FEE2E2"},
                {"range": [65, 90], "color": "#FEF3C7"},
                {"range": [90, 100], "color": "#D1FAE5"},
            ],
            "threshold": {
                "line": {"color": "#1A56DB", "width": 3},
                "thickness": 0.75,
                "value": 90,
            },
        },
    ))

    fig.update_layout(
        width=380, height=260,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="white",
    )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.write_image(tmp.name)
    tmp.close()
    return tmp.name

# PDF BUILDER
def generate_report(
    candidate_facts: dict,
    engine_result:   dict,
    score:           float,
    tips:            list,
    role:            str,
) -> str:
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    email       = candidate_facts.get("email", "candidate").replace("@", "_").replace(".", "_")
    filename    = f"report_{email}_{timestamp}.pdf"
    output_path = os.path.join(reports_dir, filename)

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "HWTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=_BRAND_DARK,
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    style_subtitle = ParagraphStyle(
        "HWSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=_MID_GREY,
        spaceAfter=2,
        alignment=TA_CENTER,
    )
    style_section = ParagraphStyle(
        "HWSection",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=_BRAND_BLUE,
        spaceBefore=14,
        spaceAfter=6,
        borderPad=2,
    )
    style_body = ParagraphStyle(
        "HWBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=_BRAND_DARK,
        spaceAfter=4,
        leading=14,
    )
    style_tip = ParagraphStyle(
        "HWTip",
        parent=styles["Normal"],
        fontSize=10,
        textColor=_BRAND_DARK,
        leftIndent=12,
        spaceAfter=5,
        leading=14,
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
    )

    story = []

    story.append(Paragraph("HireWise", style_title))
    story.append(Paragraph("Candidate Evaluation Report", style_subtitle))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=_BRAND_BLUE))
    story.append(Spacer(1, 0.4*cm))

    passed      = score >= 0.90
    status_text = "INTERVIEW INVITED" if passed else "IMPROVEMENT REQUIRED"
    status_color = _PASS_GREEN if passed else _FAIL_RED

    info_data = [
        ["Email",       candidate_facts.get("email", "N/A")],
        ["Role",        role.title()],
        ["Date",        datetime.now().strftime("%d %B %Y")],
        ["Decision",    Paragraph(
            f'<font color="{"#0E9F6E" if passed else "#F05252"}"><b>{status_text}</b></font>',
            style_body
        )],
    ]

    info_table = Table(info_data, colWidths=[4*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (0, -1), _LIGHT_GREY),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",   (0, 0), (0, -1), _BRAND_DARK),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_WHITE, _LIGHT_GREY]),
        ("GRID",        (0, 0), (-1, -1), 0.5, _MID_GREY),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Evaluation Score", style_section))
    try:
        gauge_path = _make_score_gauge(score)
        story.append(Image(gauge_path, width=9.5*cm, height=6.5*cm, hAlign="CENTER"))
        story.append(Spacer(1, 0.3*cm))
    except Exception as e:
        print(f"[report] Gauge chart failed: {e}")
        story.append(Paragraph(f"Final Score: {score:.1%}", style_body))

    story.append(Paragraph("Rule-by-Rule Breakdown", style_section))
    try:
        bar_path = _make_bar_chart(engine_result, role)
        chart_height = max(8*cm, len(engine_result.get("rules_passed", []) +
                                     engine_result.get("rules_failed", [])) * 0.7*cm)
        story.append(Image(bar_path, width=17*cm, height=chart_height, hAlign="CENTER"))
        story.append(Spacer(1, 0.3*cm))
    except Exception as e:
        print(f"[report] Bar chart failed: {e}")

    passed_rules = engine_result.get("rules_passed", [])
    if passed_rules:
        story.append(Paragraph("Rules Passed", style_section))
        table_data = [["Rule", "Description", "Weight"]]
        for r in passed_rules:
            table_data.append([
                r.get("rule", ""),
                r.get("description", ""),
                f"{r.get('weight', 0):.0%}",
            ])
        t = Table(table_data, colWidths=[3.5*cm, 11*cm, 2*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), _PASS_GREEN),
            ("TEXTCOLOR",     (0, 0), (-1, 0), _WHITE),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [_WHITE, _LIGHT_GREY]),
            ("GRID",          (0, 0), (-1, -1), 0.4, _MID_GREY),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.4*cm))

    failed_rules = engine_result.get("rules_failed", [])
    if failed_rules:
        story.append(Paragraph("Rules Failed — Areas to Improve", style_section))
        table_data = [["Rule", "Description", "Weight"]]
        for r in failed_rules:
            table_data.append([
                r.get("rule", ""),
                r.get("description", ""),
                f"{r.get('weight', 0):.0%}",
            ])
        t = Table(table_data, colWidths=[3.5*cm, 11*cm, 2*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), _FAIL_RED),
            ("TEXTCOLOR",     (0, 0), (-1, 0), _WHITE),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [_WHITE, _LIGHT_GREY]),
            ("GRID",          (0, 0), (-1, -1), 0.4, _MID_GREY),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.4*cm))

    if tips:
        story.append(Paragraph("Personalised Improvement Tips", style_section))
        story.append(Paragraph(
            "Based on your evaluation, here are targeted recommendations to strengthen your profile:",
            style_body
        ))
        story.append(Spacer(1, 0.2*cm))
        for i, tip in enumerate(tips, 1):
            story.append(Paragraph(f"{i}.  {tip}", style_tip))
        story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Extracted CV Summary", style_section))
    cv_data = [
        ["Education",   candidate_facts.get("education_level", "N/A").title()],
        ["Experience",  f"{candidate_facts.get('years_experience', 0)} years"],
        ["Skills",      ", ".join(candidate_facts.get("skills", []))],
        ["Projects",    str(len(candidate_facts.get("projects", []))) + " detected"],
        ["Certifications", str(len(candidate_facts.get("certifications", []))) + " detected"],
    ]
    cv_table = Table(cv_data, colWidths=[4*cm, 12*cm])
    cv_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (0, -1), _LIGHT_GREY),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("GRID",        (0, 0), (-1, -1), 0.4, _MID_GREY),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_WHITE, _LIGHT_GREY]),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(cv_table)
    story.append(Spacer(1, 0.5*cm))

    story.append(HRFlowable(width="100%", thickness=1, color=_MID_GREY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Generated by HireWise AI Recruitment System • {datetime.now().strftime('%d %B %Y %H:%M')}",
        ParagraphStyle("footer", parent=styles["Normal"],
                       fontSize=8, textColor=_MID_GREY, alignment=TA_CENTER)
    ))

    doc.build(story)

    try:
        if "gauge_path" in dir(): os.unlink(gauge_path)
        if "bar_path"   in dir(): os.unlink(bar_path)
    except Exception:
        pass

    print(f"[report] PDF generated: {output_path}")
    return output_path