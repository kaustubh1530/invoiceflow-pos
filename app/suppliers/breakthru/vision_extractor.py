
import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.suppliers.breakthru.models import BreakthruInvoice


load_dotenv(override=True)


def encode_invoice_image(image_path: str) -> str:
    """Convert an invoice image into a base64 data URL."""

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Invoice image not found: {path}")

    supported_extensions = {".jpg", ".jpeg", ".png"}

    if path.suffix.lower() not in supported_extensions:
        raise ValueError("Supported images: JPG, JPEG, PNG.")

    image_bytes = path.read_bytes()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    mime_type = (
        "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    )

    return f"data:{mime_type};base64,{encoded_image}"


def extract_breakthru_invoice_from_image(
    image_path: str,
) -> BreakthruInvoice:
    """
    Read a Breakthru invoice image directly using Vision AI.

    Returns structured data using the Breakthru Pydantic model.
    """

    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY was not found. Check your .env file."
        )

    image_data_url = encode_invoice_image(image_path)

    client = OpenAI(api_key=api_key)

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are an invoice extraction specialist for Breakthru Beverage.

Read the supplied invoice image directly. Extract only printed
information that is visibly supported by the image.

IMPORTANT RULES:

1. Ignore handwritten notes, circles, ticks, and counting marks.
2. Read the printed table columns carefully.
3. Cases means the number of cases purchased.
4. Btls means the number of individual bottles.
5. Pieces contains the supplier item number.
6. Item contains the UPC or barcode.
7. Keep item number and UPC separate.
8. Size is the printed bottle or package size.
9. BPC means bottles per case.
10. Extract Unit Price, Unit Disc, Unit Price Net,
    Net Btl, and Net Sales into their correct fields.
11. Do not confuse prices from adjacent columns.
12. Do not invent missing or unreadable values.
13. Do not calculate missing quantities or prices.
14. Do not include delivery fees, taxes, or other charges
    as product line items.
15. Extract only product rows visible on this page.
16. The invoice may have multiple pages. Do not assume
    this page contains every product or the final invoice total.
17. If a value cannot be read confidently, leave it null.
18. Preserve product descriptions as printed.
""",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract the printed Breakthru invoice data "
                            "from this image. This is page 1 of a "
                            "multi-page invoice."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url,
                            "detail": "low",
                        },
                    },
                ],
            },
        ],
        response_format=BreakthruInvoice,
    )

    print("Finish reason:", response.choices[0].finish_reason)
    print("Usage:", response.usage)

    result = response.choices[0].message

    if result.refusal:
        raise ValueError(f"Vision extraction refused: {result.refusal}")

    if result.parsed is None:
        raise ValueError(
            "Vision AI could not return a valid structured invoice."
        )

    return result.parsed
