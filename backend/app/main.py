import os
import logging
from uuid import uuid4
from fastapi import FastAPI
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.medical_agent.router import router as agent_router
from app.modules.chat.router import router as chat_router
from app.modules.admin.router import router as admin_router
from app.modules.mcp.router import router as mcp_router
from app.modules.rag.router import router as rag_router
from app.modules.guardrails.router import router as guardrails_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic AI Medical Platform - Modular Monolith with FastAPI, LangGraph, Generative AI API, MCP & Dedicated RAG Module"
)

logger = logging.getLogger(__name__)


def error_response(status_code: int, detail: str, request_id: str | None = None) -> JSONResponse:
    """Return a stable, client-safe error payload without exposing internal exceptions."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "request_failed",
            "detail": detail,
            "request_id": request_id or str(uuid4()),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = str(uuid4())
    detail = exc.detail if isinstance(exc.detail, str) else "Permintaan tidak dapat diproses."
    logger.warning("HTTP %s for %s [%s]: %s", exc.status_code, request.url.path, request_id, detail)
    return error_response(exc.status_code, detail, request_id)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = str(uuid4())
    logger.warning("Validation error for %s [%s]: %s", request.url.path, request_id, exc.errors())
    return error_response(422, "Data permintaan tidak valid. Periksa kembali isian Anda.", request_id)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid4())
    logger.exception("Unhandled error for %s [%s]", request.url.path, request_id)
    return error_response(500, "Terjadi gangguan pada server. Silakan coba kembali.", request_id)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Modular Monolith Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(agent_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(mcp_router, prefix=settings.API_V1_STR)
app.include_router(rag_router, prefix=settings.API_V1_STR)
app.include_router(guardrails_router, prefix=settings.API_V1_STR)

# API Health Check Endpoint
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "gemini_model": settings.GEMINI_MODEL_NAME,
        "architecture": "Modular Monolith (FastAPI + LangGraph + MCP + Dedicated RAG Module)"
    }

# Frontend static files mounting
frontend_public = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/public"))
if os.path.exists(frontend_public):
    app.mount("/static", StaticFiles(directory=frontend_public), name="static")

@app.get("/", include_in_schema=False)
def serve_index():
    index_file = os.path.join(frontend_public, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs"
    })
