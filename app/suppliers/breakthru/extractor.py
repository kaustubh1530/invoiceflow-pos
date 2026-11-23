
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
You extract printed data from Breakthru Beverage invoices.

Extract only information supported by the supplied invoice text.

IMPORTANT RULES:

1. Ignore handwritten notes, counting marks, circles, and ticks.
2. Do not interpret handwritten notes as product quantities.
3. Extract printed case quantity and bottle quantity separately.
4. Keep supplier item number separate from UPC/barcode.
5. Extract BPC (bottles per case) separately from bottle quantity.
6. Preserve product descriptions and bottle sizes.
7. Extract original unit price, unit discount, net unit price,
   net bottle price, and net sales into their respective fields.
8. Do not calculate missing prices or quantities.
9. Do not guess values when OCR is unclear.
10. Leave missing optional values as null.
11. Use the invoice number and date exactly as printed when readable.
12. Include actual product lines only. Do not treat delivery fees,
    taxes, or other charges as products.
13. Do not assume every row is readable just because it resembles
    a product row.

The OCR may contain errors. If a value is ambiguous, leave it null
rather than making an unsupported guess.
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
