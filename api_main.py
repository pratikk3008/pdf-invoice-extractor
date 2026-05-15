#!/usr/bin/env python3
"""Run the FastAPI server for the PDF invoice extractor."""

import uvicorn

HOST = "127.0.0.1"
PORT = 8000

if __name__ == "__main__":
    print(f"Starting PDF Invoice Extractor API on http://{HOST}:{PORT}")
    print(f"Open API docs: http://{HOST}:{PORT}/docs")
    print(f"Health check:  http://{HOST}:{PORT}/health")
    print("Press CTRL+C to stop the server.")
    uvicorn.run("src.api:app", host=HOST, port=PORT, reload=False)
