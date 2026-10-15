"""Google web OAuth, owner authorization and HTTPS cookies."""
import json
import logging
import os
import secrets
from urllib.parse import urlsplit
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest
from itsdangerous import URLSafeTimedSerializer, BadSignature
from app.core.config import cloud_mode
from app.core.cloud_state import CloudState, encode, decode, cipher

logger = logging.getLogger(__name__)
router = APIRouter()
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email",
          "https://www.googleapis.com/auth/drive.readonly"]
SESSION = "__Host-archivo_session"
OAUTH = "__Host-archivo_oauth"


def origin():
    value = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path:
        raise RuntimeError("PUBLIC_BASE_URL debe ser un origen HTTPS")
    return value


def owner():
    return os.environ.get("OWNER_EMAIL", "").strip().lower()


def signer():
    cipher()  # Validate secret length before signing anything.
    return URLSafeTimedSerializer(os.environ["SESSION_SECRET"], salt="archivo-session-v1")


def authenticated(request):
    try:
        data = signer().loads(request.cookies.get(SESSION, ""), max_age=8 * 3600)
        return bool(owner() and data.get("email") == owner())
    except (BadSignature, RuntimeError):
        return False


def require_owner(request: Request):
    if not cloud_mode():
        return
    if not authenticated(request):
        raise HTTPException(401, "Inicia sesión con la cuenta autorizada de Google")
    if request.method not in ("GET", "HEAD") and request.headers.get("origin") != origin():
        raise HTTPException(403, "Origen de la solicitud no autorizado")


def flow(**kwargs):
    client_id = os.environ.get("GOOGLE_WEB_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_WEB_CLIENT_SECRET", "")
    if not client_id or not client_secret or not owner():
        raise HTTPException(503, "Completa la configuración OAuth web del servidor")
    config = {"web": {"client_id": client_id, "client_secret": client_secret,
                      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                      "token_uri": "https://oauth2.googleapis.com/token"}}
    return Flow.from_client_config(config, scopes=SCOPES,
                                   redirect_uri=origin() + "/auth/callback", **kwargs)


@router.get("/api/session")
def session(request: Request):
    return {"web": cloud_mode(), "authenticated": not cloud_mode() or authenticated(request)}


@router.get("/auth/login")
def login():
    if not cloud_mode():
        return RedirectResponse("/")
    nonce = secrets.token_urlsafe(24)
    oauth = flow(autogenerate_code_verifier=True)
    url, state = oauth.authorization_url(access_type="offline", prompt="consent",
                                         nonce=nonce, login_hint=owner())
    response = RedirectResponse(url)
    response.set_cookie(OAUTH, encode({"state": state, "nonce": nonce,
                                       "verifier": oauth.code_verifier}).decode(),
                        max_age=600, secure=True, httponly=True, samesite="lax", path="/")
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/auth/callback")
def callback(request: Request):
    if not cloud_mode():
        raise HTTPException(404)
    stage = "state"
    try:
        saved = json.loads(cipher().decrypt(request.cookies.get(OAUTH, "").encode(), ttl=600))
        state = request.query_params.get("state", "")
        if not secrets.compare_digest(state, saved["state"]) or not request.query_params.get("code"):
            raise ValueError("Invalid OAuth state")
        stage = "token"
        oauth = flow(state=state, code_verifier=saved["verifier"])
        oauth.fetch_token(code=request.query_params["code"])
        stage = "identity"
        claims = id_token.verify_oauth2_token(oauth.credentials.id_token, GoogleRequest(),
                                              os.environ["GOOGLE_WEB_CLIENT_ID"])
        if (claims.get("email", "").lower() != owner() or not claims.get("email_verified")
                or claims.get("nonce") != saved["nonce"]):
            raise ValueError("Unauthorized account")
        stage = "credentials"
        info = json.loads(oauth.credentials.to_json())
        if not info.get("refresh_token"):
            raise ValueError("Missing refresh token")
        stage = "storage"
        CloudState.write("google-credentials.bin", info)
    except Exception as exc:
        # Never log the exception message, request URL, codes or token payloads.
        logger.error("OAuth callback failed stage=%s type=%s", stage, type(exc).__name__)
        raise HTTPException(400, "No se pudo autorizar. Usa la cuenta permitida e inicia de nuevo.")
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(SESSION, signer().dumps({"email": owner(), "sid": secrets.token_urlsafe(16)}),
                        max_age=8 * 3600, secure=True, httponly=True, samesite="lax", path="/")
    response.delete_cookie(OAUTH, path="/", secure=True, httponly=True, samesite="lax")
    response.headers["Cache-Control"] = "no-store"
    return response


@router.post("/auth/logout")
def logout(request: Request):
    require_owner(request)
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(SESSION, path="/", secure=True, httponly=True, samesite="lax")
    return response
