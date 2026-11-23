
import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(override=True)

IMAGE_PATH = (
    "outputs/inspection/breakthru_optimized/section_1_test.jpg"
)


def main():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise ValueError("OPENAI_API_KEY was not found.")

    image_path = Path(IMAGE_PATH)

    image_bytes = image_path.read_bytes()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    client = OpenAI(api_key=api_key)

    print("Testing raw Vision response...")
    print("Image:", image_path)
    print("Image size:", len(image_bytes), "bytes")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_completion_tokens=4000,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an invoice extraction specialist. "
                    "Read the supplied Breakthru invoice image. "
                    "Extract the printed product rows into JSON. "
                    "Ignore handwritten marks. "
                    "Keep item number, UPC, quantities, and prices "
                    "in their correct columns. Do not guess."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract the 10–15 visible product rows. "
                            "Return JSON with a line_items array. "
                            "Each item should include product_name, "
                            "item_number, upc_or_barcode, item_size, "
                            "bottles_per_case, case_quantity, "
                            "bottle_quantity, unit_price, "
                            "unit_discount, net_unit_price, "
                            "net_bottle_price, and net_sales."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                "data:image/jpeg;base64,"
                                + encoded_image
                            ),
                            "detail": "high",
                        },
                    },
                ],
            },
        ],
    )

    choice = response.choices[0]

    print("\nFinish reason:", choice.finish_reason)
    print("Usage:", response.usage)
    print("\nRaw response:\n")
    print(choice.message.content)


if __name__ == "__main__":
    main()
