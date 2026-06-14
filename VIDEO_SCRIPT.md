# Video Script — PDF Invoice Extractor Demo

**Target length:** 75–90 minutes  
**Tools to mention:** VS Code, Python, pdfplumber, pypdf  
**Tone:** Calm, technical, explain *why* not just *what*

---

## SEGMENT 1 — Introduction (5 min)

**[Show: VS Code with project folder open]**

> "Hi, I'm [your name]. In this recording I'll complete a software engineering task: building a **config-driven PDF invoice extractor**.
>
> The goal is to batch-process PDF invoices, extract structured fields like vendor, date, total, and line items, validate the data, and produce a JSON summary report plus an error log.
>
> I'm using **VS Code**, **Python**, and **pdfplumber** — which is one of the approved tools for this project.
>
> Let me start by showing the task proposal."

**[Open: TASK_PROPOSAL.md — scroll slowly]**

> "The task has four main parts: a YAML configuration for extraction rules, a sample dataset of PDF invoices, the parser implementation, and automated tests.
>
> The challenge is **cross-source reasoning** — the parser must align with the YAML rules, the PDF layout, and what the tests expect. It also needs **error isolation** — one bad PDF must not crash the entire batch."

---

## SEGMENT 2 — Project Structure (5 min)

**[Show: Explorer sidebar — expand folders]**

> "Here's how the project is organized.
>
> `config/extraction_rules.yaml` holds all regex patterns — so we can change extraction logic without touching Python code.
>
> `data/samples/` contains our PDF invoices — five valid ones and one intentionally broken file for testing error handling.
>
> `src/` has the core logic split into parser, models, report, and CLI modules.
>
> `tests/` has automated pytest tests.
>
> `scripts/generate_sample_pdfs.py` creates the sample invoices programmatically.
>
> This separation keeps parsing, data models, and reporting independent — which makes the code easier to test and extend."

---

## SEGMENT 3 — Environment Setup (10 min)

**[Show: Terminal — already in .venv]**

> "I've opened the project in VS Code and activated a Python virtual environment. You can see `(.venv)` in the prompt.
>
> First I'll install dependencies."

**[Run: `pip install -r requirements.txt`]**

> "The main libraries are **pdfplumber** for text extraction from PDFs, **PyYAML** for loading config rules, **fpdf2** for generating sample invoices, and **pytest** for testing.
>
> Everything installed successfully — all requirements already satisfied means we ran this before and the environment is ready."

**[Run: `python scripts/generate_sample_pdfs.py`]**

> "This script generates six sample invoice PDFs. We have five valid invoices from different vendors, and one invalid invoice where the total doesn't match the line items — that's deliberate, to demonstrate error handling.
>
> You might see deprecation warnings from fpdf2 — those are harmless and don't affect our output."

**[Open one PDF from data/samples/ — e.g. invoice_acme_001.pdf]**

> "Each invoice follows a consistent text layout: invoice number, vendor, date, a line-item table, and a total. The parser relies on this structure plus our regex rules in the YAML file."

---

## SEGMENT 4 — Configuration Design (10 min)

**[Open: config/extraction_rules.yaml]**

> "This YAML file is the **single source of truth** for extraction behavior.
>
> Under `fields`, each field has a regex pattern. For example, invoice number uses a pattern that matches 'Invoice Number: INV-2024-001' but avoids false matches on the word 'Number' alone.
>
> Vendor and date have their own patterns. The total pattern handles optional dollar signs and comma separators.
>
> Under `line_items`, we define how table rows are parsed — description, quantity, unit price, and line total.
>
> Under `validation`, we set business rules: at least one line item required, and the stated total must match the sum of line items within a five-cent tolerance.
>
> **Why config-driven?** If a client changes their invoice format, we update YAML — not Python. That's a production-style design decision."

---

## SEGMENT 5 — Parser Implementation (20 min)

**[Open: src/parser.py]**

> "The `InvoiceParser` class loads rules from YAML in `__init__`, then exposes `parse_directory` for batch processing and `parse_file` for a single PDF."

**[Scroll to parse_directory, lines 22–40]**

> "`parse_directory` finds all PDFs, loops through them, and wraps each parse in try/except. If one file fails, we append a ParseError and **continue** — we never abort the batch. That's the error isolation requirement."

