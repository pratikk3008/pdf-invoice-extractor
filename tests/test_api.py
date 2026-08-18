from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api import create_app
from src.service import InvoiceExtractionService

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = PROJECT_ROOT / "config" / "extraction_rules.yaml"
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"


@pytest.fixture
def service(tmp_path: Path) -> InvoiceExtractionService:
    upload_dir = tmp_path / "uploads"
    output_dir = tmp_path / "output"
    return InvoiceExtractionService(
        rules_path=RULES_PATH,
        samples_dir=SAMPLES_DIR,
        upload_dir=upload_dir,
        output_dir=output_dir,
    )


@pytest.fixture
def client(service: InvoiceExtractionService) -> TestClient:
    app = create_app(service=service)
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "pdf-invoice-extractor"
    assert "version" in payload


def test_load_config_rules(client: TestClient) -> None:
    response = client.get("/config/rules")

    assert response.status_code == 200
    payload = response.json()
    assert "fields" in payload["rules"]
    assert "invoice_number" in payload["rules"]["fields"]


def test_list_invoices_before_loading(client: TestClient) -> None:
    response = client.get("/invoices")

    assert response.status_code == 200
    assert response.json()["count"] == 0


def test_load_samples_endpoint(client: TestClient) -> None:
    response = client.post("/load/samples", json={})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success_count"] == 5
    assert payload["error_count"] == 1
    assert payload["processed_count"] == 6


def test_list_invoices_after_loading(client: TestClient) -> None:
    client.post("/load/samples", json={})
    response = client.get("/invoices")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 5
    assert payload["invoices"][0]["invoice_number"].startswith("INV-")


def test_get_invoice_detail(client: TestClient) -> None:
    client.post("/load/samples", json={})
    response = client.get("/invoices/INV-2024-001")

    assert response.status_code == 200
    payload = response.json()
    assert payload["vendor"] == "Acme Supplies Ltd"
    assert payload["line_item_count"] == 2
    assert len(payload["line_items"]) == 2


def test_get_invoice_not_found(client: TestClient) -> None:
    response = client.get("/invoices/INV-MISSING")

    assert response.status_code == 404


def test_summary_endpoint(client: TestClient) -> None:
    client.post("/load/samples", json={})
    response = client.get("/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success_count"] == 5
    assert payload["error_count"] == 1
    assert payload["total_amount"] == 1959.99
    assert len(payload["vendors"]) == 5


def test_errors_endpoint(client: TestClient) -> None:
    client.post("/load/samples", json={})
    response = client.get("/errors")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["errors"][0]["source_file"] == "invoice_bad_total.pdf"


def test_upload_and_process_single_valid_pdf(client: TestClient) -> None:
    pdf_path = SAMPLES_DIR / "invoice_acme_001.pdf"
    with open(pdf_path, "rb") as handle:
        upload_response = client.post(
            "/upload",
            files={"files": ("invoice_acme_001.pdf", handle, "application/pdf")},
        )

    assert upload_response.status_code == 200
    assert upload_response.json()["uploaded_files"] == ["invoice_acme_001.pdf"]

    process_response = client.post("/process/invoice_acme_001.pdf")
    assert process_response.status_code == 200
    assert process_response.json()["invoice_number"] == "INV-2024-001"


def test_process_invalid_pdf_returns_422(client: TestClient) -> None:
    pdf_path = SAMPLES_DIR / "invoice_bad_total.pdf"
    with open(pdf_path, "rb") as handle:
        client.post(
            "/upload",
            files={"files": ("invoice_bad_total.pdf", handle, "application/pdf")},
        )

    response = client.post("/process/invoice_bad_total.pdf")

    assert response.status_code == 422
    assert "Total mismatch" in response.json()["detail"]


def test_upload_rejects_non_pdf(client: TestClient) -> None:
    response = client.post(
        "/upload",
        files={"files": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]


def test_process_uploads_batch(client: TestClient) -> None:
    files = []
    for name in ["invoice_acme_001.pdf", "invoice_globex_002.pdf"]:
        files.append(
            (
                "files",
                (name, (SAMPLES_DIR / name).read_bytes(), "application/pdf"),
            )
        )

    upload_response = client.post("/upload", files=files)
    assert upload_response.status_code == 200

    process_response = client.post("/process")
    assert process_response.status_code == 200
    assert process_response.json()["success_count"] == 2

    list_response = client.get("/invoices")
    assert list_response.json()["count"] == 2


def test_list_uploads_endpoint(client: TestClient) -> None:
    pdf_path = SAMPLES_DIR / "invoice_acme_001.pdf"
    with open(pdf_path, "rb") as handle:
        client.post(
            "/upload",
            files={"files": ("invoice_acme_001.pdf", handle, "application/pdf")},
        )

    response = client.get("/uploads")
    assert response.status_code == 200
    assert "invoice_acme_001.pdf" in response.json()["uploaded_files"]


def test_reset_endpoint_clears_state(client: TestClient) -> None:
    client.post("/load/samples", json={})
    reset_response = client.delete("/reset")
    assert reset_response.status_code == 200

    summary_response = client.get("/summary")
    assert summary_response.json()["success_count"] == 0


def test_duplicates_endpoint_empty(client: TestClient) -> None:
    response = client.get("/duplicates")
    assert response.status_code == 200
    assert response.json()["count"] == 0


def test_summary_csv_download(client: TestClient) -> None:
    client.post("/load/samples", json={})
    response = client.get("/summary/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


def test_list_invoices_vendor_filter(client: TestClient) -> None:
    client.post("/load/samples", json={})
    response = client.get("/invoices", params={"vendor": "Acme Supplies Ltd"})
    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_metrics_endpoint_after_load(client: TestClient) -> None:
    client.post("/load/samples", json={})
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json()["success_count"] == 5


def test_upload_rejects_oversized_file(client: TestClient) -> None:
    oversized = b"%PDF-" + (b"0" * (5 * 1024 * 1024))
    response = client.post(
        "/upload/single",
        files={"file": ("big.pdf", oversized, "application/pdf")},
    )
    assert response.status_code == 400
    assert "upload limit" in response.json()["detail"].lower()


def test_vendors_endpoint(client: TestClient) -> None:
    client.post("/load/samples", json={})
    response = client.get("/vendors")
    assert response.status_code == 200
    assert response.json()["count"] == 5
