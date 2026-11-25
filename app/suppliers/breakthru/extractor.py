
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.suppliers.breakthru.models import BreakthruInvoice


load_dotenv(override=True)


def extract_breakthru_invoice(invoice_text: str) -> BreakthruInvoice:
    """
    Extract structured invoice information from Breakthru OCR text.

    Only use information supported by the supplied invoice text.
    Do not invent missing values.
    """

    if not invoice_text or not invoice_text.strip():
        raise ValueError("Invoice text is empty.")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY was not found. Check your .env file."
        )

    client = OpenAI(api_key=api_key)

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
You extract structured product information from Breakthru Beverage invoice OCR text.

Use only information supported by the supplied OCR text and the printed invoice column mapping.

EXACT COLUMN MAPPING:

- Cases: Printed case quantity only. Ignore handwritten numbers, circles, ticks, and annotations. Return null if unreadable.
- Btls: Printed individual bottle quantity. Map to bottle_quantity.
- Pieces: Supplier product item number. Map to item_number. It is not a quantity.
- Item: UPC or barcode. Map to upc_or_barcode.
- Size: Map to item_size.
- BPC: Bottles per case. Map to bottles_per_case.
- Description: Map to product_name.
- Unit Price: Map to unit_price.
- Unit Disc: Map to unit_discount.
- Unit Price Net: Map to net_unit_price.
- Net Btl: Map to net_bottle_price.
- Net Sales: Map to net_sales.

STRICT EXTRACTION RULES:

1. Preserve the relationship between values and their original printed columns.
2. Never confuse Pieces with Btls.
3. Never confuse BPC with Btls.
4. Extract printed Cases values, but ignore handwritten annotations.
5. Do not infer quantities from case counts or BPC.
6. Do not calculate missing prices or quantities.
7. Do not replace missing or unreadable values with zero.
8. Use null when a value cannot be confidently identified.
9. Preserve product descriptions and barcode digits exactly when readable.
10. Extract every product row supported by the OCR text.
11. If OCR text has ambiguous column alignment, do not guess.
12. Exclude taxes, delivery charges, and non-product charges from product rows.
13. Do not invent information.
""",
            },
            {
                "role": "user",
                "content": (
                    "Extract the Breakthru invoice data from this OCR text:\n\n"
                    f"{invoice_text}"
                ),
            },
        ],
        response_format=BreakthruInvoice,
    )

    invoice = response.choices[0].message.parsed

    if invoice is None:
        raise ValueError(
            "OpenAI could not return a valid Breakthru invoice."
        )

    return invoice
