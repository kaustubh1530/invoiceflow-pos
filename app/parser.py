
import json
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageOps
from pypdf import PdfReader

from app.invoice_extractor import extract_invoice_with_ai
from app.validator import validate_invoice


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def extract_text_with_pypdf(file_path: str) -> str:
    """Extract embedded text from a PDF."""

    try:
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

    except Exception as error:
        print(f"⚠ PDF text extraction failed: {error}")
        return ""


def preprocess_image(image):
    """Prepare an image for OCR."""

    processed_image = ImageOps.grayscale(image)

    enhancer = ImageEnhance.Contrast(processed_image)
    processed_image = enhancer.enhance(2.5)

    sharpener = ImageEnhance.Sharpness(processed_image)
    processed_image = sharpener.enhance(2)

    return processed_image


def run_ocr_on_image(image, page_number: int = 1) -> str:
    """Preprocess an image and extract text using Tesseract."""

    print(f"\n🔍 Processing image/page {page_number}...")

    processed_image = preprocess_image(image)

    output_path = Path("uploads") / f"processed_page_{page_number}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    processed_image.save(output_path)
    print(f"✓ Saved processed image: {output_path}")

    print(f"🔍 Running OCR on page {page_number}...")

    text = pytesseract.image_to_string(
        processed_image,
        config="--psm 6"
    )

    if text and text.strip():
        print(f"✓ OCR text extracted from page {page_number}")
        return text

    print(f"⚠ OCR could not read page {page_number}")
    return ""


def extract_text_with_ocr(file_path: str) -> str:
    """OCR a PDF by converting its pages into images."""

    print("\nStarting PDF OCR fallback...")

    pages = convert_from_path(file_path, dpi=400)
    pages_text = []

    for page_number, image in enumerate(pages, start=1):
        text = run_ocr_on_image(image, page_number)

        if text.strip():
            pages_text.append(text)

    return "\n".join(pages_text)


def extract_text_from_image(file_path: str) -> str:
    """Open a JPG, JPEG, or PNG file and perform OCR directly."""

    print("\nStarting image OCR...")

    with Image.open(file_path) as image:
        image.load()
        text = run_ocr_on_image(image, page_number=1)

    return text


def extract_invoice_text(file_path: str) -> str:
    """
    Extract text from supported invoice files.

    PDFs:
        1. Try embedded text extraction.
        2. If empty or failed, use OCR.

    Images:
        Perform OCR directly.
    """

    invoice_path = Path(file_path)

    if not invoice_path.exists():
        raise FileNotFoundError(f"Invoice file not found: {file_path}")

    print(f"\nProcessing invoice: {invoice_path.name}")

    extension = invoice_path.suffix.lower()

    # Handle image files directly
    if extension in SUPPORTED_IMAGE_EXTENSIONS:
        extracted_text = extract_text_from_image(str(invoice_path))

    # Handle PDFs
    elif extension == ".pdf":
        extracted_text = extract_text_with_pypdf(str(invoice_path))

        if extracted_text.strip():
            print("\n✓ Using digital PDF text extraction.")
        else:
            print("\n⚠ No embedded PDF text found. Switching to OCR.")
            extracted_text = extract_text_with_ocr(str(invoice_path))

    else:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            "Supported types: PDF, JPG, JPEG, PNG."
        )

    if not extracted_text or not extracted_text.strip():
        raise ValueError(
            "No text could be extracted from this invoice."
        )

    print("\n✓ Text extraction completed.")

    return extracted_text


def save_extracted_text(extracted_text: str) -> Path:
    """Save raw extracted text for debugging and auditing."""

    output_path = Path("outputs/extracted_invoice_text.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        extracted_text,
        encoding="utf-8"
    )

    print(f"\n✓ Extracted text saved to: {output_path}")

    return output_path


def process_invoice(file_path: str) -> dict:
    """
    Run the complete InvoiceFlow-POS processing pipeline.

    File → Text Extraction → OCR → Save Text →
    OpenAI → Validation → Structured Invoice Data
    """

    # Step 1: Extract invoice text
    extracted_text = extract_invoice_text(file_path)

    print("\n✓ Text extraction completed.")

    # Step 2: Save raw extracted text
    save_extracted_text(extracted_text)

    # Step 3: Show text preview
    print("\nOCR TEXT PREVIEW")
    print("-" * 55)
    print(extracted_text[:1000])

    # Step 4: Send text to OpenAI
    print("\n🤖 Sending invoice text to OpenAI...")

    invoice = extract_invoice_with_ai(extracted_text)

    # Step 5: Convert Pydantic model to dictionary
    invoice_data = invoice.model_dump()

    # Step 6: Validate extracted data
    print("\n🔎 Validating invoice data...")

    warnings = validate_invoice(invoice_data)

    if warnings:
        print("\n⚠ INVOICE VALIDATION WARNINGS")
        print("-" * 55)

        for warning in warnings:
            print(f"⚠ {warning}")
    else:
        print("\n✓ No validation warnings.")

    return invoice_data


def main():
    """Test the complete invoice extraction pipeline."""

    invoice_path = Path("uploads/sample_inv1.pdf")

    print("\n" + "=" * 55)
    print("InvoiceFlow-POS — AI Invoice Processing")
    print("=" * 55)

    invoice_data = process_invoice(str(invoice_path))

    print("\n" + "=" * 55)
    print("STRUCTURED INVOICE DATA")
    print("=" * 55)

    print(json.dumps(invoice_data, indent=4))


if __name__ == "__main__":
    main()
