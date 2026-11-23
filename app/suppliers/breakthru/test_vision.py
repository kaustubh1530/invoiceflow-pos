
from app.suppliers.breakthru.vision_extractor import (
    extract_breakthru_invoice_from_image,
)

IMAGE_PATH = (
    "outputs/inspection/breakthru_optimized/section_1_test.jpg"
)


def main():
    print("\nStarting Breakthru Vision extraction...")
    print("Testing Section 1 only.")

    invoice = extract_breakthru_invoice_from_image(IMAGE_PATH)

    print("\nVISION EXTRACTION RESULT")
    print("=" * 60)
    print(invoice.model_dump_json(indent=2))

    print("\nExtraction summary:")
    print(f"Invoice number: {invoice.invoice_number}")
    print(f"Invoice date: {invoice.invoice_date}")
    print(f"Products extracted: {len(invoice.line_items)}")


if __name__ == "__main__":
    main()
