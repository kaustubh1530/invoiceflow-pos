
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class BreakthruLineItem(BaseModel):
    """One printed product line from a Breakthru invoice."""

    item_number: Optional[str] = Field(
        default=None,
        description="Breakthru supplier product item number."
    )

    upc_or_barcode: Optional[str] = Field(
        default=None,
        description="Printed product UPC or barcode."
    )

    product_name: str = Field(
        description="Printed product description."
    )

    item_size: Optional[str] = Field(
        default=None,
        description="Bottle or package size, such as 375ML or 750ML."
    )

    bottles_per_case: Optional[int] = Field(
        default=None,
        description="Printed BPC value."
    )

    case_quantity: Decimal = Field(
        default=Decimal("0"),
        description="Number of cases purchased."
    )

    bottle_quantity: int = Field(
        default=0,
        description="Number of individual bottles purchased."
    )

    unit_price: Optional[Decimal] = Field(
        default=None,
        description="Original printed unit price."
    )

    unit_discount: Optional[Decimal] = Field(
        default=None,
        description="Printed discount per unit."
    )

    net_unit_price: Optional[Decimal] = Field(
        default=None,
        description="Unit price after discount."
    )

    net_bottle_price: Optional[Decimal] = Field(
        default=None,
        description="Printed net bottle price."
    )

    net_sales: Optional[Decimal] = Field(
        default=None,
        description="Final net sales amount for this line."
    )


class BreakthruInvoice(BaseModel):
    """Structured invoice data for Breakthru Beverage."""

    vendor_name: str = "Breakthru Beverage"

    invoice_number: str

    invoice_date: str

    line_items: list[BreakthruLineItem] = Field(
        default_factory=list
    )

    invoice_total: Optional[Decimal] = None
