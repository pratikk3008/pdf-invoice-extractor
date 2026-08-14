from __future__ import annotations

import logging
import re
from pathlib import Path

import pdfplumber
import yaml

from .models import ExtractionResult, Invoice, LineItem, ParseError

logger = logging.getLogger(__name__)


class InvoiceParser:
    """Extract structured invoice data from PDF files using configurable regex rules."""

    def __init__(self, rules_path: str | Path) -> None:
        with open(rules_path, encoding="utf-8") as handle:
            self.rules = yaml.safe_load(handle)

    def parse_directory(self, directory: str | Path) -> ExtractionResult:
        directory = Path(directory)
        result = ExtractionResult()

        pdf_files = sorted(directory.glob("*.pdf"))
        if not pdf_files:
            logger.warning("No PDF files found in %s", directory)

        for pdf_path in pdf_files:
            try:
                invoice = self.parse_file(pdf_path)
                result.invoices.append(invoice)
                logger.info("Parsed invoice %s from %s", invoice.invoice_number, pdf_path.name)
            except ValueError as exc:
                error = ParseError(source_file=pdf_path.name, message=str(exc))
                result.errors.append(error)
                logger.error("Failed to parse %s: %s", pdf_path.name, exc)

        return result

    def parse_file(self, pdf_path: str | Path) -> Invoice:
        pdf_path = Path(pdf_path)
        text = self._extract_text(pdf_path)
        if not text.strip():
            raise ValueError("PDF contains no extractable text")

        invoice_number = self._extract_field(text, "invoice_number")
        vendor = self._extract_field(text, "vendor")
        date = self._extract_field(text, "date")
        total = float(self._extract_field(text, "total").replace(",", ""))
        line_items = self._extract_line_items(text)

        self._validate(invoice_number, vendor, date, total, line_items)

        return Invoice(
            source_file=pdf_path.name,
            invoice_number=invoice_number,
            vendor=" ".join(vendor.split()),
            date=date,
            total=total,
            line_items=line_items,
        )

    def _extract_text(self, pdf_path: Path) -> str:
        pages: list[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text)
        return "\n".join(pages)

    def _extract_field(self, text: str, field_name: str) -> str:
        field_rules = self.rules["fields"][field_name]
        pattern = field_rules["pattern"]
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if not match:
            if field_rules.get("required", False):
                raise ValueError(f"Missing required field: {field_name}")
            return ""
        return match.group(1).strip()

    def _extract_line_items(self, text: str) -> list[LineItem]:
        pattern = self.rules["line_items"]["pattern"]
        items: list[LineItem] = []

        for line in text.splitlines():
            match = re.match(pattern, line.strip())
            if not match:
                continue
            description, quantity, unit_price, line_total = match.groups()
            items.append(
                LineItem(
                    description=description.strip(),
                    quantity=int(quantity),
                    unit_price=float(unit_price.replace(",", "")),
                    line_total=float(line_total.replace(",", "")),
                )
            )

        min_items = self.rules["validation"]["min_line_items"]
        if len(items) < min_items:
            raise ValueError(f"Expected at least {min_items} line item(s)")

        return items

    def _validate(
        self,
        invoice_number: str,
        vendor: str,
        date: str,
        total: float,
        line_items: list[LineItem],
    ) -> None:
        if not invoice_number:
            raise ValueError("Invoice number is empty")
        if not vendor:
            raise ValueError("Vendor is empty")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            raise ValueError(f"Invalid date format: {date}")

        computed = round(sum(item.line_total for item in line_items), 2)
        tolerance = float(self.rules["validation"]["max_total_deviation"])
        if abs(computed - total) > tolerance:
            raise ValueError(
                f"Total mismatch: stated {total:.2f}, computed {computed:.2f}"
            )
