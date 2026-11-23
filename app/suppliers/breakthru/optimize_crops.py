
from pathlib import Path
from PIL import Image

INPUT_DIR = Path("outputs/inspection/breakthru_crops")
OUTPUT_DIR = Path("outputs/inspection/breakthru_optimized")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_WIDTH = 2200

for filename in ["section_1.jpg", "section_2.jpg", "section_3.jpg"]:
    input_path = INPUT_DIR / filename

    with Image.open(input_path) as image:
        original_size = image.size

        if image.width > MAX_WIDTH:
            new_height = round(
                image.height * MAX_WIDTH / image.width
            )
            image = image.resize(
                (MAX_WIDTH, new_height),
                Image.Resampling.LANCZOS,
            )

        output_path = OUTPUT_DIR / filename

        image.save(
            output_path,
            format="JPEG",
            quality=90,
            optimize=True,
        )

        print(f"\n{filename}")
        print(f"Original: {original_size}")
        print(f"Optimized: {image.size}")
        print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")

print("\nImage optimization complete.")
