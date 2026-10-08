from io import BytesIO
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Image,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ============================================================
# FONT SETUP
# ============================================================

def register_unicode_font():
    """
    Find a font that supports the Indian Rupee symbol ₹.
    """

    candidates = [
        r"C:\Windows\Fonts\NirmalaUI.ttf",
        r"C:\Windows\Fonts\Nirmala.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",

        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",

        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]

    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(
                    TTFont("ClaimPilotUnicode", path)
                )
                return "ClaimPilotUnicode"
            except Exception:
                continue

    return "Helvetica"


def register_bold_font():
    """
    Register a bold Unicode font.
    """

    candidates = [
        r"C:\Windows\Fonts\NirmalaUI-Bold.ttf",
        r"C:\Windows\Fonts\Nirmala-Bold.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",

        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]

    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(
                    TTFont("ClaimPilotUnicodeBold", path)
                )
                return "ClaimPilotUnicodeBold"
            except Exception:
                continue

    return "Helvetica-Bold"


FONT_NAME = register_unicode_font()
BOLD_FONT_NAME = register_bold_font()


# ============================================================
# HELPERS
# ============================================================

def format_currency(value):
    """
    Format values using Indian Rupee notation.

    Example:
    19500 -> ₹19,500
    """

    if value is None:
        return "N/A"

    try:
        return f"₹{int(value):,}"
    except Exception:
        return "N/A"


def _table(data, widths, font_size=8):
    """
    Standard ClaimPilot table.
    """

    table = Table(
        data,
        colWidths=widths,
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#173B63")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                FONT_NAME
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#B8B8B8")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                font_size
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
        ])
    )

    return table


# ============================================================
# REPORT
# ============================================================

