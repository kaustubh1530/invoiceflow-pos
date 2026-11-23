
from pathlib import Path
import shutil

from app.parser import extract_invoice_text
from app.supplier_detection import detect_supplier, SUPPLIERS


BASE_DIR = Path(__file__).resolve().parent.parent
INCOMING_DIR = BASE_DIR / "invoices" / "incoming"


def get_destination_folder(supplier_id: str) -> Path:
    """Get the incoming folder for a supplier."""
    return INCOMING_DIR / supplier_id


def avoid_overwriting(destination: Path) -> Path:
    """Prevent an existing invoice from being overwritten."""

    if not destination.exists():
        return destination

    counter = 1

    while True:
        new_destination = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )

        if not new_destination.exists():
            return new_destination

        counter += 1


def route_invoice_file(file_path: str, supplier_id: str) -> dict:
    """Copy an invoice into the selected supplier's incoming folder."""

    source = Path(file_path)

    if not source.exists():
        raise FileNotFoundError(f"Invoice not found: {source}")

    valid_suppliers = list(SUPPLIERS.keys()) + ["other"]

    if supplier_id not in valid_suppliers:
        raise ValueError(f"Invalid supplier: {supplier_id}")

    destination_folder = get_destination_folder(supplier_id)
    destination_folder.mkdir(parents=True, exist_ok=True)

    destination = avoid_overwriting(
        destination_folder / source.name
    )

    shutil.copy2(source, destination)

    return {
        "source_file": str(source.resolve()),
        "supplier": supplier_id,
        "status": "routed",
        "destination": str(destination.resolve()),
    }


def process_invoice_file(file_path: str) -> dict:
    """
    Extract invoice text and attempt automatic supplier detection.

    If the supplier is unknown, request manual selection
    instead of guessing.
    """

    source = Path(file_path)

    if not source.exists():
        raise FileNotFoundError(f"Invoice not found: {source}")

    # Step 1: Extract invoice text
    invoice_text = extract_invoice_text(str(source))

    # Step 2: Detect supplier
    supplier_id = detect_supplier(invoice_text)

    # Step 3: Route automatically if recognized
    if supplier_id:
        print(f"\n✓ Supplier detected: {supplier_id}")
        return route_invoice_file(str(source), supplier_id)

    # Step 4: Ask for manual selection if unknown
    print("\n⚠ Supplier could not be identified automatically.")

    return {
        "source_file": str(source.resolve()),
        "supplier": None,
        "status": "needs_manual_selection",
        "destination": None,
    }


def main():
    """Run invoice processing with manual supplier fallback."""

    test_file = BASE_DIR / "uploads" / "sample_inv2.jpg"

    print("\n" + "=" * 50)
    print("InvoiceFlow-POS — Invoice Routing")
    print("=" * 50)

    # Attempt automatic detection
    result = process_invoice_file(str(test_file))

    # Ask for supplier only if automatic detection failed
    if result["status"] == "needs_manual_selection":

        supplier_options = list(SUPPLIERS.keys()) + ["other"]

        print("\nSelect the invoice supplier:")

        for index, supplier in enumerate(supplier_options, start=1):
            print(f"{index}. {supplier}")

        while True:
            choice = input("\nEnter supplier number: ").strip()

            if choice.isdigit():
                selected_index = int(choice) - 1

                if 0 <= selected_index < len(supplier_options):
                    selected_supplier = supplier_options[selected_index]
                    break

            print("Invalid selection. Please enter a valid number.")

        # Route using the manually selected supplier
        result = route_invoice_file(
            str(test_file),
            selected_supplier
        )

    # Display final result
    print("\nINVOICE ROUTING RESULT")
    print("=" * 50)

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
