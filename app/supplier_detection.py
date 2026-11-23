from typing import Optional


SUPPLIERS = {
    "breakthru": [
        "breakthru beverage",
        "breakthru",
    ],
    "southern_glazers": [
        "southern glazer",
        "southern wine & spirits",
        "southern wine and spirits",
    ],
}


def detect_supplier(invoice_text: str) -> Optional[str]:
    text = invoice_text.lower()

    for supplier_id, keywords in SUPPLIERS.items():
        for keyword in keywords:
            if keyword in text:
                return supplier_id

    return None


if __name__ == "__main__":
    test_cases = {
        "Breakthru Beverage Washington D.C.": "breakthru",
        "Southern Glazer's Wine & Spirits": "southern_glazers",
        "Unknown Distribution Company": None,
    }

    for invoice_text, expected in test_cases.items():
        result = detect_supplier(invoice_text)
        status = "PASS" if result == expected else "FAIL"

        print(f"{status} | Input: {invoice_text}")
        print(f"Expected: {expected} | Got: {result}")
        print("-" * 50)