**[Scroll to parse_file, lines 42–63]**

> "`parse_file` orchestrates the pipeline: extract text, extract fields, extract line items, validate, return an Invoice object."

**[Scroll to _extract_text, lines 65–71]**

> "`_extract_text` uses pdfplumber to open the PDF and concatenate text from every page. pdfplumber handles layout-aware extraction better than raw byte reading."

**[Scroll to _extract_field, lines 73–81]**

> "`_extract_field` looks up the regex from YAML by field name and runs re.search. If a required field is missing, it raises ValueError — which gets caught at the directory level."

**[Scroll to _extract_line_items, lines 83–105]**

> "Line items are parsed line-by-line. Non-matching lines are skipped — so headers like 'Description Qty Unit Price' don't become false line items. We also enforce minimum line item count from config."

**[Scroll to _validate, lines 107–127]**

> "Validation is where business logic lives. We check invoice number and vendor aren't empty, date matches YYYY-MM-DD format, and critically — **computed total from line items must match the stated total** within tolerance.
>
> This is what catches our bad sample invoice — stated 99.99 but line items only add up to 10.00."

**[Open: src/models.py briefly]**

> "Data classes — Invoice, LineItem, ParseError, ExtractionResult — keep the structure explicit and type-safe."

**[Open: src/report.py briefly]**

> "The report module builds a SummaryReport with vendor totals and writes JSON plus the error log. Parsing and reporting stay decoupled."

---

## SEGMENT 6 — Run the CLI (10 min)

**[Run: `python main.py --verbose`]**

> "Running the main CLI with verbose logging. Watch the output — each successful parse logs the invoice number and filename."

**[Point at terminal output]**

> "Five invoices parsed successfully. One failed — invoice_bad_total.pdf — with a total mismatch error. Final line: 5 success, 1 error, total amount 1959 dollars and 99 cents.
>
> Exit code 2 indicates partial success — some files had errors but the run completed."

**[Open: output/summary.json]**

> "The JSON summary has processed count, success and error counts, total amount, vendor breakdown, and per-invoice details. Five vendors, five invoices — Acme, Globex, Initech, Stark, and Umbrella."

**[Open: output/errors.log]**

> "The error log captures the failed file with timestamp and reason: total mismatch, stated 99.99, computed 10.00. This is exactly the behavior we designed — isolated failure, clear audit trail."

---

## SEGMENT 7 — Automated Tests (15 min)

**[Run: `pytest -v`]**

> "Now the test suite. Five tests, all should pass."

**[Open: tests/test_parser.py while tests run or after]**

> "`test_parse_valid_invoice` — checks we extract invoice number, vendor, date, total, and line items correctly from a known good PDF.
>
> `test_parse_multiple_line_items` — verifies invoices with three line items parse all rows.
>
> `test_invalid_total_raises` — confirms the bad invoice raises ValueError with 'Total mismatch'.
>
> `test_parse_directory_collects_errors` — batch of six files yields five successes and one error — doesn't stop on failure.
>
> `test_summary_report_totals` — unit test for vendor aggregation math.
>
> All five passed in about one second. The tests validate parsing, validation, batch behavior, and reporting independently."

---

## SEGMENT 8 — Closing Summary (5 min)

**[Show: summary.json or project root]**

> "To summarize what I built:
>
> One — a **config-driven PDF invoice extractor** using pdfplumber and YAML regex rules.
>
> Two — **validation logic** that reconciles line-item totals with the stated invoice total.
>
> Three — **batch error isolation** — bad PDFs are logged, good ones still process.
>
> Four — **structured outputs** — JSON summary for downstream use, error log for auditing.
>
> Five — a **pytest suite** covering parsing, validation, batch processing, and reporting.
>
> The architecture separates config, parsing, models, and reporting — so each layer can evolve independently. That's the key design decision.
>
> Thank you for watching."

**[Stop recording]**

---

## Quick Reference — Commands to Run on Camera

```powershell
pip install -r requirements.txt
python scripts/generate_sample_pdfs.py
python main.py --verbose
pytest -v
```

## Expected Final Numbers

- 5 invoices parsed
- 1 error (invoice_bad_total.pdf)
- Total: $1,959.99
- 5/5 tests passed
