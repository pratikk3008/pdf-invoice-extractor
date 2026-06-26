# PDF Invoice Extractor

A config-driven PDF invoice extraction system built with **Python**, **pdfplumber**, and **FastAPI**. Batch-process invoice PDFs, validate extracted data, and produce structured JSON summaries with isolated error handling.

**Repository:** [github.com/pratikk3008/pdf-invoice-extractor](https://github.com/pratikk3008/pdf-invoice-extractor)


---

## Overview

This project reads PDF invoice files and extracts structured fields:

- Invoice number, vendor, date, total amount
- Line items (description, quantity, unit price, line total)

It validates that line-item totals reconcile with the stated invoice total, logs failures without stopping the batch, and exposes results through both a **CLI** and a **REST API**.

### Key features

- **YAML-driven extraction** — regex rules live in config, not hard-coded in Python
- **Batch error isolation** — one invalid PDF does not abort processing
- **Dual interface** — command-line tool and FastAPI web API
- **Automated tests** — 20 tests covering parser logic and all API endpoints
- **Structured outputs** — JSON summary, error log, and runtime metrics

---

## Tech stack

| Category | Tools |
|----------|-------|
| Language | Python 3.11+ |
| PDF extraction | pdfplumber, pypdf |
| Web API | FastAPI, Uvicorn |
| Config | PyYAML |
| Testing | pytest, httpx |
| IDE | VS Code |

---

## Quick start

### 1. Clone and set up

```bash
git clone https://github.com/pratikk3008/pdf-invoice-extractor.git
cd pdf-invoice-extractor
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_sample_pdfs.py
```

**macOS / Linux:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_sample_pdfs.py
```

### 2. Run the CLI

```bash
python main.py --verbose
```

### 3. Run the API server

```bash
python api_main.py
```

Open **http://127.0.0.1:8000/docs** for interactive API documentation.

---

## CLI usage

```bash
python main.py [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--input-dir` | `data/samples` | Folder containing PDF invoices |
| `--rules` | `config/extraction_rules.yaml` | Extraction regex rules |
| `--output` | `output/summary.json` | JSON summary output path |
| `--error-log` | `output/errors.log` | Error log output path |
| `--verbose` | off | Enable debug logging |

**Example:**

```bash
python main.py --input-dir data/samples --output output/summary.json --error-log output/errors.log --verbose
```

---

## API usage

### Start the server

```bash
python api_main.py
```

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000 | Redirects to API docs |
| http://127.0.0.1:8000/docs | Swagger UI |
| http://127.0.0.1:8000/health | Health check |

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| DELETE | `/reset` | Clear in-memory state |
| GET | `/config/rules` | Load YAML extraction rules |
| POST | `/load/samples` | Process bundled sample PDFs |
| POST | `/upload` | Upload multiple PDF files |
| POST | `/upload/single` | Upload one PDF (Swagger-friendly) |
| GET | `/uploads` | List uploaded filenames |
| POST | `/process` | Process all uploaded PDFs |
| POST | `/process/{filename}` | Process a single PDF |
| GET | `/invoices` | List parsed invoices |
| GET | `/invoices/{invoice_number}` | Invoice detail with line items |
| GET | `/summary` | Aggregated summary report |
| GET | `/errors` | Parsing and validation errors |

### Example workflow

```bash
# Health check
curl http://127.0.0.1:8000/health

# Load and process sample invoices
curl -X POST http://127.0.0.1:8000/load/samples \
  -H "Content-Type: application/json" \
  -d "{}"

# View summary
curl http://127.0.0.1:8000/summary

# Get invoice detail
curl http://127.0.0.1:8000/invoices/INV-2024-001

# Upload a PDF
curl -X POST http://127.0.0.1:8000/upload/single \
  -F "file=@data/samples/invoice_globex_002.pdf"

# Process uploaded file
curl -X POST http://127.0.0.1:8000/process/invoice_globex_002.pdf
```

---

## Testing

Run the full test suite:

```bash
pytest -v
```

Run only API tests:

```bash
pytest tests/test_api.py -v
```

Run only parser tests:

```bash
pytest tests/test_parser.py -v
```

**Expected:** 20 tests passing (15 API + 5 parser).

---

## Sample output

After processing the bundled samples:

| Metric | Value |
|--------|-------|
| Invoices processed | 6 |
| Successful | 5 |
| Errors | 1 |
| Total amount | $1,959.99 |

The invalid invoice (`invoice_bad_total.pdf`) fails with:

```
Total mismatch: stated 99.99, computed 10.00
```

Generated files:

- `output/summary.json` — aggregated invoice and vendor totals
- `output/errors.log` — parsing failures with timestamps
- `output/metrics.json` — runtime processing statistics


---

## Project structure

```
pdf-invoice-extractor/
├── api_main.py                    # FastAPI server entry point
├── main.py                        # CLI entry point
├── requirements.txt
├── pytest.ini
├── config/
│   └── extraction_rules.yaml      # Regex patterns and validation rules
├── data/
│   ├── samples/                   # Sample invoice PDFs
│   └── uploads/                   # PDFs uploaded via API
├── output/                        # Generated reports (gitignored)
├── scripts/
│   └── generate_sample_pdfs.py    # Creates sample PDF dataset
├── src/
│   ├── api.py                     # FastAPI routes
│   ├── cli.py                     # CLI logic
│   ├── models.py                  # Domain dataclasses
│   ├── parser.py                  # PDF extraction and validation
│   ├── report.py                  # Summary and error log writers
│   ├── schemas.py                 # API response models
│   ├── serializers.py             # Domain-to-API mapping
│   └── service.py                 # Business logic layer
└── tests/
    ├── test_api.py                # API endpoint tests
    └── test_parser.py             # Parser unit tests
```

---

## Architecture

```
PDF files
   │
   ▼
InvoiceParser  ◄── config/extraction_rules.yaml
   │
   ├──► ExtractionResult (invoices + errors)
   │
   ▼
ReportBuilder ──► summary.json / errors.log / metrics.json
   │
   ▼
FastAPI Service ──► REST endpoints (/invoices, /summary, /errors, ...)
```

**Design decisions:**

1. **Config-driven parsing** — field patterns and validation rules are defined in YAML
2. **Layered architecture** — parser, service, and API are separate modules
3. **Fail-safe batching** — invalid files are logged and skipped, not fatal
4. **Shared core** — CLI and API use the same parser and service logic

---

## Configuration

Extraction behavior is controlled by `config/extraction_rules.yaml`:

```yaml
fields:
  invoice_number:
    pattern: "Invoice\\s+(?:Number|No\\.?|#)\\s*:\\s*([A-Z0-9-]+)"
    required: true
  vendor:
    pattern: "Vendor\\s*:?\\s*(.+)"
    required: true

validation:
  min_line_items: 1
  max_total_deviation: 0.05
```

To support a new invoice layout, update the YAML patterns — no parser code changes required.

---

## Author

**Pratik Shirsath** — [@pratikk3008](https://github.com/pratikk3008)

Built as a software engineering task for **Codefeast** — config-driven PDF processing with VS Code, pdfplumber, and FastAPI.