def build_claim_report(result, image_files=None):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    styles = getSampleStyleSheet()

    # --------------------------------------------------------
    # STYLES
    # --------------------------------------------------------

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName=FONT_NAME,
        fontSize=19,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#173B63"),
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=9.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=7
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName=BOLD_FONT_NAME,
        fontSize=11.5,
        leading=13,
        textColor=colors.HexColor("#173B63"),
        spaceBefore=6,
        spaceAfter=4
    )

    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=8.3,
        leading=10.5,
        textColor=colors.HexColor("#222222")
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=7.2,
        leading=8.5,
        textColor=colors.HexColor("#444444")
    )

    table_text_style = ParagraphStyle(
        "TableText",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#222222")
    )

    table_bold_style = ParagraphStyle(
        "TableBold",
        parent=styles["BodyText"],
        fontName=BOLD_FONT_NAME,
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#222222")
    )

    confidence_style = ParagraphStyle(
        "Confidence",
        parent=styles["BodyText"],
        fontName=BOLD_FONT_NAME,
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#173B63")
    )

    story = []

    # ========================================================
    # DATA
    # ========================================================

    vehicle = result.get(
        "vehicle_identification",
        {}
    )

    damage = result.get(
        "damage_analysis",
        {}
    )

    pricing = result.get(
        "pricing_data",
        {}
    )

    cost = result.get(
        "cost_estimation",
        {}
    )

    documents = result.get(
        "document_analysis",
        {}
    )

    triage = result.get(
        "triage_analysis",
        {}
    )

    total = cost.get(
        "estimated_total",
        {}
    )

    # ========================================================
    # HEADER
    # ========================================================

    story.append(
        Paragraph(
            "ClaimPilot",
            title_style
        )
    )

    story.append(
        Paragraph(
            "AI Motor Insurance Claim Assessment",
            subtitle_style
        )
    )

    # ========================================================
    # AI CONFIDENCE AT TOP
    # ========================================================

    ai_confidence = damage.get(
        "confidence",
        vehicle.get("confidence", 0)
    )

    confidence_box = Table(
        [
            [
                Paragraph(
                    "OVERALL AI CONFIDENCE",
                    confidence_style
                ),
                Paragraph(
                    f"<b>{ai_confidence}%</b>",
                    confidence_style
                )
            ]
        ],
        colWidths=[
            115 * mm,
            50 * mm
        ]
    )

    confidence_box.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#EEF4FA")
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                colors.HexColor("#8CA9C4")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "ALIGN",
                (1, 0),
                (1, 0),
                "RIGHT"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )

    story.append(confidence_box)

    # ========================================================
    # 1. CLAIM SNAPSHOT
    # ========================================================

    story.append(
        Paragraph(
            "1. Claim Snapshot",
            heading_style
        )
    )

    snapshot = [
        [
            "Field",
            "Assessment"
        ],

        [
            "Registration Number",
            str(
                result.get(
                    "vehicle_number",
                    "Not provided"
                )
            )
        ],

        [
            "Vehicle",
            f"{vehicle.get('make', 'Unknown')} "
            f"{vehicle.get('model', 'Unknown')}"
        ],

        [
            "Overall Severity",
            str(
                damage.get(
                    "overall_severity",
                    "UNKNOWN"
                )
            )
        ],

        [
            "Preliminary Exposure",
            f"{format_currency(total.get('min'))} - "
            f"{format_currency(total.get('max'))}"
        ],

        [
            "Evidence Completeness",
            f"{documents.get('evidence_completeness', 0)}%"
        ],

        [
            "Recommended Route",
            str(
                triage.get(
                    "recommended_route",
                    "PHYSICAL_SURVEY"
                )
            )
        ],
    ]

    story.append(
        _table(
            snapshot,
            [55 * mm, 110 * mm]
        )
    )

    # ========================================================
    # 2. AI CLAIM SUMMARY
    # ========================================================

    story.append(
        Paragraph(
            "2. AI Claim Summary",
            heading_style
        )
    )

    story.append(
        Paragraph(
            str(
                result.get(
                    "ai_summary",
                    "No AI summary available."
                )
            ),
            normal_style
        )
    )

    # ========================================================
    # 3. ACCIDENT DESCRIPTION
    # ========================================================

    story.append(
        Paragraph(
            "3. Accident Description",
            heading_style
        )
    )

    story.append(
        Paragraph(
            str(
                result.get(
                    "accident_description",
                    "Not provided"
                )
            ),
            normal_style
        )
    )

    # ========================================================
    # 4. VEHICLE IDENTIFICATION
    # ========================================================

    story.append(
        Paragraph(
            "4. Vehicle Identification",
            heading_style
        )
    )

    vehicle_rows = [
        [
            "Field",
            "Value"
        ],

        [
            "Make",
            str(
                vehicle.get(
                    "make",
                    "Unknown"
                )
            )
        ],

        [
            "Model",
            str(
                vehicle.get(
                    "model",
                    "Unknown"
                )
            )
        ],

        [
            "Estimated Year",
            str(
                vehicle.get(
                    "estimated_year",
                    "Unknown"
                )
            )
        ],

        [
            "Generation",
            str(
                vehicle.get(
                    "generation",
                    "Unknown"
                )
            )
        ],

        [
            "Identification Confidence",
            f"{vehicle.get('confidence', 0)}%"
        ],
    ]

    story.append(
        _table(
            vehicle_rows,
            [60 * mm, 105 * mm]
        )
    )

    # ========================================================
    # IMPORTANT:
    # VISUAL IDENTIFICATION EVIDENCE REMOVED
    # ========================================================

    # ========================================================
    # 5. CRASH IMAGES
    # ========================================================

    story.append(
        Paragraph(
            "5. Crash Images",
            heading_style
        )
    )

    image_cells = []

    # Maximum 4 images to keep the report compact
    for image_file in (image_files or [])[:4]:

        try:

            image_file.seek(0)

            image_cells.append(
                Image(
                    image_file,
                    width=75 * mm,
                    height=52 * mm,
                    kind="proportional"
                )
            )

        except Exception:
            continue

    if image_cells:

        rows = []

        for i in range(
            0,
            len(image_cells),
            2
        ):

            row = image_cells[i:i + 2]

            if len(row) == 1:
                row.append("")

            rows.append(row)

        image_table = Table(
            rows,
            colWidths=[
                82 * mm,
                82 * mm
            ]
        )

        image_table.setStyle(
            TableStyle([
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),
            ])
        )

        story.append(image_table)

    else:

        story.append(
            Paragraph(
                "No crash images were supplied.",
                normal_style
            )
        )

    # ========================================================
    # 6. DAMAGE ASSESSMENT
    # ========================================================

    story.append(
        Paragraph(
            "6. Detailed Damage Assessment",
            heading_style
        )
    )

    damage_rows = [
        [
            "Component",
            "Action",
            "Severity",
            "Indicative Cost",
            "Basis"
        ]
    ]

    pricing_parts = pricing.get(
        "parts",
        []
    )

    for index, part in enumerate(
        damage.get(
            "damaged_parts",
            []
        )
    ):

        price_text = "N/A"
        basis = "Not available"

        if index < len(pricing_parts):

            p = pricing_parts[index]

            if (
                p.get("price_min") is not None
                and
                p.get("price_max") is not None
            ):

                price_text = (
                    f"{format_currency(p.get('price_min'))}"
                    f" - "
                    f"{format_currency(p.get('price_max'))}"
                )

                if (
                    p.get("price_source")
                    == "PUBLIC_WEB"
                ):
                    basis = "Public web"
                else:
                    basis = "AI reference"

        damage_rows.append(
            [
                str(
                    part.get(
                        "part",
                        "Unknown"
                    )
                ),

                str(
                    part.get(
                        "recommended_action",
                        "INSPECT"
                    )
                ),

                str(
                    part.get(
                        "severity",
                        "UNKNOWN"
                    )
                ),

                price_text,

                basis
            ]
        )

    if len(damage_rows) == 1:

        damage_rows.append(
            [
                "No components identified",
                "-",
                "-",
                "-",
                "-"
            ]
        )

    story.append(
        _table(
            damage_rows,
            [
                42 * mm,
                28 * mm,
                28 * mm,
                42 * mm,
                25 * mm
            ],
            font_size=7.4
        )
    )

    # ========================================================
    # 7. VISUAL FINDINGS
    # COMPACT VERSION
    # ========================================================

    story.append(
        Paragraph(
            "7. Visual Findings and Inspection Notes",
            heading_style
        )
    )

    # Only keep the first 3 observations
    observations = damage.get(
        "observations",
        []
    )[:3]

    for item in observations:

        story.append(
            Paragraph(
                f"• {item}",
                normal_style
            )
        )

    # Compact hidden damage line
    hidden = damage.get(
        "potential_hidden_damage",
        []
    )

    if hidden:

        hidden_text = ", ".join(
            str(item)
            for item in hidden[:4]
        )

        story.append(
            Paragraph(
                f"<b>Potential hidden damage:</b> "
                f"{hidden_text}.",
                normal_style
            )
        )

    # Structural finding
    structural = damage.get(
        "structural_damage",
        {}
    )

    if structural.get(
        "suspected",
        False
    ):

        story.append(
            Paragraph(
                "<b>Structural damage:</b> "
                "Suspected based on visible deformation "
                "and panel misalignment; physical inspection required.",
                normal_style
            )
        )

    # Keep safety section very short
    safety = damage.get(
        "safety_checks",
        []
    )[:2]

    if safety:

        story.append(
            Paragraph(
                "<b>Safety checks:</b> "
                + "; ".join(
                    str(item)
                    for item in safety
                ),
                normal_style
            )
        )

    # Keep ADAS section very short
    adas = damage.get(
        "adas_checks",
        []
    )[:1]

    if adas:

        story.append(
            Paragraph(
                "<b>ADAS / sensor:</b> "
                + str(adas[0]),
                normal_style
            )
        )

    # ========================================================
    # 8. EVIDENCE STATUS
    # ========================================================

    story.append(
        Paragraph(
            "8. Evidence Status",
            heading_style
        )
    )

    evidence_rows = [
        [
            "Status",
            str(
                documents.get(
                    "status",
                    "UNKNOWN"
                )
            )
        ],

        [
            "Completeness",
            f"{documents.get('evidence_completeness', 0)}%"
        ],

        [
            "Verification Required",
            str(
                documents.get(
                    "verification_required",
                    False
                )
            )
        ],
    ]

    story.append(
        _table(
            evidence_rows,
            [60 * mm, 105 * mm]
        )
    )

    available = documents.get(
        "available_documents",
        []
    )

    missing = documents.get(
        "missing_documents",
        []
    )

    if available:

        story.append(
            Paragraph(
                "<b>Available:</b> "
                + ", ".join(available),
                small_style
            )
        )

    if missing:

        story.append(
            Paragraph(
                "<b>Missing / verify:</b> "
                + ", ".join(missing),
                small_style
            )
        )

    # ========================================================
    # 9. PRELIMINARY REPAIR EXPOSURE
    # ========================================================

    story.append(
        Paragraph(
            "9. Preliminary Repair Exposure",
            heading_style
        )
    )

    cost_rows = [
        [
            "Cost Component",
            "Minimum",
            "Maximum"
        ]
    ]

    for label, key in [
        ("Parts", "parts_cost"),
        ("Labour", "labour_cost"),
        ("Paint", "paint_cost"),
        (
            "Hidden Damage Allowance",
            "hidden_damage_allowance"
        ),
    ]:

        section = cost.get(
            key,
            {}
        )

        cost_rows.append(
            [
                label,
                format_currency(
                    section.get("min")
                ),
                format_currency(
                    section.get("max")
                )
            ]
        )

    cost_rows.append(
        [
            "TOTAL PRELIMINARY EXPOSURE",
            format_currency(
                total.get("min")
            ),
            format_currency(
                total.get("max")
            )
        ]
    )

    cost_table = _table(
        cost_rows,
        [
            80 * mm,
            42 * mm,
            42 * mm
        ]
    )

    cost_table.setStyle(
        TableStyle([
            (
                "FONTNAME",
                (0, -1),
                (-1, -1),
                BOLD_FONT_NAME
            ),
            (
                "BACKGROUND",
                (0, -1),
                (-1, -1),
                colors.HexColor("#EEF4FA")
            ),
        ])
    )

    story.append(cost_table)

    # ========================================================
    # 10. INVESTIGATION INDICATORS
    # REMOVED COMPLETELY
    # ========================================================

    # ========================================================
    # 10. RECOMMENDED SURVEY ROUTE
    # ========================================================

    story.append(
        Paragraph(
            "10. Recommended Survey Route",
            heading_style
        )
    )

    route = str(
        triage.get(
            "recommended_route",
            "PHYSICAL_SURVEY"
        )
    )

    route_confidence = (
        f"{triage.get('confidence', 0)}%"
    )

    route_reason = str(
        triage.get(
            "reason",
            ""
        )
    )

    # IMPORTANT:
    # Use Paragraph objects inside table cells so
    # long text automatically wraps instead of
    # going outside the table.

    triage_rows = [
        [
            Paragraph(
                "<b>Field</b>",
                table_bold_style
            ),
            Paragraph(
                "<b>Assessment</b>",
                table_bold_style
            )
        ],

        [
            Paragraph(
                "Recommended Route",
                table_text_style
            ),
            Paragraph(
                route,
                table_text_style
            )
        ],

        [
            Paragraph(
                "Confidence",
                table_text_style
            ),
            Paragraph(
                route_confidence,
                table_text_style
            )
        ],

        [
            Paragraph(
                "Reason",
                table_text_style
            ),
            Paragraph(
                route_reason,
                table_text_style
            )
        ],
    ]

    triage_table = Table(
        triage_rows,
        colWidths=[
            55 * mm,
            110 * mm
        ]
    )

    triage_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#173B63")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#B8B8B8")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )

    story.append(triage_table)

    # ========================================================
    # 11. DISCLAIMER
    # ========================================================

    story.append(
        Paragraph(
            "11. Important Disclaimer",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "ClaimPilot is an AI-assisted claims intelligence and "
            "triage system. It does not independently approve or "
            "reject claims, determine fraud, or make final settlement "
            "decisions. All assessments, prices and recommendations "
            "require verification by the appropriate insurance "
            "professional or surveyor.",
            small_style
        )
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()