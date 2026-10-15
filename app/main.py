"""Aplicación académica LOCAL. No desplegar públicamente sin autenticación de usuarios."""
from pathlib import Path
import logging
from ipaddress import ip_address
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.models.documento import AskRequest, AskResponse
from app.services.sync_service import SyncService
from app.services.agent_service import AgentService

ROOT = Path(__file__).resolve().parents[1]
logger = logging.getLogger(__name__)
app = FastAPI(title="Archivo TIC IA", version="1.0.0")
app.mount("/assets", StaticFiles(directory=ROOT / "assets"), name="assets")

def local_only(request: Request):
    """Defensa básica para el laboratorio; no equivale a autenticación pública."""
    host = request.client.host if request.client else ""
    try:
        if not ip_address(host).is_loopback: raise ValueError()
    except ValueError:
        raise HTTPException(status_code=403, detail="Sincronización disponible solo desde localhost")
    key = settings.local_admin_key
    if key and request.headers.get("X-Admin-Key") != key:
        raise HTTPException(status_code=401, detail="Clave administrativa incorrecta")

@app.get("/")
def index():
    return FileResponse(ROOT / "index.html")

@app.get("/api/health")
def health():
    missing = [name for name, value in (
        ("OPENAI_API_KEY", settings.openai_api_key),
        ("GOOGLE_DRIVE_FOLDER_ID", settings.drive_folder_id)) if not value]
    return {"status": "ok", "configured": not missing, "missing": missing,
            "google_oauth_available": (ROOT / "credentials.json").exists() or (ROOT / "token.json").exists()}

@app.get("/api/documents")
def documents():
    doc = SyncService.load_manifest()
    return {"documents": list(doc.get("documents", {}).values()),
            "indexed": len(doc.get("documents", {})),
            "vector_store_configured": bool(settings.vector_store_id or doc.get("vector_store_id"))}

@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    try:
        if not settings.openai_api_key: raise ValueError("Falta OPENAI_API_KEY")
        return AgentService().ask(payload.question, payload.use_search)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        logger.exception("Error al consultar OpenAI")
        raise HTTPException(status_code=502, detail="Error al consultar OpenAI. Revisa el registro local.")

@app.post("/api/sync", dependencies=[Depends(local_only)])
def sync():
    try:
        if not settings.openai_api_key: raise ValueError("Falta OPENAI_API_KEY")
        return SyncService().sync()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        logger.exception("Error al sincronizar documentos")
        raise HTTPException(status_code=502, detail="Sincronización fallida. Revisa el registro local.")
