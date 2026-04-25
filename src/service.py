from __future__ import annotations

import json
from pathlib import Path

import yaml

from .models import ExtractionResult, Invoice, ParseError
from .parser import InvoiceParser
from .report import build_summary, write_errors, write_summary


class InvoiceExtractionService:
    """Coordinates parsing, in-memory state, uploads, and report generation."""

    def __init__(
        self,
        rules_path: Path,
        samples_dir: Path,
        upload_dir: Path,
        output_dir: Path,
    ) -> None:
        self.rules_path = rules_path
        self.samples_dir = samples_dir
        self.upload_dir = upload_dir
        self.output_dir = output_dir
        self.parser = InvoiceParser(rules_path)

        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.result = ExtractionResult()
        self.summary = build_summary(self.result)

    def reset(self) -> None:
        self.result = ExtractionResult()
        self.summary = build_summary(self.result)

    def load_rules(self) -> dict:
        with open(self.rules_path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def load_samples(self, directory: Path | None = None) -> ExtractionResult:
        target = directory or self.samples_dir
        if not target.exists():
            raise FileNotFoundError(f"Sample directory not found: {target}")

        self.result = self.parser.parse_directory(target)
        self._refresh_summary()
        self._persist_outputs()
        return self.result

    def save_upload(self, filename: str, content: bytes) -> Path:
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported")

        destination = self.upload_dir / Path(filename).name
        destination.write_bytes(content)
        return destination

    def list_uploads(self) -> list[str]:
        return sorted(path.name for path in self.upload_dir.glob("*.pdf"))

    def process_uploads(self) -> ExtractionResult:
        if not any(self.upload_dir.glob("*.pdf")):
            raise FileNotFoundError("No uploaded PDF files found to process")

        upload_result = self.parser.parse_directory(self.upload_dir)
        self._merge_result(upload_result)
        self._refresh_summary()
        self._persist_outputs()
        return self.result

    def process_file(self, filename: str) -> Invoice:
        path = self._resolve_pdf_path(filename)
        invoice = self.parser.parse_file(path)
        self._upsert_invoice(invoice)
        self._refresh_summary()
        self._persist_outputs()
        return invoice

    def get_invoice(self, invoice_number: str) -> Invoice:
        for invoice in self.result.invoices:
            if invoice.invoice_number == invoice_number:
                return invoice
        raise KeyError(invoice_number)

    def get_errors(self) -> list[ParseError]:
        return list(self.result.errors)

    def get_summary_dict(self) -> dict:
        return self.summary.to_dict()

    def _resolve_pdf_path(self, filename: str) -> Path:
        safe_name = Path(filename).name
        upload_path = self.upload_dir / safe_name
        if upload_path.exists():
            return upload_path

        sample_path = self.samples_dir / safe_name
        if sample_path.exists():
            return sample_path

        raise FileNotFoundError(f"PDF not found: {safe_name}")

    def _merge_result(self, incoming: ExtractionResult) -> None:
        for invoice in incoming.invoices:
            self._upsert_invoice(invoice)
        for error in incoming.errors:
            self._upsert_error(error)

    def _upsert_invoice(self, invoice: Invoice) -> None:
        self.result.invoices = [
            existing
            for existing in self.result.invoices
            if existing.source_file != invoice.source_file
        ]
        self.result.invoices.append(invoice)
        self.result.errors = [
            error for error in self.result.errors if error.source_file != invoice.source_file
        ]

    def _upsert_error(self, error: ParseError) -> None:
        self.result.invoices = [
            invoice for invoice in self.result.invoices if invoice.source_file != error.source_file
        ]
        self.result.errors = [
            existing for existing in self.result.errors if existing.source_file != error.source_file
        ]
        self.result.errors.append(error)

    def _refresh_summary(self) -> None:
        self.summary = build_summary(self.result)

    def _persist_outputs(self) -> None:
        write_summary(self.summary, self.output_dir / "summary.json")
        write_errors(self.result, self.output_dir / "errors.log")

        metrics = {
            "processed_count": self.summary.processed_count,
            "success_count": self.summary.success_count,
            "error_count": self.summary.error_count,
            "total_amount": self.summary.total_amount,
            "vendor_count": len(self.summary.vendors),
        }
        with open(self.output_dir / "metrics.json", "w", encoding="utf-8") as handle:
            json.dump(metrics, handle, indent=2)
