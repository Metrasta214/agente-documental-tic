from types import SimpleNamespace as NS
from unittest.mock import MagicMock
from app.services.verification_service import VerificationService
from app.services.sync_service import SyncService
from app.core.cloud_state import CloudState


def setup_manifest(monkeypatch):
    from app.services import verification_service as mod
    docs = {str(i): dict(name=f'{i}.pdf',mime_type='application/pdf',modified_time='v1',openai_file_id=f'f{i}',url=f'https://drive.google.com/file/d/{i}/view') for i in range(5)}
    manifest = dict(documents=docs,vector_store_id='vs_test',sync={'state':'completed','stats':{'errors':[]}})
    monkeypatch.setattr(SyncService,'load_manifest',lambda:manifest)
    monkeypatch.setattr(mod,'settings',NS(vector_store_id='',drive_folder_id='folder',openai_api_key='test'))
    drive=MagicMock();drive.list_files.return_value=[dict(id=k,mimeType=d['mime_type'],modifiedTime='v1') for k,d in docs.items()]
    client=MagicMock();client.vector_stores.files.list.return_value=[NS(id=d['openai_file_id'],status='completed') for d in docs.values()]
    return manifest,drive,client


def test_live_checks_report_pdf_only_gap(monkeypatch):
    manifest,drive,client=setup_manifest(monkeypatch)
    report=VerificationService(client,lambda:drive).run()
    checks={x['id']:x for x in report['checks']}
    assert checks['drive']['status']==checks['freshness']['status']==checks['vector']['status']=='pass'
    assert checks['formats']['status']=='pending'
    assert 'TXT' in checks['formats']['evidence'] and 'Google Docs' in checks['formats']['evidence']
    assert report['manual']
    client.vector_stores.create.assert_not_called()


def test_checks_detect_stale_drive_and_incomplete_index(monkeypatch):
    _,drive,client=setup_manifest(monkeypatch)
    drive.list_files.return_value[0]['modifiedTime']='v2'
    client.vector_stores.files.list.return_value[0].status='in_progress'
    checks={x['id']:x for x in VerificationService(client,lambda:drive).run()['checks']}
    assert checks['freshness']['status']==checks['vector']['status']=='fail'


def test_connection_failures_do_not_expose_secret_messages(monkeypatch):
    _,drive,client=setup_manifest(monkeypatch)
    drive.list_files.side_effect=RuntimeError('private-token-must-not-appear')
    report=VerificationService(client,lambda:drive).run()
    assert 'private-token-must-not-appear' not in str(report)
    assert next(c for c in report['checks'] if c['id']=='drive')['status']=='fail'
