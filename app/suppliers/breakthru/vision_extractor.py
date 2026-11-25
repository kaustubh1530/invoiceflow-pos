
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
You are a specialist in extracting printed data from Breakthru Beverage invoices.

Extract every visible product row accurately using the supplied structured schema.

EXACT INVOICE COLUMN MAPPING:

1. Cases: On the supplied Breakthru invoice images, the entries visible in the Cases column are handwritten circled annotations. They are NOT printed supplier quantities. Therefore, return null for case_quantity for these rows. Never extract the handwritten circled numbers as quantities. Do not infer case quantities from Btls or BPC.

2. Btls: Extract the printed individual bottle quantity. Map to bottle_quantity. This is the actual quantity of bottles received.

3. Pieces: This column contains the supplier product item number. Map to item_number. Never interpret it as a quantity.

4. Item: This column contains the UPC or barcode. Map to upc_or_barcode. Preserve printed digits exactly.

5. Size: Map to item_size.

6. BPC: Extract bottles per case. Map to bottles_per_case. Never confuse BPC with Btls.

7. Description: Preserve the printed description. Map to product_name.

8. Pricing:
Unit Price -> unit_price
Unit Disc -> unit_discount
Unit Price Net -> net_unit_price
Net Btl -> net_bottle_price
Net Sales -> net_sales

STRICT RULES:

- Read each product row horizontally.
- Keep values aligned with their correct columns.
- Extract printed Cases quantities but ignore handwritten annotations.
- Never confuse Pieces with Btls.
- Never confuse BPC with Btls.
- Never calculate or infer missing values.
- Never replace unreadable values with zero.
- Use null for missing or uncertain values.
- Extract every visible product row.
- Preserve product descriptions and barcode digits.
- Exclude taxes, delivery fees, and non-product charges.
- Never invent information.
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
