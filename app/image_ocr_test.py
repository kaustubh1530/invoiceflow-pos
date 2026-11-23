from pathlib import Path

import pytesseract
from PIL import Image


def run_ocr(image_path: Path) -> str:
    """Run baseline OCR on an invoice image."""

    image = Image.open(image_path)

    print(f"\nImage: {image_path.name}")
    print(f"Dimensions: {image.size}")

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return text


def main():
    image_files = [
        Path("uploads/sample_inv2.jpg"),
        Path("uploads/sample_inv3.jpg"),
    ]

    output_dir = Path("outputs/baseline_ocr")
    output_dir.mkdir(parents=True, exist_ok=True)

    for image_path in image_files:

        if not image_path.exists():
            print(f"\n⚠ File not found: {image_path}")
            continue

        print("\n" + "=" * 60)
        print(f"OCR TEST: {image_path.name}")
        print("=" * 60)

        text = run_ocr(image_path)

        print("\nOCR RESULT")
        print("-" * 60)
        print(text)

        output_file = output_dir / f"{image_path.stem}_ocr.txt"

        output_file.write_text(
            text,
            encoding="utf-8"
        )

        print(f"\n✓ Saved OCR result: {output_file}")


if __name__ == "__main__":
    main()