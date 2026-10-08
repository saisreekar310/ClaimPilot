import streamlit as st

from services.pdf_service import extract_pdf_text
from agents.claim_agent import analyze_claim
from services.report_service import build_claim_report


st.set_page_config(
    page_title="ClaimPilot",
    page_icon="🚗",
    layout="wide",
)


st.title("🚗 ClaimPilot")

st.markdown(
    """
### AI-Powered Motor Insurance Claims Intelligence

ClaimPilot analyzes claim documents and vehicle images, prepares a
preliminary damage assessment, researches indicative spare-part pricing,
identifies investigation indicators, and recommends the next survey route.
"""
)

st.divider()


# ============================================================
# CLAIM INFORMATION
# ============================================================

st.subheader("📋 Claim Information")

col1, col2 = st.columns(2)


with col1:

    vehicle_number = st.text_input(
        "Vehicle Registration Number",
        placeholder="Example: KA01AB1234",
    )

    policy_file = st.file_uploader(
        "Upload Insurance Policy PDF",
        type=["pdf"],
    )

    rc_file = st.file_uploader(
        "Upload RC (Optional)",
        type=["pdf", "jpg", "jpeg", "png"],
    )


with col2:

    accident_description = st.text_area(
        "Accident Description",
        placeholder=(
            "Describe what happened, for example: "
            "vehicle collided with another car from "
            "the front-right side."
        ),
        height=120,
    )

    dl_file = st.file_uploader(
        "Upload Driving Licence (Optional)",
        type=["pdf", "jpg", "jpeg", "png"],
    )

    image_files = st.file_uploader(
        "Upload Vehicle Images",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
    )


st.caption(
    "RC and Driving Licence are optional. "
    "ClaimPilot can continue without them, but their presence "
    "improves evidence completeness."
)


