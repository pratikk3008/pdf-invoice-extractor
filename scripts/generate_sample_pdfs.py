#!/usr/bin/env python3
"""Generate sample invoice PDFs for development and demo purposes."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

SAMPLES = [
    {
        "filename": "invoice_acme_001.pdf",
        "invoice_number": "INV-2024-001",
        "vendor": "Acme Supplies Ltd",
        "date": "2024-03-15",
        "line_items": [
            ("Notebook Pack", 5, 4.50, 22.50),
            ("Pen Set", 10, 2.25, 22.50),
        ],
        "total": 45.00,
    },
    {
        "filename": "invoice_globex_002.pdf",
        "invoice_number": "INV-2024-002",
        "vendor": "Globex Corporation",
        "date": "2024-04-02",
        "line_items": [
            ("USB Cable", 3, 12.00, 36.00),
            ("Monitor Stand", 1, 49.99, 49.99),
            ("Keyboard", 2, 35.00, 70.00),
        ],
        "total": 155.99,
    },
    {
        "filename": "invoice_initech_003.pdf",
        "invoice_number": "INV-2024-003",
        "vendor": "Initech Services",
        "date": "2024-05-20",
        "line_items": [
            ("Cloud Hosting", 1, 120.00, 120.00),
            ("Support Hours", 4, 75.00, 300.00),
        ],
        "total": 420.00,
    },
    {
        "filename": "invoice_umbrella_004.pdf",
        "invoice_number": "INV-2024-004",
        "vendor": "Umbrella Analytics",
        "date": "2024-06-11",
        "line_items": [
            ("Data Pipeline", 1, 890.00, 890.00),
        ],
        "total": 890.00,
    },
    {
        "filename": "invoice_stark_005.pdf",
        "invoice_number": "INV-2024-005",
        "vendor": "Stark Industries",
        "date": "2024-07-08",
        "line_items": [
            ("Sensor Module", 6, 45.50, 273.00),
            ("Calibration Kit", 2, 88.00, 176.00),
        ],
        "total": 449.00,
    },
    # Intentionally invalid: total does not match line items (for error-log demo)
    {
        "filename": "invoice_bad_total.pdf",
        "invoice_number": "INV-2024-BAD",
        "vendor": "Broken Books Inc",
        "date": "2024-08-01",
        "line_items": [
            ("Mispriced Item", 1, 10.00, 10.00),
        ],
        "total": 99.99,
    },
]


def render_invoice(data: dict) -> FPDF:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    pdf.cell(0, 10, "INVOICE", ln=True)
    pdf.ln(4)
    pdf.cell(0, 8, f"Invoice Number: {data['invoice_number']}", ln=True)
    pdf.cell(0, 8, f"Vendor: {data['vendor']}", ln=True)
    pdf.cell(0, 8, f"Date: {data['date']}", ln=True)
    pdf.ln(8)

    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(70, 8, "Description", border=1)
    pdf.cell(25, 8, "Qty", border=1)
    pdf.cell(35, 8, "Unit Price", border=1)
    pdf.cell(35, 8, "Line Total", border=1, ln=True)

    pdf.set_font("Helvetica", size=11)
    for description, qty, unit_price, line_total in data["line_items"]:
        pdf.cell(70, 8, description, border=1)
        pdf.cell(25, 8, str(qty), border=1)
        pdf.cell(35, 8, f"{unit_price:.2f}", border=1)
        pdf.cell(35, 8, f"{line_total:.2f}", border=1, ln=True)

    pdf.ln(6)
    pdf.cell(0, 8, f"Total: ${data['total']:.2f}", ln=True)
    return pdf


def main() -> None:
    output_dir = Path(__file__).resolve().parents[1] / "data" / "samples"
    output_dir.mkdir(parents=True, exist_ok=True)

    for sample in SAMPLES:
        pdf = render_invoice(sample)
        target = output_dir / sample["filename"]
        pdf.output(str(target))
        print(f"Created {target.name}")


if __name__ == "__main__":
    main()
