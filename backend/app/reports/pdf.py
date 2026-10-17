"""PDF report for the Diagnostic Flash, generated in memory with ReportLab."""

from __future__ import annotations

import io
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ..diagnostic.models import Answers, AssessmentResult, RiskCategory, SystemProfile
from ..diagnostic.questionnaire import QUESTIONS, applicable_answers, option_label

NAVY = colors.HexColor("#1E3A8A")
TEAL = colors.HexColor("#0F9488")
GREY = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")

CATEGORY_COLORS = {
    RiskCategory.OUT_OF_SCOPE: colors.HexColor("#64748B"),
    RiskCategory.MINIMAL: colors.HexColor("#15803D"),
    RiskCategory.TRANSPARENCY: colors.HexColor("#B45309"),
    RiskCategory.HIGH: colors.HexColor("#C2410C"),
    RiskCategory.UNACCEPTABLE: colors.HexColor("#B91C1C"),
}

DISCLAIMER = (
    "Ce rapport est une pré-qualification automatisée fondée sur les déclarations de l'utilisateur et sur "
    "le texte du règlement (UE) 2024/1689 tel qu'adopté. Il ne constitue pas un avis juridique. Les dates "
    "d'application peuvent être modifiées par des actes ultérieurs ; une analyse approfondie par un expert "
    "est recommandée avant toute décision. Conformément à notre politique Zero-Data Retention, aucune "
    "réponse n'est conservée après la génération de ce rapport."
)

_FONT_DIRS = [Path("/usr/share/fonts/truetype/dejavu"), Path("/usr/share/fonts/dejavu")]


def _register_fonts() -> tuple[str, str]:
    """Use DejaVu Sans when available for full Unicode coverage."""
    for directory in _FONT_DIRS:
        regular, bold = directory / "DejaVuSans.ttf", directory / "DejaVuSans-Bold.ttf"
        if regular.exists() and bold.exists():
            if "DejaVuSans" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("DejaVuSans", str(regular)))
                pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(bold)))
                # Map <b> markup in paragraphs to the bold face.
                addMapping("DejaVuSans", 0, 0, "DejaVuSans")
                addMapping("DejaVuSans", 1, 0, "DejaVuSans-Bold")
            return "DejaVuSans", "DejaVuSans-Bold"
    return "Helvetica", "Helvetica-Bold"


