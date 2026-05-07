from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import RedirectResponse

from .schemas import (
    ConfigRulesResponse,
    ErrorListResponse,
    HealthResponse,
    InvoiceDetailResponse,
    InvoiceListResponse,
    InvoiceSummaryResponse,
    LineItemResponse,
    LoadSamplesRequest,
    MessageResponse,
    ParseErrorResponse,
    ProcessResponse,
    SummaryResponse,
    UploadResponse,
)
from .serializers import invoice_to_dict
from .service import InvoiceExtractionService

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES_PATH = PROJECT_ROOT / "config" / "extraction_rules.yaml"
DEFAULT_SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
DEFAULT_UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


def create_service() -> InvoiceExtractionService:
    return InvoiceExtractionService(
        rules_path=DEFAULT_RULES_PATH,
        samples_dir=DEFAULT_SAMPLES_DIR,
        upload_dir=DEFAULT_UPLOAD_DIR,
        output_dir=DEFAULT_OUTPUT_DIR,
    )


def create_app(service: InvoiceExtractionService | None = None) -> FastAPI:
    app = FastAPI(
        title="PDF Invoice Extractor API",
        description="Upload, process, summarize, and inspect PDF invoices.",
        version="1.0.0",
    )
    app.state.service = service or create_service()

    def get_service() -> InvoiceExtractionService:
        return app.state.service

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        """Redirect the base URL to interactive API docs."""
        return RedirectResponse(url="/docs")

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    def health_check() -> HealthResponse:
        return HealthResponse(status="ok", service="pdf-invoice-extractor")

    @app.get("/config/rules", response_model=ConfigRulesResponse, tags=["loading"])
    def load_config_rules(service: InvoiceExtractionService = Depends(get_service)) -> ConfigRulesResponse:
        return ConfigRulesResponse(
            rules_path=str(service.rules_path),
            rules=service.load_rules(),
        )

    @app.post("/load/samples", response_model=ProcessResponse, tags=["loading"])
    def load_sample_invoices(
        payload: LoadSamplesRequest | None = None,
        service: InvoiceExtractionService = Depends(get_service),
    ) -> ProcessResponse:
        directory = Path(payload.directory) if payload and payload.directory else None
        try:
            result = service.load_samples(directory)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        return ProcessResponse(
            message="Sample invoices loaded and processed",
            processed_count=len(result.invoices) + len(result.errors),
            success_count=len(result.invoices),
            error_count=len(result.errors),
        )

    async def _save_uploaded_files(uploads: list[UploadFile], service: InvoiceExtractionService) -> list[str]:
        if not uploads:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")

        saved: list[str] = []
        for upload in uploads:
            content = await upload.read()
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Uploaded file is empty: {upload.filename}",
                )
            try:
                destination = service.save_upload(upload.filename or "invoice.pdf", content)
            except ValueError as exc:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
            saved.append(destination.name)
        return saved

    @app.post("/upload", response_model=UploadResponse, tags=["loading"])
    async def upload_invoices(
        files: list[UploadFile] = File(...),
        service: InvoiceExtractionService = Depends(get_service),
    ) -> UploadResponse:
        saved = await _save_uploaded_files(files, service)
        return UploadResponse(message="Files uploaded successfully", uploaded_files=saved)

    @app.post("/upload/single", response_model=UploadResponse, tags=["loading"])
    async def upload_single_invoice(
        file: UploadFile = File(..., description="One PDF invoice file"),
        service: InvoiceExtractionService = Depends(get_service),
    ) -> UploadResponse:
        """Swagger-friendly upload endpoint with a proper file picker."""
        saved = await _save_uploaded_files([file], service)
        return UploadResponse(message="File uploaded successfully", uploaded_files=saved)

    @app.get("/uploads", response_model=UploadResponse, tags=["loading"])
    def list_uploaded_files(service: InvoiceExtractionService = Depends(get_service)) -> UploadResponse:
        files = service.list_uploads()
        return UploadResponse(message="Uploaded files listed", uploaded_files=files)

    @app.post("/process", response_model=ProcessResponse, tags=["processing"])
    def process_uploaded_invoices(
        service: InvoiceExtractionService = Depends(get_service),
    ) -> ProcessResponse:
        try:
            result = service.process_uploads()
        except FileNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        return ProcessResponse(
            message="Uploaded invoices processed",
            processed_count=len(result.invoices) + len(result.errors),
            success_count=len(result.invoices),
            error_count=len(result.errors),
        )

    @app.post("/process/{filename}", response_model=InvoiceDetailResponse, tags=["processing"])
    def process_single_invoice(
        filename: str,
        service: InvoiceExtractionService = Depends(get_service),
    ) -> InvoiceDetailResponse:
        try:
            invoice = service.process_file(filename)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        return _invoice_detail(invoice)

    @app.get("/invoices", response_model=InvoiceListResponse, tags=["invoices"])
    def list_invoices(service: InvoiceExtractionService = Depends(get_service)) -> InvoiceListResponse:
        invoices = [
            InvoiceSummaryResponse(**invoice_to_dict(invoice))
            for invoice in service.result.invoices
        ]
        return InvoiceListResponse(count=len(invoices), invoices=invoices)

    @app.get("/invoices/{invoice_number}", response_model=InvoiceDetailResponse, tags=["invoices"])
    def get_invoice(
        invoice_number: str,
        service: InvoiceExtractionService = Depends(get_service),
    ) -> InvoiceDetailResponse:
        try:
            invoice = service.get_invoice(invoice_number)
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice not found: {invoice_number}",
            ) from exc

        return _invoice_detail(invoice)

    @app.get("/summary", response_model=SummaryResponse, tags=["summarization"])
    def get_summary(service: InvoiceExtractionService = Depends(get_service)) -> SummaryResponse:
        return SummaryResponse(**service.get_summary_dict())

    @app.get("/errors", response_model=ErrorListResponse, tags=["summarization"])
    def get_errors(service: InvoiceExtractionService = Depends(get_service)) -> ErrorListResponse:
        errors = [
            ParseErrorResponse(source_file=error.source_file, message=error.message)
            for error in service.get_errors()
        ]
        return ErrorListResponse(count=len(errors), errors=errors)

    @app.delete("/reset", response_model=MessageResponse, tags=["system"])
    def reset_state(service: InvoiceExtractionService = Depends(get_service)) -> MessageResponse:
        service.reset()
        return MessageResponse(message="Extractor state reset")

    return app


def _invoice_detail(invoice) -> InvoiceDetailResponse:
    payload = invoice_to_dict(invoice, include_line_items=True)
    line_items = [LineItemResponse(**item) for item in payload.pop("line_items")]
    return InvoiceDetailResponse(**payload, line_items=line_items)


app = create_app()
