"""
CareerPath AI - PDF Text Extractor
Extracts text content from uploaded PDF resume files.
Primary extraction via pdfplumber with PyPDF2 fallback.
"""

import io
import re
import pdfplumber
import PyPDF2


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from an uploaded PDF file (Streamlit UploadedFile object).

    Uses pdfplumber as the primary extraction engine for better layout
    preservation. Falls back to PyPDF2 if pdfplumber fails.

    Args:
        uploaded_file: Streamlit UploadedFile object or file-like object
                       with a .read() method.

    Returns:
        str: Extracted and cleaned text from the PDF.
             Returns empty string if extraction fails entirely.
    """
    try:
        pdf_bytes = uploaded_file.read()
    except Exception as e:
        print(f"[PDF Extractor] Error reading uploaded file: {e}")
        return ""

    text = _extract_with_pdfplumber(pdf_bytes)

    if not text or len(text.strip()) < 50:
        fallback_text = _extract_with_pypdf2(pdf_bytes)
        if len(fallback_text.strip()) > len(text.strip()):
            text = fallback_text

    text = _clean_text(text)
    return text


def _extract_with_pdfplumber(pdf_bytes):
    """
    Extract text using pdfplumber (primary method).

    Args:
        pdf_bytes (bytes): Raw PDF file bytes.

    Returns:
        str: Extracted text, or empty string on failure.
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            return "\n".join(pages_text)
    except Exception as e:
        print(f"[PDF Extractor] pdfplumber extraction failed: {e}")
        return ""


def _extract_with_pypdf2(pdf_bytes):
    """
    Extract text using PyPDF2 (fallback method).

    Args:
        pdf_bytes (bytes): Raw PDF file bytes.

    Returns:
        str: Extracted text, or empty string on failure.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)
        return "\n".join(pages_text)
    except Exception as e:
        print(f"[PDF Extractor] PyPDF2 extraction failed: {e}")
        return ""


def _clean_text(text):
    """
    Clean extracted text by normalising whitespace and removing artefacts.

    Args:
        text (str): Raw extracted text.

    Returns:
        str: Cleaned text.
    """
    if not text:
        return ""

    # Collapse multiple spaces into one
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse 3+ consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Final strip
    text = text.strip()

    return text
