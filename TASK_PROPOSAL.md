# Task 1: PDF Invoice Extractor & Summary Report

## Problem Statement

Build a command-line tool that reads a folder of PDF invoice files, extracts structured fields (invoice number, vendor, date, total, line items), validates the extracted data against business rules, and produces:

- A JSON summary report with aggregated totals by vendor
- An error log for PDFs that fail validation or parsing

The implementation must be driven by a YAML configuration file containing regex patterns, include automated tests, and use **VS Code** with **`pdfplumber`** / **`pypdf`** (approved tools). A **FastAPI** layer exposes upload, processing, summarization, and invoice inspection endpoints.

## Workflow Artifacts

1. **Configuration specification** — `config/extraction_rules.yaml` defines field patterns, line-item format, and validation tolerances.
2. **Sample dataset** — 6 PDF invoices in `data/samples/` (5 valid, 1 intentionally invalid).
3. **Starter expectation** — Implement parser, reporter, CLI, tests, and sample generator.

## Challenge Dimensions

- **Cross-source reasoning** — Parser behavior must align with YAML rules, PDF layout, and test expectations.
- **Validation logic** — Line-item totals must reconcile with the stated invoice total within tolerance.
- **Error isolation** — One bad PDF must not stop batch processing; errors are logged separately.

## Deliverables

| Deliverable | Location |
|-------------|----------|
| Source implementation | `src/` |
| Configuration | `config/extraction_rules.yaml` |
| Automated tests | `tests/test_parser.py` |
| Sample PDFs | `data/samples/` |
| JSON summary output | `output/summary.json` |
| Error log | `output/errors.log` |
| FastAPI service | `src/api.py`, `api_main.py` |
| API tests | `tests/test_api.py` |
| Setup & run instructions | `README.md` |

## Rubric (Self-Assessment)

| Weight | Criteria |
|--------|----------|
| 0.10 | Project installs and runs with documented commands |
| 0.20 | YAML rules correctly drive field extraction |
| 0.20 | Line items parsed and totals validated |
| 0.15 | Batch processing with isolated error handling |
| 0.15 | JSON summary and error log generated correctly |
| 0.20 | Automated tests pass |

## Implementation Summary (fill after completion)

_Architecture: config-driven regex parser using pdfplumber for text extraction, dataclass models for invoices, separate report module for JSON/log output. Key design choice: invalid invoices are collected without aborting the batch._
