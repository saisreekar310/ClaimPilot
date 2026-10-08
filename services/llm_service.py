# ============================================================
# CLAIMPILOT GEMINI LLM SERVICE
# ============================================================

import json
import os
import re
import time

from google import genai
from google.genai import types
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# API KEY
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY is missing from the .env file."
    )


# ============================================================
# MODEL CONFIGURATION
# ============================================================

PRIMARY_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash"
)


FALLBACK_MODEL = os.getenv(
    "GEMINI_FALLBACK_MODEL",
    "gemini-3.5-flash-lite"
)


SECOND_FALLBACK_MODEL = os.getenv(
    "GEMINI_SECOND_FALLBACK_MODEL",
    "gemini-3.6-flash"
)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# MODEL LIST
# ============================================================

MODELS_TO_TRY = [

    PRIMARY_MODEL,

    FALLBACK_MODEL,

    SECOND_FALLBACK_MODEL,

]


# Remove duplicates while preserving order

MODELS_TO_TRY = list(
    dict.fromkeys(
        MODELS_TO_TRY
    )
)


# ============================================================
# RETRY SETTINGS
# ============================================================

MAX_RETRIES_PER_MODEL = 3


RETRY_DELAYS = [
    2,
    4,
    8,
]


# ============================================================
# JSON CLEANING
# ============================================================

def clean_json_response(
    response_text
):
    """
    Convert Gemini's response into a Python dictionary.

    Handles:
    - normal JSON
    - ```json ... ```
    - accidental Markdown wrappers
    """

    if not response_text:

        raise ValueError(
            "Gemini returned an empty response."
        )


    text = str(
        response_text
    ).strip()


    # --------------------------------------------------------
    # Remove Markdown code fences
    # --------------------------------------------------------

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )


    text = re.sub(
        r"^```\s*",
        "",
        text
    )


    text = re.sub(
        r"\s*```$",
        "",
        text
    )


    text = text.strip()


    # --------------------------------------------------------
    # First attempt: direct JSON
    # --------------------------------------------------------

    try:

        parsed = json.loads(
            text
        )

        if isinstance(
            parsed,
            dict
        ):

            return parsed

    except json.JSONDecodeError:

        pass


    # --------------------------------------------------------
    # Second attempt:
    # Find JSON object inside response
    # --------------------------------------------------------

    first_brace = text.find(
        "{"
    )


    last_brace = text.rfind(
        "}"
    )


    if (
        first_brace != -1
        and
        last_brace != -1
        and
        last_brace > first_brace
    ):

        json_text = text[
            first_brace:
            last_brace + 1
        ]


        try:

            parsed = json.loads(
                json_text
            )


            if isinstance(
                parsed,
                dict
            ):

                return parsed

        except json.JSONDecodeError:

            pass


    # --------------------------------------------------------
    # If parsing fails
    # --------------------------------------------------------

    raise ValueError(
        "Gemini returned invalid JSON."
    )


# ============================================================
# ERROR CLASSIFICATION
# ============================================================

def is_retryable_error(
    error
):
    """
    Determine whether the error is likely temporary.

    Retry:
    - 429
    - 500
    - 502
    - 503
    - 504

    Do not repeatedly retry:
    - 400
    - 401
    - 403
    - 404
    - malformed request
    """

    message = str(
        error
    ).lower()


    retryable_codes = [

        "429",

        "500",

        "502",

        "503",

        "504",

        "resource_exhausted",

        "unavailable",

        "temporarily",

        "overloaded",

        "timeout",

    ]


    return any(

        code in message

        for code in retryable_codes

    )


# ============================================================
# GEMINI CALL
# ============================================================

