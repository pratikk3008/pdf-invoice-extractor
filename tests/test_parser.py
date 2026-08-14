from __future__ import annotations

from pathlib import Path

import pytest

from src.models import ExtractionResult, Invoice, LineItem
from src.parser import InvoiceParser
from src.report import build_summary


RULES_PATH = Path(__file__).resolve().parents[1] / "config" / "extraction_rules.yaml"
SAMPLES_DIR = Path(__file__).resolve().parents[1] / "data" / "samples"


@pytest.fixture
def parser() -> InvoiceParser:
    return InvoiceParser(RULES_PATH)


def test_parse_valid_invoice(parser: InvoiceParser) -> None:
    invoice = parser.parse_file(SAMPLES_DIR / "invoice_acme_001.pdf")

    assert invoice.invoice_number == "INV-2024-001"
    assert invoice.vendor == "Acme Supplies Ltd"
    assert invoice.date == "2024-03-15"
    assert invoice.total == 45.00
    assert len(invoice.line_items) == 2
    assert invoice.computed_total == invoice.total


def test_parse_multiple_line_items(parser: InvoiceParser) -> None:
    invoice = parser.parse_file(SAMPLES_DIR / "invoice_globex_002.pdf")

    assert len(invoice.line_items) == 3
    assert invoice.line_items[0].description == "USB Cable"
    assert invoice.line_items[0].quantity == 3


def test_invalid_total_raises(parser: InvoiceParser) -> None:
    with pytest.raises(ValueError, match="Total mismatch"):
        parser.parse_file(SAMPLES_DIR / "invoice_bad_total.pdf")


def test_parse_directory_collects_errors(parser: InvoiceParser) -> None:
    result = parser.parse_directory(SAMPLES_DIR)

    assert len(result.invoices) == 5
    assert len(result.errors) == 1
    assert result.errors[0].source_file == "invoice_bad_total.pdf"


def test_summary_report_totals() -> None:
    result = ExtractionResult(
        invoices=[
            Invoice(
                source_file="a.pdf",
                invoice_number="INV-1",
                vendor="Acme Supplies Ltd",
                date="2024-01-01",
                total=100.0,
                line_items=[LineItem("Item", 1, 100.0, 100.0)],
            ),
            Invoice(
                source_file="b.pdf",
                invoice_number="INV-2",
                vendor="Globex Corporation",
                date="2024-02-01",
                total=50.0,
                line_items=[LineItem("Item", 1, 50.0, 50.0)],
            ),
        ]
    )

    summary = build_summary(result)

    assert summary.success_count == 2
    assert summary.total_amount == 150.0
    assert summary.vendors["Acme Supplies Ltd"] == 100.0
    assert summary.vendors["Globex Corporation"] == 50.0


def test_vendor_whitespace_normalized(parser: InvoiceParser) -> None:
    invoice = parser.parse_file(SAMPLES_DIR / "invoice_acme_001.pdf")
    assert "  " not in invoice.vendor
