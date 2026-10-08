# ============================================================
# CLAIMPILOT INVESTIGATION / ANOMALY AGENT
# ============================================================

def analyze_fraud_indicators(
    damage_analysis,
    accident_description,
    cost_estimation
):
    """
    Generate investigation indicators for a motor insurance
    claim.

    IMPORTANT:
    This function does NOT determine fraud.

    It only identifies claim characteristics that may require
    additional investigation or physical verification.
    """


    # ========================================================
    # INITIALIZE
    # ========================================================

    indicators = []

    verification_items = []


    # ========================================================
    # SAFELY READ DAMAGE ANALYSIS
    # ========================================================

    if not isinstance(
        damage_analysis,
        dict
    ):

        damage_analysis = {}


    damaged_parts = damage_analysis.get(
        "damaged_parts",
        []
    )


    potential_hidden_damage = (
        damage_analysis.get(
            "potential_hidden_damage",
            []
        )
    )


    overall_severity = str(

        damage_analysis.get(
            "overall_severity",
            "UNKNOWN"
        )

    ).upper()


    structural_damage = (
        damage_analysis.get(
            "structural_damage",
            {}
        )
    )


    safety_checks = (
        damage_analysis.get(
            "safety_checks",
            []
        )
    )


    adas_checks = (
        damage_analysis.get(
            "adas_checks",
            []
        )
    )


    # ========================================================
    # HIGH / SEVERE DAMAGE
    # ========================================================

    if overall_severity in [
        "HIGH",
        "SEVERE"
    ]:

        indicators.append(

            "High-severity visible damage requires "
            "physical verification before final assessment."

        )


        verification_items.append(

            "Verify the extent of visible damage "
            "during physical inspection."

        )


    # ========================================================
    # HIDDEN DAMAGE
    # ========================================================

    if (
        isinstance(
            potential_hidden_damage,
            list
        )
        and
        potential_hidden_damage
    ):

        indicators.append(

            "Potential hidden damage was identified "
            "behind or around visibly damaged components."

        )


        verification_items.append(

            "Inspect potential hidden damage "
            "during workshop/surveyor inspection."

        )


    # ========================================================
    # STRUCTURAL DAMAGE
    # ========================================================

    if isinstance(
        structural_damage,
        dict
    ):

        structural_suspected = (
            structural_damage.get(
                "suspected",
                False
            )
        )


        if structural_suspected:

            indicators.append(

                "Possible structural deformation "
                "requires physical verification."

            )


            verification_items.append(

                "Inspect chassis/frame alignment "
                "and structural members."

            )


    # ========================================================
    # SAFETY-CRITICAL COMPONENTS
    # ========================================================

    if (
        isinstance(
            safety_checks,
            list
        )
        and
        safety_checks
    ):

        indicators.append(

            "Safety-critical components require "
            "inspection based on the image assessment."

        )


        for item in safety_checks[:5]:

            if item:

                verification_items.append(
                    str(item)
                )


    # ========================================================
    # ADAS / SENSOR CHECKS
    # ========================================================

    if (
        isinstance(
            adas_checks,
            list
        )
        and
        adas_checks
    ):

        indicators.append(

            "ADAS, radar, camera or sensor components "
            "may require additional inspection/calibration."

        )


        for item in adas_checks[:5]:

            if item:

                verification_items.append(
                    str(item)
                )


    # ========================================================
    # MULTIPLE DAMAGED COMPONENTS
    # ========================================================

    if (
        isinstance(
            damaged_parts,
            list
        )
        and
        len(damaged_parts) >= 5
    ):

        indicators.append(

            "Multiple damaged components were identified; "
            "the complete damage extent should be verified "
            "during survey."

        )


        verification_items.append(

            "Verify that all affected components "
            "are consistent with the reported accident."

        )


    # ========================================================
    # SEVERE COMPONENT ACTIONS
    # ========================================================

    replace_count = 0
    inspect_count = 0


    if isinstance(
        damaged_parts,
        list
    ):

        for part in damaged_parts:

            if not isinstance(
                part,
                dict
            ):
                continue


            action = str(

                part.get(
                    "recommended_action",
                    ""
                )

            ).upper()


            severity = str(

                part.get(
                    "severity",
                    ""
                )

            ).upper()


            if action == "REPLACE":

                replace_count += 1


            if action == "INSPECT":

                inspect_count += 1


            if (
                action == "REPLACE"
                and
                severity in [
                    "HIGH",
                    "SEVERE"
                ]
            ):

                verification_items.append(

                    "Verify replacement necessity and "
                    "extent of damage for "
                    + str(
                        part.get(
                            "part",
                            "affected component"
                        )
                    )
                    + "."

                )


    # ========================================================
    # MULTIPLE REPLACEMENT COMPONENTS
    # ========================================================

    if replace_count >= 3:

        indicators.append(

            "Several components have been assessed "
            "for replacement; repair scope should be "
            "confirmed during physical inspection."

        )


    # ========================================================
    # ACCIDENT DESCRIPTION
    # ========================================================

    accident_text = str(
        accident_description or ""
    ).strip()


    if not accident_text:

        indicators.append(

            "Accident description was not provided; "
            "incident circumstances require verification."

        )


        verification_items.append(

            "Obtain and verify the accident description."

        )


    # ========================================================
    # COST INFORMATION
    # ========================================================

    if not isinstance(
        cost_estimation,
        dict
    ):

        cost_estimation = {}


    estimated_total = (
        cost_estimation.get(
            "estimated_total",
            {}
        )
    )


    if isinstance(
        estimated_total,
        dict
    ):

        estimated_min = estimated_total.get(
            "min",
            0
        )

        estimated_max = estimated_total.get(
            "max",
            0
        )

    else:

        estimated_min = 0
        estimated_max = 0


    try:

        estimated_min = float(
            estimated_min
        )

    except (
        TypeError,
        ValueError
    ):

        estimated_min = 0


    try:

        estimated_max = float(
            estimated_max
        )

    except (
        TypeError,
        ValueError
    ):

        estimated_max = 0


    # ========================================================
    # HIGH-VALUE PRELIMINARY REPAIR
    # ========================================================

    # This is deliberately only an investigation indicator.
    # It is NOT a fraud score.

    if estimated_max >= 100000:

        indicators.append(

            "The preliminary repair exposure is relatively "
            "high and should be supported by detailed "
            "physical inspection and repair estimates."

        )


        verification_items.append(

            "Verify major repair components and workshop "
            "estimate against the physical vehicle."

        )


    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique_indicators = []

    for item in indicators:

        item = str(item).strip()

        if (
            item
            and
            item not in unique_indicators
        ):

            unique_indicators.append(
                item
            )


    unique_verifications = []

    for item in verification_items:

        item = str(item).strip()

        if (
            item
            and
            item not in unique_verifications
        ):

            unique_verifications.append(
                item
            )


    # ========================================================
    # OVERALL INDICATOR LEVEL
    # ========================================================

    if len(
        unique_indicators
    ) >= 4:

        indicator_level = "REVIEW_REQUIRED"

    elif len(
        unique_indicators
    ) >= 2:

        indicator_level = "REVIEW_RECOMMENDED"

    elif unique_indicators:

        indicator_level = "REVIEW_RECOMMENDED"

    else:

        indicator_level = "NO_SPECIFIC_INDICATOR"


    # ========================================================
    # EXPLANATION
    # ========================================================

    if unique_indicators:

        explanation = (

            "ClaimPilot identified one or more "
            "investigation indicators that may require "
            "additional evidence or physical verification. "
            "These indicators are not a fraud determination."

        )

    else:

        explanation = (

            "No specific investigation indicators were "
            "identified from the currently available "
            "claim evidence. Standard surveyor verification "
            "is still required."

        )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "indicator_level":
            indicator_level,

        "indicators":
            unique_indicators,

        "verification_items":
            unique_verifications,

        "explanation":
            explanation,

        "risk_level":
            indicator_level,

        "fraud_determination":
            "NOT DETERMINED",

        "human_review_required":
            True

    }