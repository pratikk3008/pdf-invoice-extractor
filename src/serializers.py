from __future__ import annotations

from src.models import ExtractionResult, Invoice, LineItem, ParseError, SummaryReport


def line_item_to_dict(item: LineItem) -> dict:
    return {
        "description": item.description,
        "quantity": item.quantity,
        "unit_price": item.unit_price,
        "line_total": item.line_total,
    }


def invoice_to_dict(invoice: Invoice, *, include_line_items: bool = False) -> dict:
    payload = {
        "source_file": invoice.source_file,
        "invoice_number": invoice.invoice_number,
        "vendor": invoice.vendor,
        "date": invoice.date,
        "total": invoice.total,
        "computed_total": invoice.computed_total,
        "line_item_count": len(invoice.line_items),
    }
    if include_line_items:
        payload["line_items"] = [line_item_to_dict(item) for item in invoice.line_items]
    return payload


def parse_error_to_dict(error: ParseError) -> dict:
    return {
        "source_file": error.source_file,
        "message": error.message,
    }


def extraction_result_to_dict(result: ExtractionResult) -> dict:
    return {
        "invoices": [invoice_to_dict(invoice) for invoice in result.invoices],
        "errors": [parse_error_to_dict(error) for error in result.errors],
    }