analyze_button = st.button(
    "🔍 Analyze Claim",
    type="primary",
    width="stretch",
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze_button:

    if not image_files:

        st.error(
            "Please upload at least one vehicle image."
        )

        st.stop()


    if not accident_description.strip():

        st.warning(
            "Accident description is empty. "
            "The analysis can continue, but the AI summary "
            "may be less informative."
        )


    # --------------------------------------------------------
    # POLICY
    # --------------------------------------------------------

    policy_text = ""


    if policy_file:

        try:

            policy_text = extract_pdf_text(
                policy_file
            )

        except Exception as error:

            st.error(
                f"Could not read policy PDF: {error}"
            )

            st.stop()

    else:

        st.info(
            "No policy PDF uploaded. "
            "Policy verification will be marked incomplete."
        )


    # --------------------------------------------------------
    # RC / DL
    # --------------------------------------------------------

    rc_available = (
        rc_file is not None
    )

    dl_available = (
        dl_file is not None
    )


    # --------------------------------------------------------
    # RUN CLAIM AGENT
    # --------------------------------------------------------

    with st.spinner(
        "ClaimPilot is analyzing the claim..."
    ):

        try:

            result = analyze_claim(

                vehicle_number=vehicle_number,

                policy_text=policy_text,

                accident_description=accident_description,

                image_files=image_files,

                rc_available=rc_available,

                dl_available=dl_available,

            )

        except TypeError:

            # Compatibility fallback if an older
            # claim_agent.py is still being used.

            result = analyze_claim(

                vehicle_number=vehicle_number,

                policy_text=policy_text,

                accident_description=accident_description,

                image_files=image_files,

            )

        except Exception as error:

            st.error(
                f"Claim analysis failed: {error}"
            )

            st.exception(error)

            st.stop()


    st.success(
        "Claim analysis completed."
    )


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

    cost = result.get(
        "cost_estimation",
        {}
    )

    total = cost.get(
        "estimated_total",
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


    # ========================================================
    # CLAIM SNAPSHOT
    # ========================================================

    st.subheader(
        "📌 Claim Snapshot"
    )


    snap1, snap2, snap3, snap4 = st.columns(4)


    with snap1:

        st.metric(
            "Vehicle",
            (
                f"{str(vehicle.get('make', 'Unknown'))} "
                f"{str(vehicle.get('model', 'Unknown'))}"
            )
        )


    with snap2:

        st.metric(
            "Severity",
            str(
                damage.get(
                    "overall_severity",
                    "UNKNOWN"
                )
            )
        )


    with snap3:

        st.metric(
            "Preliminary Exposure",
            (
                f"₹{int(total.get('min', 0)):,}"
                f" – "
                f"₹{int(total.get('max', 0)):,}"
            )
        )


    with snap4:

        st.metric(
            "Evidence",
            f"{documents.get('evidence_completeness', 0)}%"
        )


    # ========================================================
    # AI SUMMARY
    # ========================================================

    st.subheader(
        "🤖 AI Claim Summary"
    )


    st.info(

        str(

            result.get(
                "ai_summary",
                "No AI summary available."
            )

        )

    )


    # ========================================================
    # VEHICLE
    # ========================================================

    st.subheader(
        "🚘 Vehicle Identification"
    )


    vehicle_data = {

        "Field": [

            "Make",
            "Model",
            "Estimated Year",
            "Generation",
            "Confidence",

        ],

        "Detected Value": [

            str(
                vehicle.get(
                    "make",
                    "Unknown"
                )
            ),

            str(
                vehicle.get(
                    "model",
                    "Unknown"
                )
            ),

            str(
                vehicle.get(
                    "estimated_year",
                    "Unknown"
                )
            ),

            str(
                vehicle.get(
                    "generation",
                    "Unknown"
                )
            ),

            str(
                vehicle.get(
                    "confidence",
                    "Unknown"
                )
            ),

        ],

    }


    st.table(
        vehicle_data
    )


    # ========================================================
    # DAMAGE
    # ========================================================

    st.subheader(
        "🔧 Damage Assessment"
    )


    damaged_parts = damage.get(
        "damaged_parts",
        []
    )


    pricing_parts = result.get(
        "pricing_data",
        {}
    ).get(
        "parts",
        []
    )


    damage_rows = []


    for index, part in enumerate(
        damaged_parts
    ):

        price_text = "Not available"


        if index < len(
            pricing_parts
        ):

            pricing = pricing_parts[
                index
            ]


            if (

                pricing.get(
                    "price_min"
                ) is not None

                and

                pricing.get(
                    "price_max"
                ) is not None

            ):

                price_text = (

                    f"₹{int(pricing['price_min']):,}"

                    f" – "

                    f"₹{int(pricing['price_max']):,}"

                )


        damage_rows.append(

            {

                "Component": str(
                    part.get(
                        "part",
                        "Unknown"
                    )
                ),

                "Action": str(
                    part.get(
                        "recommended_action",
                        "INSPECT"
                    )
                ),

                "Severity": str(
                    part.get(
                        "severity",
                        "UNKNOWN"
                    )
                ),

                "Estimated Price": price_text,

            }

        )


    if damage_rows:

        st.dataframe(

            damage_rows,

            width="stretch",

            hide_index=True,

        )

    else:

        st.warning(
            "No damaged components were identified."
        )


    # ========================================================
    # ROUTE
    # ========================================================

    st.subheader(
        "🧭 Recommended Claim Route"
    )


    r1, r2 = st.columns(2)


    with r1:

        st.metric(

            "Recommended Route",

            str(

                triage.get(

                    "recommended_route",

                    "PHYSICAL_SURVEY"

                )

            )

        )


    with r2:

        st.metric(

            "Confidence",

            f"{triage.get('confidence', 0)}%"

        )


    st.info(

        str(

            triage.get(

                "reason",

                "Human verification required."

            )

        )

    )


    # ========================================================
    # PDF
    # ========================================================

    st.divider()


    st.subheader(
        "📑 Detailed Surveyor Report"
    )


    st.caption(

        "The PDF contains the detailed evidence, "
        "crash images, policy information, cost breakdown, "
        "investigation indicators and verification notes."

    )


    try:

        pdf_bytes = build_claim_report(

            result,

            image_files=image_files

        )


        st.download_button(

            label=(
                "⬇️ Download Surveyor Report"
            ),

            data=pdf_bytes,

            file_name=(
                "ClaimPilot_Claim_Assessment.pdf"
            ),

            mime="application/pdf",

            width="stretch",

        )


    except Exception as error:

        st.error(
            f"Could not generate PDF report: {error}"
        )

        st.exception(error)


st.divider()


st.caption(

    "ClaimPilot AI assists claim preparation and triage. "
    "Final claim decisions remain with qualified insurance "
    "professionals and surveyors."

)