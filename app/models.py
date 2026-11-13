from pydantic import BaseModel, Field


class InvoiceLineItem(BaseModel):
    """
    Represents one product line from a distributor invoice.
    """

    upc_or_barcode: str = Field(
        default="UNKNOWN",
        description=(
            "UPC or barcode for the product. "
            "Use UNKNOWN if it is not available."
        ),
    )

    product_name: str = Field(
        description="Name of the product."
    )

    item_size: str = Field(
        default="UNKNOWN",
        description=(
            "Product size or package size, such as 750ml, "
            "1L, 1.75L, or 12-pack. Use UNKNOWN if unavailable."
        ),
    )

    quantity_purchased: int = Field(
        description="Number of units or cases purchased."
    )

    cost_per_unit: float = Field(
        description="Cost for one unit."
    )

    total_cost: float = Field(
        description="Total cost for this line item."
    )


class Invoice(BaseModel):
    """
    Structured representation of a distributor invoice.
    """

    vendor_name: str = Field(
        description="Name of the distributor or vendor."
    )

    invoice_number: str = Field(
        description="Invoice number."
    )

    invoice_date: str = Field(
        description="Invoice date."
    )

    line_items: list[InvoiceLineItem] = Field(
        description="All products found on the invoice."
    )

    grand_total: float = Field(
        description="Final total amount for the invoice."
    )