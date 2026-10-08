# ============================================================
# CLAIMPILOT PDF SERVICE
# ============================================================

import io
import re

from pypdf import PdfReader


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(pdf_file):
    """
    Extract text from an uploaded PDF.

    Parameters
    ----------
    pdf_file:
        Streamlit UploadedFile or a file-like object.

    Returns
    -------
    str
        Extracted text from all readable PDF pages.
    """

    if pdf_file is None:

        return ""


    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    try:

        pdf_bytes = pdf_file.getvalue()

    except AttributeError:

        try:

            pdf_file.seek(0)

            pdf_bytes = pdf_file.read()

        except Exception as error:

            raise ValueError(
                f"Could not read PDF file: {error}"
            )


    if not pdf_bytes:

        return ""


    # --------------------------------------------------------
    # Create PDF reader
    # --------------------------------------------------------

    try:

        reader = PdfReader(
            io.BytesIO(
                pdf_bytes
            )
        )

    except Exception as error:

        raise ValueError(
            f"Could not open PDF: {error}"
        )


    # --------------------------------------------------------
    # Extract every page
    # --------------------------------------------------------

    extracted_pages = []


    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        try:

            text = page.extract_text()

        except Exception:

            text = ""


        if text:

            text = str(
                text
            ).strip()


            if text:

                extracted_pages.append(

                    f"--- Page {page_number} ---\n"
                    f"{text}"

                )


    # --------------------------------------------------------
    # Combine pages
    # --------------------------------------------------------

    full_text = "\n\n".join(
        extracted_pages
    )


    # --------------------------------------------------------
    # Basic cleanup
    # --------------------------------------------------------

    full_text = re.sub(
        r"[ \t]+",
        " ",
        full_text
    )


    full_text = re.sub(
        r"\n{3,}",
        "\n\n",
        full_text
    )


    return full_text.strip()


# ============================================================
# POLICY TEXT AVAILABILITY
# ============================================================

def has_extractable_text(
    pdf_file
):
    """
    Check whether a PDF contains extractable text.
    """

    text = extract_pdf_text(
        pdf_file
    )

    return bool(
        text.strip()
    )


# ============================================================
# POLICY TEXT SUMMARY
# ============================================================

def get_pdf_page_count(
    pdf_file
):
    """
    Return the number of pages in the uploaded PDF.
    """

    if pdf_file is None:

        return 0


    try:

        pdf_bytes = pdf_file.getvalue()

        reader = PdfReader(
            io.BytesIO(
                pdf_bytes
            )
        )

        return len(
            reader.pages
        )

    except Exception:

        return 0