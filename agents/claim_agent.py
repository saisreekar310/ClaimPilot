from agents.damage_agent import analyze_damage
from agents.document_agent import analyze_documents
from agents.fraud_agent import analyze_fraud_indicators
from agents.pricing_agent import search_part_prices
from agents.triage_agent import determine_triage


# ============================================================
# HELPERS
# ============================================================

def safe_int(
    value,
    default=0
):
    try:

        return int(
            float(value)
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# COST ENGINE
# ============================================================

def estimate_cost(
    damage_analysis,
    pricing_data,
):

    damaged_parts = damage_analysis.get(
        "damaged_parts",
        []
    )


    pricing_parts = pricing_data.get(
        "parts",
        []
    )


    priced_parts = []


    total_parts_min = 0

    total_parts_max = 0


    public_count = 0

    estimated_count = 0


    # --------------------------------------------------------
    # COMPONENT PRICING
    # --------------------------------------------------------

    for index, damage in enumerate(
        damaged_parts
    ):

        if not isinstance(
            damage,
            dict,
        ):

            continue


        part_name = damage.get(
            "part",
            "Unknown component",
        )


        action = damage.get(
            "recommended_action",
            "INSPECT",
        )


        severity = damage.get(
            "severity",
            "MODERATE",
        )


        if index < len(
            pricing_parts
        ):

            pricing = pricing_parts[
                index
            ]


            price_min = pricing.get(
                "price_min"
            )


            price_max = pricing.get(
                "price_max"
            )


            price_source = pricing.get(
                "price_source",
                "AI_REFERENCE_ESTIMATE",
            )

        else:

            price_min = 3000

            price_max = 12000

            price_source = (
                "AI_REFERENCE_ESTIMATE"
            )


        if price_min is None:

            price_min = 3000


        if price_max is None:

            price_max = 12000


        price_min = safe_int(
            price_min,
            3000,
        )


        price_max = safe_int(
            price_max,
            12000,
        )


        if price_max < price_min:

            price_max = price_min


        total_parts_min += price_min

        total_parts_max += price_max


        if price_source == "PUBLIC_WEB":

            public_count += 1

        else:

            estimated_count += 1


        priced_parts.append(

            {

                "part": part_name,

                "action": action,

                "severity": severity,

                "price_min": price_min,

                "price_max": price_max,

                "price_source": price_source,

                "estimated_contribution_min": price_min,

                "estimated_contribution_max": price_max,

            }

        )


    # ========================================================
    # LABOUR
    # ========================================================

    labour_min = int(
        total_parts_min * 0.15
    )


    labour_max = int(
        total_parts_max * 0.25
    )


    # ========================================================
    # PAINT
    # ========================================================

    paint_required = any(

        (

            "PAINT"
            in
            str(
                p.get(
                    "action",
                    "",
                )
            ).upper()

        )

        or

        (

            "REPLACE"
            in
            str(
                p.get(
                    "action",
                    "",
                )
            ).upper()

        )

        for p in priced_parts

    )


    if paint_required:

        paint_min = 3000

        paint_max = 12000

    else:

        paint_min = 0

        paint_max = 0


    # ========================================================
    # HIDDEN DAMAGE
    # ========================================================

    hidden_damage = damage_analysis.get(
        "potential_hidden_damage",
        []
    )


    if (

        isinstance(
            hidden_damage,
            list,
        )

        and

        hidden_damage

    ):

        hidden_damage_min = int(
            total_parts_min * 0.10
        )

        hidden_damage_max = int(
            total_parts_max * 0.20
        )

    else:

        hidden_damage_min = 0

        hidden_damage_max = 0


    # ========================================================
    # ORIGINAL TOTAL
    # ========================================================

    original_total_min = (

        total_parts_min

        +

        labour_min

        +

        paint_min

        +

        hidden_damage_min

    )


    original_total_max = (

        total_parts_max

        +

        labour_max

        +

        paint_max

        +

        hidden_damage_max

    )


    # ========================================================
    # CONTROLLED DISPLAY RANGE
    # ========================================================

    midpoint = (

        (
            total_parts_min
            +
            total_parts_max
        )
        / 2

        +

        (
            labour_min
            +
            labour_max
        )
        / 2

        +

        (
            paint_min
            +
            paint_max
        )
        / 2

        +

        (
            hidden_damage_min
            +
            hidden_damage_max
        )
        / 2

    )


    original_spread = (

        original_total_max
        -
        original_total_min

    )


    if original_spread > 10000:

        total_min = int(

            round(
                (
                    midpoint
                    -
                    5000
                )
                /
                500
            )
            *
            500

        )


        total_max = int(

            round(
                (
                    midpoint
                    +
                    5000
                )
                /
                500
            )
            *
            500

        )

    else:

        total_min = int(

            round(
                original_total_min
                /
                500
            )
            *
            500

        )


        total_max = int(

            round(
                original_total_max
                /
                500
            )
            *
            500

        )


    if total_min < 0:

        total_min = 0


    if total_max < total_min:

        total_max = total_min


    if (
        total_max
        -
        total_min
        >
        10000
    ):

        total_max = (
            total_min
            +
            10000
        )


    # ========================================================
    # COMPONENT BREAKDOWN
    # ========================================================

    component_midpoints = {

        "parts_cost": (

            total_parts_min
            +
            total_parts_max

        ) / 2,

        "labour_cost": (

            labour_min
            +
            labour_max

        ) / 2,

        "paint_cost": (

            paint_min
            +
            paint_max

        ) / 2,

        "hidden_damage_allowance": (

            hidden_damage_min
            +
            hidden_damage_max

        ) / 2,

    }


    component_total = sum(
        component_midpoints.values()
    )


    if component_total <= 0:

        component_total = 1


    half_spread = (

        total_max
        -
        total_min

    ) / 2


    controlled_components = {}


    for (
        key,
        midpoint_value
    ) in component_midpoints.items():

        share = (
            midpoint_value
            /
            component_total
        )


        component_delta = (
            half_spread
            *
            share
        )


        component_min = (
            midpoint_value
            -
            component_delta
        )


        component_max = (
            midpoint_value
            +
            component_delta
        )


        controlled_components[key] = {

            "min": int(
                round(
                    component_min
                    /
                    500
                )
                *
                500
            ),

            "max": int(
                round(
                    component_max
                    /
                    500
                )
                *
                500
            ),

        }


    # ========================================================
    # PRICING STATUS
    # ========================================================

    if (
        public_count == len(
            priced_parts
        )
        and
        priced_parts
    ):

        status = "PUBLIC_WEB"

        confidence = 82

    elif public_count > 0:

        status = "MIXED"

        confidence = 70

    else:

        status = (
            "AI_REFERENCE_ESTIMATE"
        )

        confidence = 58


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "status": status,

        "priced_parts": priced_parts,

        "parts_cost": (
            controlled_components[
                "parts_cost"
            ]
        ),

        "labour_cost": (
            controlled_components[
                "labour_cost"
            ]
        ),

        "paint_cost": (
            controlled_components[
                "paint_cost"
            ]
        ),

        "hidden_damage_allowance": (
            controlled_components[
                "hidden_damage_allowance"
            ]
        ),

        "estimated_total": {

            "min": total_min,

            "max": total_max,

        },

        "public_price_count": public_count,

        "estimated_price_count": estimated_count,

        "confidence": confidence,

        "original_total": {

            "min": original_total_min,

            "max": original_total_max,

        },

        "notes": (
            "Public web prices are indicative market observations. "
            "Components without suitable public listings use AI-generated "
            "reference estimates. The displayed preliminary exposure "
            "uses a controlled range of no more than ₹10,000 for easier "
            "surveyor review. Final repair cost requires surveyor verification."
        ),

    }


