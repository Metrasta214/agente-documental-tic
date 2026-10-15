import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core import web_auth
from app.core.cloud_state import CloudState, encode, decode


@pytest.fixture
def web(monkeypatch):
    monkeypatch.setenv("APP_MODE", "web")
    monkeypatch.setenv("SESSION_SECRET", "test-only-secret-" * 5)
    monkeypatch.setenv("OWNER_EMAIL", "owner@example.com")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://archivo.example")
    monkeypatch.setenv("GOOGLE_WEB_CLIENT_ID", "test.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_WEB_CLIENT_SECRET", "test-secret")
    with TestClient(app, base_url="https://archivo.example") as client:
        yield client


def authorize(client, email="owner@example.com"):
    client.cookies.set(web_auth.SESSION, web_auth.signer().dumps({"email": email}))


def test_public_inventory_and_queries_keep_sync_private(web, monkeypatch):
    from app.services.agent_service import AgentService
    monkeypatch.setattr(CloudState, "read", lambda *args: {"documents": {"private-id": {
        "name": "Documento.pdf", "url": "https://drive.google.com/file/d/public/view",
        "openai_file_id": "file-secret", "modified_time": "internal"}}})
    quota = []
    monkeypatch.setattr(CloudState, "consume_quota", lambda *args: quota.append(args))
    monkeypatch.setattr(AgentService, "ask", lambda *args: {"success": True, "answer": "Respuesta", "sources": []})
    r=web.get('/api/documents')
    assert r.status_code == 200
    assert 'file-secret' not in r.text and 'private-id' not in r.text
    assert r.json()['indexed'] == 1
    assert web.post('/api/ask', json={"question": "Pregunta"}, headers={"origin": "https://archivo.example"}).status_code == 200
    assert quota == [("ask", 30)]
    assert web.post('/api/ask', json={"question": "Pregunta"}).status_code == 403
    assert web.post('/api/sync', headers={"origin": "https://archivo.example"}).status_code == 401
    assert web.get('/api/session').json() == {"web": True, "authenticated": False, "can_query": True, "can_sync": False}


def test_web_rejects_forged_or_other_owner_sync(web):
    web.cookies.set(web_auth.SESSION, "forged")
    assert web.post('/api/sync', headers={"origin": "https://archivo.example"}).status_code == 401
    authorize(web, "other@example.com")
    assert web.post('/api/sync', headers={"origin": "https://archivo.example"}).status_code == 401


def test_owner_inventory_and_csrf(web, monkeypatch):
    authorize(web)
    monkeypatch.setattr(CloudState, "read", lambda *args: {"documents": {}})
    assert web.get('/api/documents').status_code == 200
    assert web.post('/api/sync', headers={"origin": "https://evil.example"}).status_code == 403
    assert web.post('/api/ask', json={"question": "Pregunta"}).status_code == 403
    assert web.get('/api/documents').headers['cache-control'] == 'no-store'


def test_oauth_state_pkce_and_secure_cookie(web):
    r = web.get('/auth/login', follow_redirects=False)
    assert r.status_code == 307
    assert 'code_challenge=' in r.headers['location']
    assert 'nonce=' in r.headers['location']
    cookie = r.headers['set-cookie'].lower()
    assert 'secure' in cookie and 'httponly' in cookie and 'samesite=lax' in cookie
    bad = web.get('/auth/callback?state=wrong&code=wrong')
    assert bad.status_code == 400


def test_encrypted_state_and_tamper_rejection(web):
    raw = encode({"refresh_token": "private-test-token"})
    assert b'private-test-token' not in raw
    assert decode(raw)['refresh_token'] == 'private-test-token'
    with pytest.raises(Exception):
        decode(raw[:-1] + b'!')


def test_sync_lease_released_and_quotas(web, monkeypatch):
    from contextlib import contextmanager
    @contextmanager
    def lock(name):
        yield
    state = {}
    monkeypatch.setattr(CloudState, "exclusive", lock)
    monkeypatch.setattr(CloudState, "read", lambda name, default=None: state.get(name, default))
    monkeypatch.setattr(CloudState, "write", lambda name, value: state.update({name: value}))
    CloudState.consume_quota("ask", 1)
    with pytest.raises(ValueError, match="límite"):
        CloudState.consume_quota("ask", 1)


def test_web_health_requires_python_blob_credential(web, monkeypatch):
    monkeypatch.delenv("BLOB_READ_WRITE_TOKEN", raising=False)
    monkeypatch.setenv("BLOB_STORE_ID", "store-test")
    assert "BLOB_READ_WRITE_TOKEN" in web.get('/api/health').json()["missing"]
    monkeypatch.setenv("BLOB_READ_WRITE_TOKEN", "test-credential-not-real")
    body = web.get('/api/health').json()
    assert "BLOB_READ_WRITE_TOKEN" not in body["missing"]
    assert "test-credential-not-real" not in json.dumps(body)


def test_logout_clears_session_and_oauth_even_when_expired(web, monkeypatch):
    monkeypatch.setattr(CloudState, "read", lambda *args: {"documents": {}})
    web.cookies.set(web_auth.SESSION, "expired")
    web.cookies.set(web_auth.OAUTH, "old-flow")
    r = web.post('/auth/logout', headers={"origin": "https://archivo.example"}, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"
    cookies = r.headers.get_list("set-cookie")
    assert any(web_auth.SESSION in c and "Max-Age=0" in c for c in cookies)
    assert any(web_auth.OAUTH in c and "Max-Age=0" in c for c in cookies)
    assert web.get('/api/session').json()["authenticated"] is False
    assert web.get('/api/documents').status_code == 200
    assert web.post('/auth/logout', headers={"origin": "https://evil.example"}).status_code == 403
    assert web.get('/').headers["referrer-policy"] == "same-origin"


def test_inventory_reports_persistent_sync_progress(web, monkeypatch):
    authorize(web)
    progress = {"state": "running", "total": 7, "processed": 2}
    monkeypatch.setattr(CloudState, "read", lambda *args: {"documents": {}, "sync": progress})
    assert web.get('/api/documents').json()["sync"] == progress
