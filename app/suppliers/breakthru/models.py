
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class BreakthruLineItem(BaseModel):
    """One printed product line from a Breakthru invoice."""

    item_number: Optional[str] = Field(
        default=None,
        description="Supplier item number printed in the Pieces column.",
    )

    upc_or_barcode: Optional[str] = Field(
        default=None,
        description="Product UPC or barcode printed in the Item column.",
    )

    product_name: str = Field(
        description="Product description printed on the invoice.",
    )

    item_size: Optional[str] = Field(
        default=None,
        description="Printed product size, such as 375ML or 750ML.",
    )

    bottles_per_case: Optional[int] = Field(
        default=None,
        description="BPC value printed on the invoice.",
    )

    case_quantity: Optional[Decimal] = Field(
        default=None,
        description="Printed Cases quantity only. Ignore all handwritten marks.",
    )

    bottle_quantity: Optional[int] = Field(
        default=None,
        description="Printed Btls quantity. This is the received bottle quantity.",
    )

    unit_price: Optional[Decimal] = Field(
        default=None,
        description="Original printed Unit Price.",
    )

    unit_discount: Optional[Decimal] = Field(
        default=None,
        description="Printed Unit Disc.",
    )

    net_unit_price: Optional[Decimal] = Field(
        default=None,
        description="Printed Unit Price Net.",
    )

    net_bottle_price: Optional[Decimal] = Field(
        default=None,
        description="Printed Net Btl price.",
    )

    net_sales: Optional[Decimal] = Field(
        default=None,
        description="Printed Net Sales amount.",
    )


class BreakthruInvoice(BaseModel):
    """Structured invoice data for Breakthru Beverage."""

    vendor_name: str = "Breakthru Beverage"

    invoice_number: Optional[str] = None

    invoice_date: Optional[str] = None

    line_items: list[BreakthruLineItem] = Field(
        default_factory=list
    )

    invoice_total: Optional[Decimal] = None
