
from pathlib import Path
from PIL import Image, ImageDraw

IMAGE_PATH = Path("outputs/inspection/sample_inv2_upright.jpg")
OUTPUT_PATH = Path("outputs/inspection/sample_inv2_grid.jpg")

image = Image.open(IMAGE_PATH).convert("RGB")
draw = ImageDraw.Draw(image)

width, height = image.size

# Draw horizontal guides every 400 pixels.
for y in range(0, height, 400):
    draw.line((0, y, width, y), fill="red", width=3)
    draw.text((20, y + 8), str(y), fill="red", stroke_width=2)

# Draw vertical guides every 400 pixels.
for x in range(0, width, 400):
    draw.line((x, 0, x, height), fill="blue", width=3)
    draw.text((x + 8, 20), str(x), fill="blue", stroke_width=2)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
image.save(OUTPUT_PATH)

print(f"Saved inspection grid: {OUTPUT_PATH}")
print(f"Image dimensions: {width} x {height}")
