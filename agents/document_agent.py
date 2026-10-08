import re


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_value(value):
    """
    Clean a value extracted from the policy document.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def extract_money(text, keywords):
    """
    Extract a monetary value near a specific keyword.

    Used for:
    - IDV
    - Deductible
    - Excess
    """

    if not text:
        return None

    text_lower = text.lower()

    for keyword in keywords:

        position = text_lower.find(
            keyword.lower()
        )

        if position == -1:
            continue

        section = text[
            max(0, position - 100):
            min(
                len(text),
                position + 250
            )
        ]

        matches = re.findall(
            r"(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)",
            section,
            flags=re.IGNORECASE
        )

        for match in matches:

            try:

                amount = float(
                    match.replace(
                        ",",
                        ""
                    )
                )

            except ValueError:

                continue

            # Ignore years
            if 1900 <= amount <= 2035:
                continue

            # Ignore tiny irrelevant numbers
            if amount < 500:
                continue

            return int(amount)

    return None


def find_policy_value(
    text,
    patterns
):
    """
    Search a policy document using several regex patterns.
    """

    if not text:
        return None

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            value = match.group(1).strip()

            if value:

                return value[:150]

    return None


# ============================================================
# POLICY ANALYSIS
# ============================================================

def analyze_policy(
    policy_text
):
    """
    Perform deterministic extraction of important policy
    information.

    This function deliberately does not make a final
    coverage decision.
    """

    # --------------------------------------------------------
    # POLICY NOT AVAILABLE
    # --------------------------------------------------------

    if not policy_text or not policy_text.strip():

        return {

            "policy_available":
                False,

            "policy_status":
                "NOT_AVAILABLE",

            "own_damage":
                "Manual verification required",

            "policy_number":
                "Manual verification required",

            "policy_period":
                "Manual verification required",

            "idv":
                None,

            "deductible":
                None,

            "add_ons":
                "Manual verification required",

            "exclusions":
                "Manual verification required",

            "coverage_concern":
                "Policy document was not provided."

        }


    # --------------------------------------------------------
    # NORMALIZE TEXT
    # --------------------------------------------------------

    text = str(
        policy_text
    )

    text_lower = text.lower()


    # ========================================================
    # POLICY NUMBER
    # ========================================================

    policy_number = find_policy_value(

        text,

        [

            r"""
            policy\s*
            (?:no|number|#)
            \s*[:\-]?\s*
            ([A-Z0-9\/\-]+)
            """,

            r"""
            policy\s*
            id
            \s*[:\-]?\s*
            ([A-Z0-9\/\-]+)
            """,

            r"""
            certificate\s*
            (?:no|number)
            \s*[:\-]?\s*
            ([A-Z0-9\/\-]+)
            """

        ]

    )


    # ========================================================
    # POLICY PERIOD
    # ========================================================

    policy_period = find_policy_value(

        text,

        [

            r"""
            policy\s*
            period
            \s*[:\-]?\s*
            (.{5,100})
            """,

            r"""
            period\s*
            of\s*
            insurance
            \s*[:\-]?\s*
            (.{5,100})
            """,

            r"""
            period\s*
            \s*[:\-]?\s*
            (.{5,100})
            """

        ]

    )


    # ========================================================
    # IDV
    # ========================================================

    idv = extract_money(

        text,

        [

            "IDV",

            "Insured Declared Value",

            "insured declared value"

        ]

    )


    # ========================================================
    # DEDUCTIBLE / EXCESS
    # ========================================================

    deductible = extract_money(

        text,

        [

            "deductible",

            "compulsory excess",

            "voluntary excess",

            "excess"

        ]

    )


    # ========================================================
    # OWN DAMAGE COVERAGE
    # ========================================================

    own_damage_found = any(

        keyword in text_lower

        for keyword in [

            "own damage",

            "own-damage",

            "od cover",

            "od policy",

            "loss or damage to the insured vehicle",

            "loss or damage to the vehicle"

        ]

    )


    if own_damage_found:

        own_damage = (
            "Own-damage coverage indicated"
        )

    else:

        own_damage = (
            "Manual verification required"
        )


    # ========================================================
    # ADD-ONS
    # ========================================================

    add_on_keywords = [

        "zero depreciation",

        "nil depreciation",

        "roadside assistance",

        "engine protection",

        "return to invoice",

        "consumables",

        "key replacement",

        "tyre protection",

        "personal accident",

        "invoice protection"

    ]


    detected_addons = [

        addon

        for addon in add_on_keywords

        if addon in text_lower

    ]


    if detected_addons:

        addons = ", ".join(
            detected_addons
        )

    else:

        addons = (
            "Manual verification required"
        )


    # ========================================================
    # EXCLUSIONS
    # ========================================================

    exclusion_keywords = [

        "wear and tear",

        "driving without a valid licence",

        "driving licence",

        "alcohol",

        "intoxication",

        "contributory negligence",

        "mechanical breakdown",

        "electrical breakdown",

        "racing",

        "speed testing",

        "commercial use",

        "unauthorized use"

    ]


    detected_exclusions = [

        exclusion

        for exclusion in exclusion_keywords

        if exclusion in text_lower

    ]


    if detected_exclusions:

        exclusions = ", ".join(
            detected_exclusions
        )

    else:

        exclusions = (
            "Manual verification required"
        )


    # ========================================================
    # POLICY STATUS
    # ========================================================

    policy_status = "AVAILABLE"


    # ========================================================
    # COVERAGE CONCERN
    # ========================================================

    coverage_concern = (

        "Policy information was extracted for "
        "preliminary review. Final coverage "
        "interpretation requires verification "
        "by the appropriate insurance professional."

    )


    # ========================================================
    # RETURN POLICY ANALYSIS
    # ========================================================

    return {

        "policy_available":
            True,

        "policy_status":
            policy_status,

        "own_damage":
            own_damage,

        "policy_number":
            policy_number
            or
            "Manual verification required",

        "policy_period":
            policy_period
            or
            "Manual verification required",

        "idv":
            idv,

        "deductible":
            deductible,

        "add_ons":
            addons,

        "exclusions":
            exclusions,

        "coverage_concern":
            coverage_concern

    }


# ============================================================
# DOCUMENT / EVIDENCE ANALYSIS
# ============================================================

def analyze_documents(
    policy_text,
    accident_description,
    vehicle_number,
    image_files,
    rc_available=False,
    dl_available=False
):
    """
    Check whether the main claim evidence is available.

    Required evidence for the prototype:

    1. Insurance policy
    2. Registration information
    3. Accident description
    4. Vehicle damage images

    RC and Driving Licence are optional additional evidence.
    """

    # ========================================================
    # TRACK AVAILABLE / MISSING DOCUMENTS
    # ========================================================

    missing_documents = []

    available_documents = []


    # --------------------------------------------------------
    # INSURANCE POLICY
    # --------------------------------------------------------

    if (
        policy_text
        and
        policy_text.strip()
    ):

        available_documents.append(
            "Insurance policy"
        )

    else:

        missing_documents.append(
            "Insurance policy"
        )


    # --------------------------------------------------------
    # REGISTRATION INFORMATION
    # --------------------------------------------------------

    if (
        vehicle_number
        and
        vehicle_number.strip()
    ):

        available_documents.append(
            "Registration information"
        )

    else:

        missing_documents.append(
            "Registration information"
        )


    # --------------------------------------------------------
    # ACCIDENT DESCRIPTION
    # --------------------------------------------------------

    if (
        accident_description
        and
        accident_description.strip()
    ):

        available_documents.append(
            "Accident description"
        )

    else:

        missing_documents.append(
            "Accident description"
        )


    # --------------------------------------------------------
    # VEHICLE IMAGES
    # --------------------------------------------------------

    if image_files:

        try:

            image_count = len(
                image_files
            )

        except TypeError:

            image_count = 1


        available_documents.append(

            f"Vehicle damage images: "
            f"{image_count}"

        )

    else:

        missing_documents.append(
            "Vehicle damage images"
        )


    # --------------------------------------------------------
    # RC
    # --------------------------------------------------------

    if rc_available:

        available_documents.append(
            "RC copy"
        )


    # --------------------------------------------------------
    # DRIVING LICENCE
    # --------------------------------------------------------

    if dl_available:

        available_documents.append(
            "Driving Licence copy"
        )


    # ========================================================
    # REQUIRED EVIDENCE COMPLETENESS
    # ========================================================

    required_items = 4

    completed_required = 0


    if (
        policy_text
        and
        policy_text.strip()
    ):

        completed_required += 1


    if (
        vehicle_number
        and
        vehicle_number.strip()
    ):

        completed_required += 1


    if (
        accident_description
        and
        accident_description.strip()
    ):

        completed_required += 1


    if image_files:

        completed_required += 1


    evidence_completeness = int(

        (
            completed_required
            /
            required_items
        )
        *
        100

    )


    # ========================================================
    # STATUS
    # ========================================================

    if evidence_completeness == 100:

        status = "COMPLETE"

    elif evidence_completeness >= 50:

        status = "PARTIALLY_COMPLETE"

    else:

        status = "INCOMPLETE"


    # ========================================================
    # POLICY ANALYSIS
    # ========================================================

    policy_analysis = analyze_policy(
        policy_text
    )


    # ========================================================
    # FINAL DOCUMENT ANALYSIS
    # ========================================================

    return {

        "status":
            status,

        "evidence_completeness":
            evidence_completeness,

        "available_documents":
            available_documents,

        "missing_documents":
            missing_documents,

        "verification_required":
            bool(
                missing_documents
            ),

        "policy_analysis":
            policy_analysis

    }