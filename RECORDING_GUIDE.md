# Screen Recording Guide (~1.5–2 hours)

Use this outline while recording in VS Code. Speak naturally — explain *why*, not just *what*.

---

## Before You Record

- [ ] Install OBS Studio or use Windows Game Bar (`Win + G`)
- [ ] Close unrelated apps/notifications
- [ ] Open VS Code with `pdf-invoice-extractor` folder
- [ ] Terminal ready at project root

---

## Segment 1: Intro & Task Overview (5 min)

**Say something like:**

> "Today I'm completing a software engineering task: building a PDF invoice extractor using Python, pdfplumber, and configurable YAML rules. The goal is to batch-process PDF invoices, validate them, and output a JSON summary plus an error log."

- Show `TASK_PROPOSAL.md` briefly
- Walk through folder structure in VS Code explorer

---

## Segment 2: Environment Setup (10 min)

```powershell
cd c:\Users\acer\Codefeast\pdf-invoice-extractor
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Explain:** why a virtual environment, why pdfplumber for text extraction.

Generate sample PDFs:

```powershell
python scripts/generate_sample_pdfs.py
```

- Open one PDF from `data/samples/` to show invoice layout
- Mention 5 valid + 1 invalid sample for error handling demo

---

## Segment 3: Configuration Design (10 min)

Open `config/extraction_rules.yaml`

**Explain:**

- Regex patterns for each field
- Line-item row format
- Validation tolerance for total vs line items

---

## Segment 4: Core Parser Walkthrough (20 min)

Open `src/parser.py` and explain:

1. `_extract_text()` — pdfplumber page iteration
2. `_extract_field()` — regex from YAML
3. `_extract_line_items()` — structured row parsing
4. `_validate()` — total reconciliation
5. `parse_directory()` — continue on error, collect failures

Optional: set a breakpoint and step through one file.

---

## Segment 5: Models & Report Layer (10 min)

Show `src/models.py` — dataclasses for Invoice, LineItem, ParseError

Show `src/report.py` — JSON summary, vendor aggregation, error log

---

## Segment 6: Run the CLI (10 min)

```powershell
python main.py --verbose
```

Show outputs:

- `output/summary.json` — counts, vendors, totals
- `output/errors.log` — bad invoice captured

**Say:** "One invalid PDF didn't crash the batch — it's logged separately."

---

## Segment 7: Tests (15 min)

```powershell
pytest -v
```

Walk through `tests/test_parser.py`:

- Valid invoice parsing
- Invalid total raises error
- Directory batch with mixed success/failure
- Summary aggregation

If a test fails during recording, debug it on camera — that looks great.

---

## Segment 8: Wrap-Up Summary (5 min)

**Say (3–5 lines):**

> "I built a config-driven PDF invoice extractor with pdfplumber, YAML-based regex rules, batch error isolation, JSON reporting, and pytest coverage. The design separates parsing, models, and reporting so rules can change without touching core logic."

Show final `summary.json` totals one more time.

---

## What to Submit in the Form

- Screen recording (MP4)
- Optional: zip of `pdf-invoice-extractor/` folder
- Link to task proposal (`TASK_PROPOSAL.md`) if they ask for written proposal

---

## Recording Tips

1. **Talk through decisions** — "I used pdfplumber because it handles layout text better than raw pypdf."
2. **Show errors gracefully** — the bad invoice is a feature, not a bug.
3. **Run tests on camera** — passing tests = strong signal.
4. Aim for **90+ minutes** total if you include setup + explanation; **60 min** minimum if you're efficient.