# ============================================================
# CLAIM ORCHESTRATOR
# ============================================================

def analyze_claim(
    vehicle_number,
    policy_text,
    accident_description,
    image_files,
    rc_available=False,
    dl_available=False,
):

    # --------------------------------------------------------
    # DOCUMENT AGENT
    # --------------------------------------------------------

    document_analysis = analyze_documents(

        policy_text=policy_text,

        accident_description=accident_description,

        vehicle_number=vehicle_number,

        image_files=image_files,

        rc_available=rc_available,

        dl_available=dl_available,

    )


    # --------------------------------------------------------
    # DAMAGE / VISION AGENT
    # --------------------------------------------------------

    damage_analysis = analyze_damage(

        vehicle_model=None,

        vehicle_year=None,

        accident_description=accident_description,

        image_files=image_files,

    )


    # --------------------------------------------------------
    # VEHICLE IDENTIFICATION
    # --------------------------------------------------------

    vehicle_identification = (
        damage_analysis.get(
            "vehicle_identification",
            {}
        )
    )


    vehicle_make = (
        vehicle_identification.get(
            "make",
            "Unknown"
        )
    )


    vehicle_model = (
        vehicle_identification.get(
            "model",
            "Unknown"
        )
    )


    vehicle_year = (
        vehicle_identification.get(
            "estimated_year"
        )
    )


    vehicle_generation = (
        vehicle_identification.get(
            "generation",
            "Unknown"
        )
    )


    detected_vehicle = " ".join(

        str(x)

        for x in [

            vehicle_make,

            vehicle_model,

        ]

        if (

            x

            and

            str(x).lower()
            !=
            "unknown"

        )

    ).strip()


    if not detected_vehicle:

        detected_vehicle = (
            "Unknown vehicle"
        )


    # --------------------------------------------------------
    # PRICING AGENT
    # --------------------------------------------------------

    pricing_data = search_part_prices(

        vehicle=detected_vehicle,

        year=vehicle_year,

        damaged_parts=(
            damage_analysis.get(
                "damaged_parts",
                []
            )
        ),

    )


    # --------------------------------------------------------
    # COST ENGINE
    # --------------------------------------------------------

    cost_estimation = estimate_cost(

        damage_analysis=damage_analysis,

        pricing_data=pricing_data,

    )


    # --------------------------------------------------------
    # INVESTIGATION AGENT
    # --------------------------------------------------------

    anomaly_analysis = (
        analyze_fraud_indicators(

            damage_analysis=damage_analysis,

            accident_description=(
                accident_description
            ),

            cost_estimation=cost_estimation,

        )
    )


    # --------------------------------------------------------
    # TRIAGE AGENT
    # --------------------------------------------------------

    triage_analysis = determine_triage(

        damage_analysis=damage_analysis,

        anomaly_analysis=anomaly_analysis,

        document_analysis=document_analysis,

        cost_estimation=cost_estimation,

    )


    # --------------------------------------------------------
    # AI SUMMARY
    # --------------------------------------------------------

    ai_summary = damage_analysis.get(
        "ai_summary",
        ""
    )


    if not ai_summary:

        severity = damage_analysis.get(
            "overall_severity",
            "UNKNOWN"
        )


        damaged_count = len(

            damage_analysis.get(
                "damaged_parts",
                []
            )

        )


        ai_summary = (

            "The submitted accident description and "
            "vehicle images were reviewed as a preliminary "
            "claim assessment. "

            f"The visible assessment indicates "
            f"{severity.lower()} severity with "
            f"{damaged_count} potentially affected "
            "component(s). "

            "Potential hidden damage or components "
            "requiring inspection should be verified "
            "by the surveyor before any final claim decision."

        )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "vehicle_number": vehicle_number,

        "accident_description": (
            accident_description
        ),

        "ai_summary": ai_summary,

        "vehicle_identification": {

            "make": vehicle_make,

            "model": vehicle_model,

            "estimated_year": vehicle_year,

            "generation": vehicle_generation,

            "confidence": (
                vehicle_identification.get(
                    "confidence"
                )
            ),

            "evidence": (
                vehicle_identification.get(
                    "evidence",
                    []
                )
            ),

        },

        "document_analysis": document_analysis,

        "damage_analysis": damage_analysis,

        "pricing_data": pricing_data,

        "cost_estimation": cost_estimation,

        "anomaly_analysis": anomaly_analysis,

        "triage_analysis": triage_analysis,

        "pricing_sources": (
            pricing_data.get(
                "sources",
                []
            )
        ),

        "rc_available": rc_available,

        "dl_available": dl_available,

    }