def analyze_with_gemini(
    prompt,
    image_parts=None
):
    """
    Send a multimodal request to Gemini.

    Parameters
    ----------
    prompt : str
        Analysis instructions.

    image_parts : list
        Gemini image Parts created using
        types.Part.from_bytes(...).

    Returns
    -------
    dict
        Parsed JSON response.
    """


    if not prompt:

        raise ValueError(
            "Gemini prompt cannot be empty."
        )


    if image_parts is None:

        image_parts = []


    # ========================================================
    # BUILD CONTENT
    # ========================================================

    contents = [

        prompt

    ]


    # Add uploaded images

    if image_parts:

        contents.extend(
            image_parts
        )


    # ========================================================
    # GENERATION CONFIGURATION
    # ========================================================

    config = types.GenerateContentConfig(

        temperature=0.2,

        response_mime_type=(
            "application/json"
        ),

    )


    last_error = None


    # ========================================================
    # TRY EACH MODEL
    # ========================================================

    for model_name in MODELS_TO_TRY:

        print(
            f"\n🤖 {model_name} "
            f"attempting Gemini analysis..."
        )


        # ----------------------------------------------------
        # RETRIES
        # ----------------------------------------------------

        for attempt in range(
            MAX_RETRIES_PER_MODEL
        ):

            try:

                print(

                    f"📡 Attempt "
                    f"{attempt + 1}/"
                    f"{MAX_RETRIES_PER_MODEL}"

                )


                # =================================================
                # GEMINI REQUEST
                # =================================================

                response = (
                    client.models.generate_content(

                        model=model_name,

                        contents=contents,

                        config=config

                    )
                )


                # =================================================
                # GET TEXT
                # =================================================

                response_text = (
                    getattr(
                        response,
                        "text",
                        None
                    )
                )


                if not response_text:

                    raise ValueError(
                        "Gemini returned no text."
                    )


                # =================================================
                # PARSE JSON
                # =================================================

                parsed = clean_json_response(
                    response_text
                )


                print(
                    f"✅ {model_name} "
                    f"returned valid JSON."
                )


                return parsed


            except Exception as error:

                last_error = error


                print(

                    f"❌ {model_name} "
                    f"attempt {attempt + 1} "
                    f"failed: {error}"

                )


                # =================================================
                # NON-RETRYABLE ERROR
                # =================================================

                if not is_retryable_error(
                    error
                ):

                    print(

                        f"⚠️ Error is not considered "
                        f"retryable. Moving to next model."

                    )

                    break


                # =================================================
                # RETRY
                # =================================================

                if (
                    attempt
                    <
                    MAX_RETRIES_PER_MODEL - 1
                ):

                    delay = RETRY_DELAYS[
                        min(
                            attempt,
                            len(
                                RETRY_DELAYS
                            ) - 1
                        )
                    ]


                    print(

                        f"⏳ Waiting "
                        f"{delay}s before retry..."

                    )


                    time.sleep(
                        delay
                    )


        # ----------------------------------------------------
        # MOVE TO NEXT MODEL
        # ----------------------------------------------------

        print(

            f"⚠️ Moving to next Gemini model..."

        )


    # ========================================================
    # ALL MODELS FAILED
    # ========================================================

    raise RuntimeError(

        "All configured Gemini models failed. "
        f"Last error: {last_error}"

    )


# ============================================================
# SIMPLE TEXT GENERATION
# ============================================================

def generate_text(
    prompt
):
    """
    Optional helper for future ClaimPilot agents that only
    need text rather than structured JSON.

    This does NOT affect the Vision Agent.
    """

    if not prompt:

        raise ValueError(
            "Prompt cannot be empty."
        )


    last_error = None


    for model_name in MODELS_TO_TRY:

        for attempt in range(
            MAX_RETRIES_PER_MODEL
        ):

            try:

                response = (
                    client.models.generate_content(

                        model=model_name,

                        contents=prompt,

                        config=types.GenerateContentConfig(

                            temperature=0.2

                        )

                    )
                )


                text = getattr(
                    response,
                    "text",
                    None
                )


                if text:

                    return text.strip()


                raise ValueError(
                    "Gemini returned empty text."
                )


            except Exception as error:

                last_error = error


                if not is_retryable_error(
                    error
                ):

                    break


                if (
                    attempt
                    <
                    MAX_RETRIES_PER_MODEL - 1
                ):

                    delay = RETRY_DELAYS[
                        min(
                            attempt,
                            len(
                                RETRY_DELAYS
                            ) - 1
                        )
                    ]


                    time.sleep(
                        delay
                    )


    raise RuntimeError(

        "All configured Gemini models failed "
        f"for text generation. "
        f"Last error: {last_error}"

    )