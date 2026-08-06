from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .parser import InvoiceParser
from .report import build_summary, write_errors, write_summary, write_summary_csv


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract invoice data from PDF files and produce a JSON summary."
    )
    parser.add_argument(
        "--input-dir",
        default="data/samples",
        help="Directory containing PDF invoice files.",
    )
    parser.add_argument(
        "--rules",
        default="config/extraction_rules.yaml",
        help="YAML file with extraction regex rules.",
    )
    parser.add_argument(
        "--output",
        default="output/summary.json",
        help="Path for the aggregated JSON summary.",
    )
    parser.add_argument(
        "--error-log",
        default="output/errors.log",
        help="Path for the parsing error log.",
    )
    parser.add_argument("--export-csv", default=None, help="Optional CSV export path.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.verbose)

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        logging.error("Input directory does not exist: %s", input_dir)
        return 1

    extractor = InvoiceParser(args.rules)
    result = extractor.parse_directory(input_dir)

    report = build_summary(result)
    write_summary(report, args.output)
    write_errors(result, args.error_log)
    if args.export_csv:
        write_summary_csv(report, args.export_csv)

    logging.info(
        "Finished: %s success, %s errors, total amount $%.2f",
        report.success_count,
        report.error_count,
        report.total_amount,
    )
    return 0 if report.error_count == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
