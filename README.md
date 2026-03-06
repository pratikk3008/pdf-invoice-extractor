# PDF Invoice Extractor

Extract structured data from PDF invoices and produce a JSON summary report plus an error log.

**Tools:** VS Code, Python, `pdfplumber`, `pypdf`

## Setup

```bash
python -m venv .venv
pip install -r requirements.txt
python scripts/generate_sample_pdfs.py
```

## Run

```bash
python main.py --verbose
```

## Test

```bash
pytest -v
```
