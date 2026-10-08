# ============================================================
# CLAIMPILOT TRIAGE AGENT
# ============================================================

def determine_triage(
    damage_analysis,
    anomaly_analysis,
    document_analysis,
    cost_estimation
):
    """
    Determine the recommended next survey route for a claim.

    Possible routes:

    FAST_TRACK
    REMOTE_SURVEY
    PHYSICAL_SURVEY

    IMPORTANT:
    This is a recommendation for workflow routing only.

    It does NOT:
    - approve a claim
    - reject a claim
    - determine fraud
    - make a final coverage decision
    """


    # ========================================================
    # SAFELY NORMALIZE INPUTS
    # ========================================================

    if not isinstance(
        damage_analysis,
        dict
    ):

        damage_analysis = {}


    if not isinstance(
        anomaly_analysis,
        dict
    ):

        anomaly_analysis = {}


    if not isinstance(
        document_analysis,
        dict
    ):

        document_analysis = {}


    if not isinstance(
        cost_estimation,
        dict
    ):

        cost_estimation = {}


    # ========================================================
    # DAMAGE INFORMATION
    # ========================================================

    overall_severity = str(

        damage_analysis.get(
            "overall_severity",
            "UNKNOWN"
        )

    ).upper()


    damaged_parts = damage_analysis.get(
        "damaged_parts",
        []
    )


    if not isinstance(
        damaged_parts,
        list
    ):

        damaged_parts = []


    potential_hidden_damage = (
        damage_analysis.get(
            "potential_hidden_damage",
            []
        )
    )


    if not isinstance(
        potential_hidden_damage,
        list
    ):

        potential_hidden_damage = []


    structural_damage = (
        damage_analysis.get(
            "structural_damage",
            {}
        )
    )


    if not isinstance(
        structural_damage,
        dict
    ):

        structural_damage = {}


    structural_suspected = (
        structural_damage.get(
            "suspected",
            False
        )
    )


    image_quality = (
        damage_analysis.get(
            "image_quality",
            {}
        )
    )


    if not isinstance(
        image_quality,
        dict
    ):

        image_quality = {}


    images_adequate = (
        image_quality.get(
            "adequate_for_assessment",
            True
        )
    )


    # ========================================================
    # DOCUMENT INFORMATION
    # ========================================================

    evidence_completeness = (
        document_analysis.get(
            "evidence_completeness",
            0
        )
    )


    try:

        evidence_completeness = int(
            evidence_completeness
        )

    except (
        TypeError,
        ValueError
    ):

        evidence_completeness = 0


    missing_documents = (
        document_analysis.get(
            "missing_documents",
            []
        )
    )


    if not isinstance(
        missing_documents,
        list
    ):

        missing_documents = []


    verification_required = (
        document_analysis.get(
            "verification_required",
            False
        )
    )


    # ========================================================
    # INVESTIGATION INFORMATION
    # ========================================================

    indicators = (
        anomaly_analysis.get(
            "indicators",
            []
        )
    )


    if not isinstance(
        indicators,
        list
    ):

        indicators = []


    indicator_level = str(

        anomaly_analysis.get(
            "indicator_level",
            "NO_SPECIFIC_INDICATOR"
        )

    ).upper()


    # ========================================================
    # COST INFORMATION
    # ========================================================

    estimated_total = (
        cost_estimation.get(
            "estimated_total",
            {}
        )
    )


    if not isinstance(
        estimated_total,
        dict
    ):

        estimated_total = {}


    total_min = estimated_total.get(
        "min",
        0
    )


    total_max = estimated_total.get(
        "max",
        0
    )


    try:

        total_min = float(
            total_min
        )

    except (
        TypeError,
        ValueError
    ):

        total_min = 0


    try:

        total_max = float(
            total_max
        )

    except (
        TypeError,
        ValueError
    ):

        total_max = 0


    # ========================================================
    # DECISION FLAGS
    # ========================================================

    physical_reasons = []

    remote_reasons = []

    fast_track_reasons = []


    # ========================================================
    # RULE 1: STRUCTURAL DAMAGE
    # ========================================================

    if structural_suspected:

        physical_reasons.append(

            "Possible structural damage "
            "requires physical inspection."

        )


    # ========================================================
    # RULE 2: SEVERE DAMAGE
    # ========================================================

    if overall_severity == "SEVERE":

        physical_reasons.append(

            "Severe visible damage requires "
            "physical survey verification."

        )


    # ========================================================
    # RULE 3: HIGH DAMAGE
    # ========================================================

    elif overall_severity == "HIGH":

        physical_reasons.append(

            "High-severity damage may require "
            "physical inspection."

        )


    # ========================================================
    # RULE 4: HIDDEN DAMAGE
    # ========================================================

    if potential_hidden_damage:

        physical_reasons.append(

            "Potential hidden damage requires "
            "workshop/surveyor inspection."

        )


    # ========================================================
    # RULE 5: IMAGE QUALITY
    # ========================================================

    if not images_adequate:

        physical_reasons.append(

            "Available images are insufficient "
            "for reliable remote assessment."

        )


    # ========================================================
    # RULE 6: SAFETY / CRITICAL COMPONENTS
    # ========================================================

    safety_checks = (
        damage_analysis.get(
            "safety_checks",
            []
        )
    )


    if (
        isinstance(
            safety_checks,
            list
        )
        and
        safety_checks
    ):

        physical_reasons.append(

            "Safety-critical components require "
            "additional verification."

        )


    # ========================================================
    # RULE 7: ADAS
    # ========================================================

    adas_checks = (
        damage_analysis.get(
            "adas_checks",
            []
        )
    )


    if (
        isinstance(
            adas_checks,
            list
        )
        and
        adas_checks
    ):

        remote_reasons.append(

            "ADAS or sensor components may "
            "require additional inspection "
            "or calibration."

        )


    # ========================================================
    # RULE 8: MULTIPLE DAMAGED PARTS
    # ========================================================

    if len(
        damaged_parts
    ) >= 5:

        physical_reasons.append(

            "Multiple damaged components were "
            "identified and the full damage extent "
            "should be verified."

        )


    # ========================================================
    # RULE 9: INVESTIGATION INDICATORS
    # ========================================================

    if indicator_level in [

        "REVIEW_REQUIRED",

        "REVIEW_RECOMMENDED"

    ]:

        remote_reasons.append(

            "Additional investigation indicators "
            "require human review."

        )


    # ========================================================
    # RULE 10: INCOMPLETE EVIDENCE
    # ========================================================

    if evidence_completeness < 100:

        remote_reasons.append(

            "Claim evidence is incomplete and "
            "requires additional verification."

        )


    if missing_documents:

        remote_reasons.append(

            "One or more claim documents are "
            "missing or require verification."

        )


    # ========================================================
    # RULE 11: HIGH PRELIMINARY EXPOSURE
    # ========================================================

    if total_max >= 100000:

        physical_reasons.append(

            "The preliminary repair exposure is "
            "relatively high and should be verified "
            "through detailed survey."

        )


    # ========================================================
    # RULE 12: FAST TRACK CONDITIONS
    # ========================================================
    #
    # Fast-track is considered only when:
    #
    # - evidence is complete
    # - images are adequate
    # - damage is low/moderate
    # - no hidden damage
    # - no structural concern
    # - no investigation indicators
    # - no safety concerns
    #
    # This is deliberately conservative.
    # ========================================================

    fast_track_eligible = (

        evidence_completeness >= 100

        and

        images_adequate is True

        and

        overall_severity in [
            "LOW",
            "MODERATE"
        ]

        and

        not potential_hidden_damage

        and

        not structural_suspected

        and

        not indicators

        and

        not safety_checks

        and

        len(damaged_parts) <= 3

        and

        total_max < 50000

    )


    if fast_track_eligible:

        fast_track_reasons.extend([

            "Claim evidence is complete.",

            "Images are adequate for preliminary "
            "assessment.",

            "Damage severity is low or moderate.",

            "No specific investigation indicators "
            "were identified.",

            "No structural or hidden-damage concern "
            "was identified.",

            "Preliminary repair exposure is relatively "
            "limited."

        ])


    # ========================================================
    # FINAL ROUTE DECISION
    # ========================================================

    if physical_reasons:

        recommended_route = (
            "PHYSICAL_SURVEY"
        )


        confidence = 92


        reason = (

            "Physical survey is recommended because "
            + " ".join(
                physical_reasons
            )

        )


    elif fast_track_eligible:

        recommended_route = (
            "FAST_TRACK"
        )


        confidence = 88


        reason = (

            "The claim meets the current "
            "preliminary fast-track criteria. "
            + " ".join(
                fast_track_reasons
            )

        )


    else:

        recommended_route = (
            "REMOTE_SURVEY"
        )


        confidence = 82


        if remote_reasons:

            reason = (

                "Remote survey is recommended for "
                "further claim verification. "
                + " ".join(
                    remote_reasons
                )

            )

        else:

            reason = (

                "Remote survey is recommended as "
                "the next verification step based "
                "on the currently available evidence."

            )


    # ========================================================
    # CONFIDENCE ADJUSTMENT
    # ========================================================
    #
    # Very incomplete evidence should reduce confidence.
    # ========================================================

    if evidence_completeness < 50:

        confidence -= 15

    elif evidence_completeness < 75:

        confidence -= 8


    if not images_adequate:

        confidence -= 10


    confidence = max(
        50,
        min(
            98,
            confidence
        )
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "recommended_route":
            recommended_route,

        "confidence":
            confidence,

        "reason":
            reason,

        "physical_survey_reasons":
            physical_reasons,

        "remote_survey_reasons":
            remote_reasons,

        "fast_track_reasons":
            fast_track_reasons,

        "human_review_required":
            True,

        "final_decision":
            "NOT DETERMINED BY AI"

    }