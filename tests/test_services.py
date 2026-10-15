from types import SimpleNamespace as NS
from unittest.mock import MagicMock
import pytest
from app.services import sync_service, agent_service


@pytest.fixture
def lab(tmp_path, monkeypatch):
    monkeypatch.setattr(sync_service, "MANIFEST", tmp_path / "manifest.json")
    config = NS(vector_store_id="", drive_folder_id="folder", openai_model="test")
    monkeypatch.setattr(sync_service, "settings", config)
    monkeypatch.setattr(agent_service, "settings", config)
    client, drive = MagicMock(), MagicMock()
    client.vector_stores.create.return_value = NS(id="vs_test")
    client.vector_stores.files.upload_and_poll.side_effect = [
        NS(id="file_old", status="completed"), NS(id="file_new", status="completed")]
    drive.list_files.return_value = [dict(id="doc", name="Práctica", mimeType="text/plain", modifiedTime="1")]
    drive.get_bytes.return_value = (b"Contenido de prueba", "Practica.txt", "text/plain")
    return config, client, drive, sync_service.SyncService(client, drive)


def test_incremental_lifecycle(lab):
    _, client, drive, service = lab
    assert service.sync()["stats"]["added"] == 1
    assert service.sync()["stats"]["unchanged"] == 1
    assert client.vector_stores.files.upload_and_poll.call_count == 1
    drive.list_files.return_value[0]["modifiedTime"] = "2"
    assert service.sync()["stats"]["updated"] == 1
    assert service.load_manifest()["documents"]["doc"]["openai_file_id"] == "file_new"
    drive.list_files.return_value = []
    assert service.sync()["stats"]["removed"] == 1
    assert service.load_manifest()["documents"] == {}


def test_failed_update_preserves_previous(lab):
    _, client, drive, service = lab
    service.sync()
    drive.list_files.return_value[0]["modifiedTime"] = "2"
    client.vector_stores.files.upload_and_poll.side_effect = RuntimeError("Indexación fallida")
    assert len(service.sync()["stats"]["errors"]) == 1
    assert service.load_manifest()["documents"]["doc"]["openai_file_id"] == "file_old"
    client.vector_stores.files.delete.assert_not_called()


def test_changed_store_is_rejected(lab):
    config, _, _, service = lab
    service.sync()
    config.vector_store_id = "vs_other"
    with pytest.raises(ValueError, match="no coincide"):
        service.sync()
    assert service.load_manifest()["vector_store_id"] == "vs_test"


def test_unsupported_and_empty_documents(lab):
    _, client, drive, service = lab
    drive.list_files.return_value.append(dict(id="sheet", name="Tabla", mimeType="application/vnd.google-apps.spreadsheet"))
    drive.get_bytes.return_value = (b"", "vacio.txt", "text/plain")
    result = service.sync()
    assert result["stats"]["added"] == 0
    assert len(result["stats"]["errors"]) == 1
    client.vector_stores.files.upload_and_poll.assert_not_called()


def test_only_verified_unique_citations(lab):
    _, client, _, service = lab
    service.sync()
    client.responses.create.return_value = NS(output_text="Respuesta", output=[NS(content=[NS(annotations=[
        NS(type="file_citation", file_id="file_old"),
        NS(type="file_citation", file_id="file_old"),
        NS(type="file_citation", file_id="unknown")])])])
    agent = agent_service.AgentService(client)
    result = agent.ask("¿Qué dice la práctica?")
    assert result["sources"] == [{"name": "Práctica", "url": "https://drive.google.com/file/d/doc/view"}]
    assert client.responses.create.call_args.kwargs["tools"][0]["vector_store_ids"] == ["vs_test"]
    agent.ask("¿Qué dice la práctica?", False)
    assert "tools" not in client.responses.create.call_args.kwargs


def test_search_requires_index(lab):
    _, client, _, _ = lab
    with pytest.raises(ValueError, match="Primero sincroniza"):
        agent_service.AgentService(client).ask("¿Qué dice la práctica?")
    client.responses.create.assert_not_called()


def test_retrieval_is_not_a_citation(lab):
    _, client, _, service = lab
    service.sync()
    client.responses.create.return_value = NS(output_text="Respuesta", output=[
        NS(type="file_search_call", results=[NS(file_id="file_old"), NS(file_id="unknown")])])
    result = agent_service.AgentService(client).ask("Busca la práctica")
    assert result["sources"] == []
    assert len(result["retrieved_sources"]) == 1
    assert result["retrieved_sources"][0]["name"] == "Práctica"
    result = agent_service.AgentService(client).ask("Busca la práctica", False)
    assert result["retrieved_sources"] == []
    assert "NO tienes acceso" in client.responses.create.call_args.kwargs["instructions"]
