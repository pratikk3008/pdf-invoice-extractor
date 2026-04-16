from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path

from .models import ExtractionResult, SummaryReport

logger = logging.getLogger(__name__)


def build_summary(result: ExtractionResult) -> SummaryReport:
    vendor_totals: dict[str, float] = defaultdict(float)
    invoice_rows: list[dict] = []

    for invoice in result.invoices:
        vendor_totals[invoice.vendor] += invoice.total
        invoice_rows.append(
            {
                "source_file": invoice.source_file,
                "invoice_number": invoice.invoice_number,
                "vendor": invoice.vendor,
                "date": invoice.date,
                "total": invoice.total,
                "line_item_count": len(invoice.line_items),
            }
        )

    processed = len(result.invoices) + len(result.errors)
    total_amount = sum(invoice.total for invoice in result.invoices)

    return SummaryReport(
        processed_count=processed,
        success_count=len(result.invoices),
        error_count=len(result.errors),
        total_amount=total_amount,
        vendors=dict(vendor_totals),
        invoices=invoice_rows,
    )


def write_summary(report: SummaryReport, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report.to_dict(), handle, indent=2)
    logger.info("Wrote summary report to %s", output_path)


def write_errors(result: ExtractionResult, log_path: str | Path) -> None:
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    error_logger = logging.getLogger("invoice_errors")
    error_logger.setLevel(logging.ERROR)
    error_logger.handlers.clear()
    error_logger.addHandler(file_handler)
    error_logger.propagate = False

    if not result.errors:
        error_logger.error("No parsing errors encountered.")
    else:
        for error in result.errors:
            error_logger.error("%s | %s", error.source_file, error.message)

    file_handler.close()
    logger.info("Wrote error log to %s", log_path)


def write_summary_csv(report: SummaryReport, output_path: str | Path) -> None:
    import csv

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["source_file", "invoice_number", "vendor", "date", "total", "line_item_count"],
        )
        writer.writeheader()
        for row in report.invoices:
            writer.writerow({key: row[key] for key in writer.fieldnames})
    logger.info("Wrote CSV summary to %s", output_path)


def write_metrics(report: SummaryReport, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics = {
        "processed_count": report.processed_count,
        "success_count": report.success_count,
        "error_count": report.error_count,
        "total_amount": report.total_amount,
        "vendor_count": len(report.vendors),
    }
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
    logger.info("Wrote metrics report to %s", output_path)