def _styles(font: str, bold: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()["Normal"]
    return {
        "title": ParagraphStyle("title", parent=base, fontName=bold, fontSize=20, leading=24, textColor=NAVY, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("subtitle", parent=base, fontName=font, fontSize=11, leading=14, textColor=TEAL, alignment=TA_CENTER),
        "h2": ParagraphStyle("h2", parent=base, fontName=bold, fontSize=13, leading=16, textColor=NAVY, spaceBefore=10, spaceAfter=6),
        "body": ParagraphStyle("body", parent=base, fontName=font, fontSize=9.5, leading=13),
        "small": ParagraphStyle("small", parent=base, fontName=font, fontSize=8, leading=10.5),
        "cell_bold": ParagraphStyle("cell_bold", parent=base, fontName=bold, fontSize=8.5, leading=11),
        "verdict": ParagraphStyle("verdict", parent=base, fontName=bold, fontSize=16, leading=20, textColor=colors.white, alignment=TA_CENTER),
        "verdict_sub": ParagraphStyle("verdict_sub", parent=base, fontName=font, fontSize=10, leading=13, textColor=colors.white, alignment=TA_CENTER),
        "header": ParagraphStyle("header", parent=base, fontName=bold, fontSize=8.5, leading=11, textColor=colors.white),
    }


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(text), style)


def _table(rows: list[list], widths: list[float], header: bool = True) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
        commands += [("BACKGROUND", (0, i), (-1, i), GREY) for i in range(2, len(rows), 2)]
    table.setStyle(TableStyle(commands))
    return table


def _answer_text(question_id: str, value) -> str:
    if isinstance(value, bool):
        return "Oui" if value else "Non"
    if isinstance(value, list):
        return " ; ".join(option_label(question_id, v) for v in value)
    return option_label(question_id, value)


def render_report(profile: SystemProfile, answers: Answers, result: AssessmentResult, generated_on: date | None = None) -> bytes:
    font, bold = _register_fonts()
    s = _styles(font, bold)
    generated_on = generated_on or date.today()
    width = A4[0] - 36 * mm

    story: list = [
        _p("Rapport de Diagnostic Flash", s["title"]),
        Spacer(1, 4),
        _p("Classification du risque selon l'AI Act (Règlement UE 2024/1689)", s["subtitle"]),
        Spacer(1, 12),
    ]

    identity = [
        ["Système d'IA", profile.system_name],
        ["Organisation", profile.organization or "—"],
        ["Date du diagnostic", generated_on.strftime("%d/%m/%Y")],
    ]
    if profile.description:
        identity.append(["Description", profile.description])
    id_table = _table([[_p(k, s["cell_bold"]), _p(v, s["body"])] for k, v in identity], [45 * mm, width - 45 * mm], header=False)
    id_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), GREY)]))
    story += [id_table, Spacer(1, 14)]

    verdict = Table(
        [
            [_p(result.category_label.upper(), s["verdict"])],
            [_p(f"AI Risk Score : {result.risk_score} / 100", s["verdict_sub"])],
        ],
        colWidths=[width],
    )
    verdict.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CATEGORY_COLORS[result.category]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [verdict, Spacer(1, 10), _p(result.summary, s["body"])]
    if result.max_penalty:
        story += [Spacer(1, 6), Paragraph(f"<b>Sanction maximale encourue :</b> {escape(result.max_penalty)}", s["body"])]

    if result.findings:
        story.append(_p("Constats de la classification", s["h2"]))
        rows = [[_p("Constat", s["header"]), _p("Détail", s["header"]), _p("Référence", s["header"])]]
        rows += [[_p(f.title, s["cell_bold"]), _p(f.detail, s["small"]), _p(f.legal_reference, s["small"])] for f in result.findings]
        story.append(_table(rows, [45 * mm, width - 80 * mm, 35 * mm]))

    if result.flags:
        story.append(_p("Points d'attention", s["h2"]))
        story.append(ListFlowable([ListItem(_p(flag, s["body"]), leftIndent=10) for flag in result.flags], bulletType="bullet", start="•"))

    if result.obligations:
        story.append(_p("Obligations applicables et correspondance ISO/IEC 42001", s["h2"]))
        rows = [[_p("Obligation", s["header"]), _p("Référence", s["header"]), _p("Applicable dès", s["header"]), _p("ISO/IEC 42001", s["header"])]]
        for o in result.obligations:
            cell = [_p(o.title, s["cell_bold"]), Spacer(1, 2), _p(o.description, s["small"])]
            rows.append([cell, _p(o.legal_reference, s["small"]), _p(o.applies_from, s["small"]), Paragraph("<br/>".join(escape(c) for c in o.iso42001_controls), s["small"])])
        story.append(_table(rows, [width - 105 * mm, 25 * mm, 25 * mm, 55 * mm]))

    score_rows = [[_p("Composante", s["header"]), _p("Points", s["header"])]]
    score_rows += [[_p(f.label, s["small"]), _p(f"{f.points:g}", s["small"])] for f in result.score_factors]
    score_rows.append([_p("AI Risk Score", s["cell_bold"]), _p(str(result.risk_score), s["cell_bold"])])
    story.append(KeepTogether([_p("Calcul de l'AI Risk Score", s["h2"]), _table(score_rows, [width - 30 * mm, 30 * mm])]))

    kept = applicable_answers(answers)
    answer_rows = [[_p("Question", s["header"]), _p("Réponse", s["header"])]]
    for question in QUESTIONS:
        if question.id in kept:
            answer_rows.append([_p(question.text, s["small"]), _p(_answer_text(question.id, kept[question.id]), s["small"])])
    story += [_p("Récapitulatif des réponses", s["h2"]), _table(answer_rows, [width * 0.6, width * 0.4])]

    story += [Spacer(1, 14), _p(DISCLAIMER, s["small"])]

    def footer(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont(font, 7.5)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(18 * mm, 10 * mm, "AI Compliance & ISO 42001 Management Platform — Diagnostic Flash")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"Diagnostic AI Act — {profile.system_name}",
        author="AI Compliance Platform",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
