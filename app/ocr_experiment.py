
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps
import pytesseract


def main():
    image_path = Path("outputs/product_table_crop.png")
    image = Image.open(image_path).convert("L")

    width, height = image.size

    print("Product table dimensions:", image.size)

    # Approximate vertical boundaries of product rows.
    # Each range is expressed as a fraction of image height.
    product_rows = {
        "cazadores_blanco": (0.17, 0.30),
        "cazadores_reposado": (0.30, 0.43),
        "elijah_craig_1": (0.43, 0.56),
        "elijah_craig_2": (0.56, 0.69),
        "st_germain": (0.69, 0.82),
        "delivery_charge": (0.82, 0.96),
    }

    output_dir = Path("outputs/product_rows")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []

    for row_name, (top_ratio, bottom_ratio) in product_rows.items():

        top = int(height * top_ratio)
        bottom = int(height * bottom_ratio)

        # Crop one product row.
        row_image = image.crop(
            (0, top, width, bottom)
        )

        # Improve contrast.
        row_image = ImageOps.autocontrast(row_image)

        # Convert to a clearer black-and-white image.
        row_image = row_image.point(
            lambda pixel: 0 if pixel < 175 else 255
        )

        # Enlarge the row.
        row_image = row_image.resize(
            (row_image.width * 2, row_image.height * 2)
        )

        # Save each individual row.
        row_path = output_dir / f"{row_name}.png"
        row_image.save(row_path)

        # Run OCR on the individual row.
        text = pytesseract.image_to_string(
            row_image,
            config="--psm 6"
        )

        result = (
            f"\n{'=' * 60}\n"
            f"PRODUCT ROW: {row_name}\n"
            f"{'=' * 60}\n"
            f"{text}\n"
        )

        all_results.append(result)

        print(result)

    # Save all row OCR results.
    result_path = Path("outputs/product_rows_ocr.txt")

    result_path.write_text(
        "\n".join(all_results),
        encoding="utf-8"
    )

    print("\n✓ Individual product row OCR completed.")
    print(f"✓ Results saved to: {result_path}")


if __name__ == "__main__":
    main()
