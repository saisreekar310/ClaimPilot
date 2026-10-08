from google.genai import types

from services.llm_service import analyze_with_gemini


# =========================================================
# VEHICLE + DAMAGE VISION AGENT
# =========================================================

def analyze_damage(
    vehicle_model,
    vehicle_year,
    accident_description,
    image_files
):
    """
    Gemini Vision Agent for ClaimPilot.

    The vehicle make/model/year are primarily identified
    from the uploaded images.

    vehicle_model and vehicle_year are retained in the
    function signature for compatibility with the rest
    of the application, but they are NOT required for
    vehicle identification.
    """

    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""
You are ClaimPilot's Vehicle & Damage Vision Agent.

You are analyzing images submitted for a motor insurance
claim.

Your job is to inspect ALL uploaded vehicle images together
and produce structured claim intelligence.

IMPORTANT:

1. Identify the vehicle from the images.
2. Do NOT rely on the user entering the make/model.
3. Use visible visual characteristics such as:
   - manufacturer badge
   - grille
   - headlights
   - taillights
   - body shape
   - wheel design
   - dashboard/interior if visible
   - model-specific styling
   - generation-specific design
4. If the exact model cannot be determined reliably,
   provide the closest likely identification and lower
   the confidence.
5. NEVER invent an exact model when the image does not
   provide enough evidence.

ACCIDENT DESCRIPTION:
{accident_description or "Not provided"}

USER-PROVIDED VEHICLE INFORMATION:
Make/model: {vehicle_model or "Not provided"}
Year: {vehicle_year or "Not provided"}

The user-provided vehicle information is only supporting
information. The uploaded images are the primary source
for vehicle identification.

---------------------------------------------------------
VEHICLE IDENTIFICATION
---------------------------------------------------------

Identify:

- manufacturer / make
- model
- approximate model year if visually possible
- generation / chassis if visually possible
- confidence

If exact year is uncertain, provide an approximate year
or null.

If generation is uncertain, provide null.

---------------------------------------------------------
DAMAGE ANALYSIS
---------------------------------------------------------

Inspect every uploaded image carefully.

Identify visible damaged components.

For every damaged component determine:

- component name
- severity
- recommended action
- reason for the recommendation

Recommended actions must be one of:

REPAIR
REPLACE
INSPECT

Severity must be one of:

LOW
MODERATE
HIGH
SEVERE

Look for components such as:

- front bumper
- rear bumper
- bonnet / hood
- fender
- doors
- side mirror
- headlights
- taillights
- grille
- windshield
- windows
- wheels
- tyres
- suspension components if visible
- radiator area if visible
- airbags if visible
- sensors
- cameras
- radar
- ADAS components
- exhaust
- underbody components

Do NOT claim hidden damage as confirmed if it cannot
be seen.

Instead identify possible hidden damage separately.

---------------------------------------------------------
STRUCTURAL DAMAGE
---------------------------------------------------------

Look for visual indicators of:

- frame damage
- chassis deformation
- crumple-zone deformation
- misalignment
- major panel displacement

If structural damage cannot be confirmed from images,
say so.

---------------------------------------------------------
SAFETY
---------------------------------------------------------

Identify visible safety-critical concerns.

Examples:

- deployed airbags
- damaged wheels
- damaged tyres
- exposed electrical components
- broken lights
- windshield damage
- suspension concerns

---------------------------------------------------------
ADAS
---------------------------------------------------------

Check whether visible damage may affect:

- radar
- cameras
- parking sensors
- ultrasonic sensors
- lane-assistance cameras
- adaptive cruise sensors
- other ADAS components

Do not claim that an ADAS component is damaged unless
there is visual evidence.

---------------------------------------------------------
HIDDEN DAMAGE
---------------------------------------------------------

List possible hidden damage that a surveyor/workshop
should inspect.

Examples:

- bumper reinforcement
- radiator
- condenser
- mounting brackets
- wiring
- suspension
- sensors behind bumper
- structural members

These are inspection suggestions, NOT confirmed damage.

---------------------------------------------------------
AI CLAIM SUMMARY
---------------------------------------------------------

Generate a concise professional AI claim summary.

The summary MUST combine:

1. The accident description supplied by the claimant.
2. The vehicle identified from the images.
3. The major visible damage identified from the images.
4. Overall damage severity.
5. Any important potential hidden damage or inspection
   requirement.

The summary must be approximately 3-5 sentences.

The summary must be factual and suitable for a surveyor's
claim working document.

Do NOT:

- approve the claim
- reject the claim
- determine fraud
- make a final coverage decision
- state hidden damage as confirmed
- claim that the AI has made a final repair estimate

Use wording such as "visible damage", "preliminary
assessment", "potential hidden damage", and "requires
surveyor verification" where appropriate.

