
def validate_invoice(invoice: dict) -> list[str]:
    """
    Validate extracted invoice data.
    Returns warnings for missing or inconsistent values.
    """
    warnings = []

    if invoice.get("vendor_name") == "UNKNOWN":
        warnings.append("Vendor name is missing.")

    if invoice.get("invoice_number") == "UNKNOWN":
        warnings.append("Invoice number is missing.")

    if invoice.get("invoice_date") == "UNKNOWN":
        warnings.append("Invoice date is missing.")

    line_items = invoice.get("line_items", [])

    if not line_items:
        warnings.append("No invoice line items were extracted.")

    calculated_total = 0.0

    for index, item in enumerate(line_items, start=1):
        name = item.get("product_name", "UNKNOWN")
        quantity = item.get("quantity_purchased", 0)
        unit_cost = item.get("cost_per_unit", 0)
        total_cost = item.get("total_cost", 0)
        item_size = item.get("item_size", "UNKNOWN")

        if name == "UNKNOWN":
            warnings.append(f"Line {index}: Product name is missing.")

        if item_size == "UNKNOWN":
            warnings.append(
                f"Line {index} ({name}): Item size needs review."
            )

        if quantity <= 0:
            warnings.append(f"Line {index} ({name}): Invalid quantity.")

        if unit_cost <= 0:
            warnings.append(f"Line {index} ({name}): Unit cost needs review.")

        if total_cost <= 0:
            warnings.append(f"Line {index} ({name}): Total cost needs review.")

        expected_total = quantity * unit_cost

        if abs(expected_total - total_cost) > 0.01:
            warnings.append(
                f"Line {index} ({name}): Quantity × unit cost "
                "does not match total cost."
            )

        calculated_total += total_cost

    grand_total = invoice.get("grand_total", 0)

    if abs(calculated_total - grand_total) > 0.01:
        warnings.append(
            "Sum of line-item totals does not match the invoice grand total."
        )

    return warnings
