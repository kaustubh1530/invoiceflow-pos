import os

from dotenv import load_dotenv
from openai import OpenAI

from app.models import InvoiceData


load_dotenv()


def extract_invoice_data(invoice_text: str) -> InvoiceData:
    """
    Use OpenAI to convert raw invoice text into structured data.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. "
            "Add it to your .env file."
        )

    client = OpenAI(api_key=api_key)

    system_prompt = """
You are an invoice data extraction assistant for a liquor store.

Your job is to extract invoice information from raw OCR text and
return structured data that follows the provided schema exactly.

Important rules:
- Extract only information supported by the invoice text.
- Do not invent missing values.
- If a UPC or barcode is missing, use "UNKNOWN".
- Carefully identify each product line item.
- quantity_purchased must be an integer.
- cost_per_unit and total_cost must be numbers.
- Ignore unreadable text that cannot be confidently interpreted.
- Ensure the grand_total represents the final invoice total when available.
"""

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": (
                    "Extract the invoice data from the following OCR text:\n\n"
                    f"{invoice_text}"
                ),
            },
        ],
        response_format=InvoiceData,
    )

    invoice_data = completion.choices[0].message.parsed

    if invoice_data is None:
        raise ValueError(
            "OpenAI could not extract structured invoice data."
        )

    return invoice_data