---------------------------------------------------------
IMPORTANT CLAIM RULES
---------------------------------------------------------

You must NOT:

- approve the insurance claim
- reject the insurance claim
- determine final settlement
- determine fraud
- make a final coverage decision
- invent damage that is not visible
- claim exact repair cost
- claim an exact vehicle model without sufficient evidence

This is an AI-assisted preliminary assessment.

A human surveyor/claims professional must make the
final consequential decision.

---------------------------------------------------------
OUTPUT FORMAT
---------------------------------------------------------

Return ONLY valid JSON.

Use exactly this structure:

{{
    "vehicle_identification": {{
        "make": "",
        "model": "",
        "estimated_year": null,
        "generation": "",
        "confidence": 0,
        "evidence": []
    }},

    "damaged_parts": [
        {{
            "part": "",
            "severity": "",
            "recommended_action": "",
            "reason": ""
        }}
    ],

    "overall_severity": "",

    "confidence": 0,

    "ai_summary": "",

    "observations": [],

    "potential_hidden_damage": [],

    "structural_damage": {{
        "suspected": false,
        "reason": ""
    }},

    "safety_checks": [],

    "adas_checks": [],

    "image_quality": {{
        "adequate_for_assessment": true,
        "limitations": []
    }}
}}

Additional rules:

- confidence must be an integer from 0 to 100.
- vehicle_identification.confidence must be an integer
  from 0 to 100.
