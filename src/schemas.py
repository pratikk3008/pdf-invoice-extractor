from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    invoice_count: int
    error_count: int


class LineItemResponse(BaseModel):
    description: str
    quantity: int
    unit_price: float
    line_total: float


class InvoiceSummaryResponse(BaseModel):
    source_file: str
    invoice_number: str
    vendor: str
    date: str
    total: float
    computed_total: float
    line_item_count: int


class InvoiceDetailResponse(InvoiceSummaryResponse):
    line_items: list[LineItemResponse]


class ParseErrorResponse(BaseModel):
    source_file: str
    message: str


class SummaryResponse(BaseModel):
    processed_count: int
    success_count: int
    error_count: int
    total_amount: float
    vendors: dict[str, float]
    invoices: list[dict]


class ProcessResponse(BaseModel):
    message: str
    processed_count: int
    success_count: int
    error_count: int


class UploadResponse(BaseModel):
    message: str
    uploaded_files: list[str]


class ConfigRulesResponse(BaseModel):
    rules_path: str
    rules: dict


class InvoiceListResponse(BaseModel):
    count: int
    invoices: list[InvoiceSummaryResponse]


class ErrorListResponse(BaseModel):
    count: int
    errors: list[ParseErrorResponse]


class MessageResponse(BaseModel):
    message: str


class LoadSamplesRequest(BaseModel):
    directory: str | None = Field(
        default=None,
        description="Optional directory override. Defaults to bundled sample invoices.",
    )


class DuplicateListResponse(BaseModel):
    count: int
    duplicate_invoice_numbers: list[str]


class VendorTotalsResponse(BaseModel):
    count: int
    vendors: dict[str, float]
