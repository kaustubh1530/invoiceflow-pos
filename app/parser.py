import json
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader

from app.invoice_extractor import extract_invoice_with_ai


def extract_text_with_pypdf(file_path: str) -> str:
    """
    Try to extract embedded text from a normal PDF.
    """

    reader = PdfReader(file_path)
    pages_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text and text.strip():
            pages_text.append(text)
            print(f"✓ Extracted digital text from page {page_number}")
        else:
            print(f"⚠ No digital text found on page {page_number}")

    return "\n".join(pages_text)


def extract_text_with_ocr(file_path: str) -> str:
    """
    Convert a scanned PDF into images and extract text using OCR.
    """

    print("\nStarting OCR fallback...")

    # Convert PDF pages into images.
    # 300 DPI provides good image quality for invoice OCR.
    pages = convert_from_path(file_path, dpi=300)

    pages_text = []

    for page_number, image in enumerate(pages, start=1):
        print(f"🔍 Running OCR on page {page_number}...")

        text = pytesseract.image_to_string(image)

        if text and text.strip():
            pages_text.append(text)
            print(f"✓ OCR text extracted from page {page_number}")
        else:
            print(f"⚠ OCR could not read page {page_number}")

    return "\n".join(pages_text)


def extract_invoice_text(file_path: str) -> str:
    """
    Extract text from an invoice PDF.

    First tries normal PDF text extraction.
    If no text is found, falls back to OCR.
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    print(f"\nProcessing invoice: {pdf_path.name}")

    # Step 1: Try regular PDF text extraction.
    extracted_text = extract_text_with_pypdf(str(pdf_path))

    if extracted_text.strip():
        print("\n✓ Using digital PDF text extraction.")
        return extracted_text

    # Step 2: Fall back to OCR for scanned invoices.
    print("\n⚠ No embedded text found. Switching to OCR.")

    extracted_text = extract_text_with_ocr(str(pdf_path))

    if not extracted_text.strip():
        raise ValueError(
            "No text could be extracted from this invoice, "
            "even after OCR."
        )

    print("\n✓ OCR extraction completed successfully.")

    return extracted_text


if __name__ == "__main__":
    invoice_path = Path("uploads/sample_inv1.pdf")

    print("\n" + "=" * 55)
    print("InvoiceFlow-POS — AI Invoice Processing")
    print("=" * 55)

    # Extract text using the PDF + OCR fallback pipeline.
    extracted_text = extract_invoice_text(str(invoice_path))

    print("\n✓ Text extraction completed.")

    # Show a preview so we can verify what the AI receives.
    print("\nOCR TEXT PREVIEW")
    print("-" * 55)
    print(extracted_text[:1000])

    # Send the extracted text to OpenAI.
    print("\n🤖 Sending invoice text to OpenAI...")

    invoice = extract_invoice_with_ai(extracted_text)

    # Convert the validated Pydantic object to a Python dictionary.
    invoice_json = invoice.model_dump()

    print("\n" + "=" * 55)
    print("STRUCTURED INVOICE DATA")
    print("=" * 55)

    print(json.dumps(invoice_json, indent=4))