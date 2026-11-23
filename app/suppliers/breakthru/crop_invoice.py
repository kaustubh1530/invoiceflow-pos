
from pathlib import Path
from PIL import Image

INPUT_IMAGE = Path(
    "outputs/inspection/sample_inv2_upright.jpg"
)

OUTPUT_DIR = Path("outputs/inspection/breakthru_crops")

# Approximate coordinates identified from the inspection grid.
HEADER_TOP = 1370
HEADER_BOTTOM = 1550

SECTIONS = [
    ("section_1.jpg", 1550, 2850),
    ("section_2.jpg", 2750, 4100),
    ("section_3.jpg", 4000, 5450),
]


def main():
    image = Image.open(INPUT_IMAGE).convert("RGB")
    width, height = image.size

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    header = image.crop(
        (0, HEADER_TOP, width, HEADER_BOTTOM)
    )

    for filename, top, bottom in SECTIONS:
        # Crop the product rows.
        product_rows = image.crop(
            (0, top, width, min(bottom, height))
        )

        # Repeat the column headings at the top of each crop.
        combined = Image.new(
            "RGB",
            (width, header.height + product_rows.height),
            "white",
        )

        combined.paste(header, (0, 0))
        combined.paste(product_rows, (0, header.height))

        output_path = OUTPUT_DIR / filename
        combined.save(output_path, quality=95)

        print(f"Saved: {output_path}")
        print(f"Dimensions: {combined.size}")

    print("\nThree invoice sections created.")


if __name__ == "__main__":
    main()
