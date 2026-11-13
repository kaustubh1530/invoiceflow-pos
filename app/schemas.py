from pydantic import BaseModel, Field


class LineItem(BaseModel):
    """A single product line from a distributor invoice."""

    upc_or_barcode: str = Field(
        default="UNKNOWN",
        description="Product UPC or barcode. Use UNKNOWN if not found.",
    )
    product_name: str
    quantity_purchased: int
    iteam_size: int
    cost_per_unit: float
    total_cost: float


class Invoice(BaseModel):
    """Structured data extracted from a distributor invoice."""

    vendor_name: str
    invoice_number: str
    invoice_date: str
    line_items: list[LineItem]
    grand_total: float
