from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LineItem:
    description: str
    quantity: int
    unit_price: float
    line_total: float


@dataclass
class Invoice:
    source_file: str
    invoice_number: str
    vendor: str
    date: str
    total: float
    line_items: list[LineItem] = field(default_factory=list)

    @property
    def computed_total(self) -> float:
        return round(sum(item.line_total for item in self.line_items), 2)


@dataclass
class ParseError:
    source_file: str
    message: str


@dataclass
class ExtractionResult:
    invoices: list[Invoice] = field(default_factory=list)
    errors: list[ParseError] = field(default_factory=list)


@dataclass
class SummaryReport:
    processed_count: int
    success_count: int
    error_count: int
    total_amount: float
    vendors: dict[str, float]
    invoices: list[dict]

    def to_dict(self) -> dict:
        return {
            "processed_count": self.processed_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "total_amount": round(self.total_amount, 2),
            "vendors": {k: round(v, 2) for k, v in self.vendors.items()},
            "invoices": self.invoices,
        }


def ensure_path(path: str | Path) -> Path:
    return Path(path).resolve()