- estimated_year must be a number or null.
- generation must be a string or null.
- damaged_parts must always be an array.
- potential_hidden_damage must always be an array.
- observations must always be an array.
- safety_checks must always be an array.
- adas_checks must always be an array.
- ai_summary must always be a string.
- Never include Markdown.
- Never wrap the JSON in ```json.
"""


    # =====================================================
    # IMAGE PREPARATION
    # =====================================================

    image_parts = []

    if image_files:

        for image_file in image_files:

            try:

                image_bytes = image_file.getvalue()

                mime_type = (
                    getattr(
                        image_file,
                        "type",
                        None
                    )
                    or "image/jpeg"
                )

                image_parts.append(
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type
                    )
                )

            except Exception as error:

                print(
                    f"⚠️ Could not process image "
                    f"{getattr(image_file, 'name', 'unknown')}: "
                    f"{error}"
                )


    # =====================================================
    # NO IMAGES
    # =====================================================

    if not image_parts:

        return {
            "vehicle_identification": {
                "make": None,
                "model": None,
                "estimated_year": None,
                "generation": None,
                "confidence": 0,
                "evidence": []
            },

            "damaged_parts": [],

            "overall_severity": "UNKNOWN",

            "confidence": 0,

            "ai_summary": (
                "No AI claim summary could be generated "
                "because valid vehicle images were not "
                "provided. The submitted claim requires "
                "additional visual evidence before a "
                "preliminary vehicle damage assessment "
                "can be completed."
            ),

            "observations": [
                "No valid vehicle images were provided."
            ],

            "potential_hidden_damage": [],

            "structural_damage": {
                "suspected": False,
                "reason": "No images available."
            },

            "safety_checks": [],

            "adas_checks": [],

            "image_quality": {
                "adequate_for_assessment": False,
                "limitations": [
                    "No valid images were available."
                ]
            }
        }


    # =====================================================
    # GEMINI VISION CALL
    # =====================================================

    print(
        "\n🔍 Starting Vehicle + Damage Vision Agent..."
    )

    print(
        f"📸 Images supplied to Gemini: "
        f"{len(image_parts)}"
    )

    result = analyze_with_gemini(
        prompt,
        image_parts
    )


    # =====================================================
    # BASIC SAFETY NORMALIZATION
    # =====================================================

    if not isinstance(result, dict):

        print(
            "⚠️ Gemini returned an unexpected result."
        )

        return {
            "vehicle_identification": {
                "make": None,
                "model": None,
                "estimated_year": None,
                "generation": None,
                "confidence": 0,
                "evidence": []
            },

            "damaged_parts": [],

            "overall_severity": "UNKNOWN",

            "confidence": 0,

            "ai_summary": (
                "No AI claim summary could be generated "
                "because the vision model did not return "
                "a valid structured assessment."
            ),

            "observations": [
                "Gemini did not return a valid "
                "structured analysis."
            ],

            "potential_hidden_damage": [],

            "structural_damage": {
                "suspected": False,
                "reason": ""
            },

            "safety_checks": [],

            "adas_checks": [],

            "image_quality": {
                "adequate_for_assessment": False,
                "limitations": [
                    "Invalid Gemini response."
                ]
            }
        }


    # =====================================================
    # ENSURE REQUIRED FIELDS EXIST
    # =====================================================

    if "vehicle_identification" not in result:

        result["vehicle_identification"] = {
            "make": None,
            "model": None,
            "estimated_year": None,
            "generation": None,
            "confidence": 0,
            "evidence": []
        }


    if "damaged_parts" not in result:

        result["damaged_parts"] = []


    if "overall_severity" not in result:

        result["overall_severity"] = "UNKNOWN"


    if "confidence" not in result:

        result["confidence"] = 0


    if "ai_summary" not in result:

        result["ai_summary"] = (
            "The submitted accident description and "
            "vehicle images were reviewed as a "
            "preliminary claim assessment. Visible "
            "damage identified in the supplied evidence "
            "requires verification by the surveyor "
            "before any final claim decision."
        )


    if "observations" not in result:

        result["observations"] = []


    if "potential_hidden_damage" not in result:

        result["potential_hidden_damage"] = []


    if "structural_damage" not in result:

        result["structural_damage"] = {
            "suspected": False,
            "reason": ""
        }


    if "safety_checks" not in result:

        result["safety_checks"] = []


    if "adas_checks" not in result:

        result["adas_checks"] = []


    if "image_quality" not in result:

        result["image_quality"] = {
            "adequate_for_assessment": True,
            "limitations": []
        }


    # =====================================================
    # NORMALIZE VEHICLE IDENTIFICATION
    # =====================================================

    vehicle_info = result[
        "vehicle_identification"
    ]


    if not isinstance(
        vehicle_info,
        dict
    ):

        vehicle_info = {}


    vehicle_info.setdefault(
        "make",
        None
    )

    vehicle_info.setdefault(
        "model",
        None
    )

    vehicle_info.setdefault(
        "estimated_year",
        None
    )

    vehicle_info.setdefault(
        "generation",
        None
    )

    vehicle_info.setdefault(
        "confidence",
        0
    )

    vehicle_info.setdefault(
        "evidence",
        []
    )


    result[
        "vehicle_identification"
    ] = vehicle_info


    # =====================================================
    # NORMALIZE DAMAGE PARTS
    # =====================================================

    normalized_parts = []


    for part in result.get(
        "damaged_parts",
        []
    ):

        if not isinstance(
            part,
            dict
        ):

            continue


        normalized_parts.append({

            "part": part.get(
                "part",
                "Unknown component"
            ),

            "severity": str(
                part.get(
                    "severity",
                    "UNKNOWN"
                )
            ).upper(),

            "recommended_action": str(
                part.get(
                    "recommended_action",
                    "INSPECT"
                )
            ).upper(),

            "reason": part.get(
                "reason",
                ""
            )

        })


    result[
        "damaged_parts"
    ] = normalized_parts


    # =====================================================
    # NORMALIZE AI SUMMARY
    # =====================================================

    if not isinstance(
        result.get(
            "ai_summary"
        ),
        str
    ):

        result["ai_summary"] = str(
            result.get(
                "ai_summary",
                ""
            )
        )


    if not result[
        "ai_summary"
    ].strip():

        result["ai_summary"] = (
            "The submitted accident description "
            "and vehicle images were reviewed as "
            "a preliminary claim assessment. "
            "Visible damage identified in the "
            "supplied evidence requires verification "
            "by the surveyor before any final claim "
            "decision."
        )


    # =====================================================
    # NORMALIZE CONFIDENCE
    # =====================================================

    try:

        result["confidence"] = int(
            result.get(
                "confidence",
                0
            )
        )

    except (
        ValueError,
        TypeError
    ):

        result["confidence"] = 0


    try:

        vehicle_info["confidence"] = int(
            vehicle_info.get(
                "confidence",
                0
            )
        )

    except (
        ValueError,
        TypeError
    ):

        vehicle_info["confidence"] = 0


    # =====================================================
    # CLAMP CONFIDENCE
    # =====================================================

    result["confidence"] = max(
        0,
        min(
            100,
            result["confidence"]
        )
    )


    vehicle_info["confidence"] = max(
        0,
        min(
            100,
            vehicle_info["confidence"]
        )
    )


    # =====================================================
    # FINAL LOGGING
    # =====================================================

    print(
        "\n✅ Vision analysis completed."
    )


    print(
        "🚘 Detected vehicle: "
        f"{vehicle_info.get('make') or 'Unknown'} "
        f"{vehicle_info.get('model') or 'Unknown'}"
    )


    print(
        "📅 Estimated year: "
        f"{vehicle_info.get('estimated_year') or 'Unknown'}"
    )


    print(
        "🎯 Vehicle confidence: "
        f"{vehicle_info.get('confidence', 0)}%"
    )


    print(
        "🔧 Damaged components: "
        f"{len(result.get('damaged_parts', []))}"
    )


    print(
        "⚠️ Overall severity: "
        f"{result.get('overall_severity', 'UNKNOWN')}"
    )


    print(
        "🤖 AI claim summary generated."
    )


    return result