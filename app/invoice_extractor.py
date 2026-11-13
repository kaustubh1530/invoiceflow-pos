import os

from dotenv import load_dotenv
from openai import OpenAI

from app.models import Invoice


load_dotenv(override=True)


def extract_invoice_with_ai(invoice_text: str) -> Invoice:
    """
    Send extracted invoice text to OpenAI and return
    a structured Invoice object.
    """

    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY was not found. "
            "Add it to your .env file."
        )

    client = OpenAI(api_key=api_key)

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an invoice data extraction assistant for "
                    "liquor stores. Extract information only from the "
                    "provided invoice text. Do not invent missing values. "
                    "Use UNKNOWN when a UPC/barcode or item size is missing."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Extract the invoice data from the following OCR text:\n\n"
                    f"{invoice_text}"
                ),
            },
        ],
        response_format=Invoice,
    )

    invoice = response.choices[0].message.parsed

    if invoice is None:
        raise ValueError(
            "OpenAI could not return a valid structured invoice."
        )

    return invoice