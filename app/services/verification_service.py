"""Read-only checks against the live folder and OpenAI index, not just env vars."""
from datetime import datetime, timezone
from urllib.parse import urlsplit
from openai import OpenAI
from app.core.config import settings, cloud_mode
from app.services.drive_service import DriveService
from app.services.sync_service import SyncService, SUPPORTED


class VerificationService:
    def __init__(self, client=None, drive_factory=None):
        self.client = client
        self.drive_factory = drive_factory or DriveService

    def run(self):
        checks = []
        def record(key, title, status, evidence):
            checks.append(dict(id=key, title=title, status=status, evidence=evidence))
        manifest = SyncService.load_manifest()
        docs = manifest.get('documents', {})
        record('minimum', 'Al menos cinco documentos (15, 21)',
               'pass' if len(docs) >= 5 else 'fail', f'{len(docs)} documentos en el manifiesto.')
        sync = manifest.get('sync', {})
        state = sync.get('state')
        clean = state == 'completed' and not sync.get('stats', {}).get('errors')
        record('sync', 'Última sincronización (40, 47)', 'pass' if clean else 'pending',
               f"Estado: {state or 'sin evidencia registrada'}. Errores: {len(sync.get('stats', {}).get('errors', []))}.")
        formats = {d.get('mime_type') for d in docs.values()}
        names = [('PDF', 'application/pdf'), ('TXT', 'text/plain'), ('Google Docs', 'application/vnd.google-apps.document')]
        missing = [name for name, mime in names if mime not in formats]
        record('formats', 'PDF, TXT y Google Docs (15, 38)', 'pending' if missing else 'pass',
               'Falta probar en el corpus actual: ' + ', '.join(missing) if missing else 'Los tres formatos están en el índice.')
        valid_links = bool(docs) and all(
            urlsplit(d.get('url', '')).scheme == 'https' and
            urlsplit(d.get('url', '')).hostname in ('drive.google.com', 'docs.google.com') and
            f'/d/{drive_id}/' in urlsplit(d.get('url', '')).path + '/'
            for drive_id, d in docs.items())
        record('links', 'Enlaces asociados a IDs de Drive (41, 46)', 'pass' if valid_links else 'fail',
               'Los enlaces corresponden a los IDs del manifiesto. Abrir las fuentes sigue siendo una revisión manual.')
        try:
            files = self.drive_factory().list_files(settings.drive_folder_id)
            live = {f['id']: f for f in files if f['mimeType'] in SUPPORTED}
            changed = [key for key in set(live) & set(docs)
                       if live[key].get('modifiedTime') != docs[key].get('modified_time')]
            added, removed = len(set(live)-set(docs)), len(set(docs)-set(live))
            same = not (added or removed or changed)
            record('drive', 'Drive API y OAuth en vivo (21, 37)', 'pass', f'{len(live)} archivos admitidos accesibles en la carpeta autorizada.')
            record('freshness', 'Drive coincide con el índice (40, 47)', 'pass' if same else 'fail',
                   f'Pendientes: {added} nuevos, {len(changed)} modificados, {removed} retirados. Sincroniza si hay diferencias.')
        except Exception as exc:
            record('drive', 'Drive API y OAuth en vivo (21, 37)', 'fail',
                   f'No se pudo consultar Drive ({type(exc).__name__}). Revisa la conexión de Google.')
        store = settings.vector_store_id or manifest.get('vector_store_id')
        if not store:
            record('vector', 'Indexación en OpenAI (39)', 'fail', 'No hay índice configurado; sincroniza primero.')
        else:
            try:
                client = self.client or OpenAI(api_key=settings.openai_api_key, timeout=25, max_retries=0)
                remote = list(client.vector_stores.files.list(vector_store_id=store, limit=100))
                remote_by_id = {f.id: f.status for f in remote}
                expected = [d.get('openai_file_id') for d in docs.values()]
                completed = sum(remote_by_id.get(i) == 'completed' for i in expected)
                unique = len(expected) == len(set(expected))
                extra = len(set(remote_by_id)-set(expected))
                ok = bool(expected) and unique and completed == len(expected) and extra == 0
                record('vector', 'Indexación en OpenAI (39)', 'pass' if ok else 'fail',
                       f'{completed}/{len(expected)} archivos del manifiesto completados; {extra} adicionales en el índice. Las retiradas pueden tener consistencia eventual.')
            except Exception as exc:
                record('vector', 'Indexación en OpenAI (39)', 'fail',
                       f'No se pudo comprobar OpenAI ({type(exc).__name__}). Revisa las credenciales y el servicio.')
        manual = [
            {'requirement': '43–45: comparación con/sin File Search', 'evidence': 'Usa la comparación del panel con la misma pregunta. Revisa precisión y evidencia; las citas no garantizan corrección.'},
            {'requirement': '46: localizar, resumir y comparar', 'evidence': 'Conserva al menos tres consultas y abre sus fuentes originales.'},
            {'requirement': '47: alta, cambio, baja y repetición sin cambios', 'evidence': 'Usa un documento de ensayo y guarda las estadísticas antes y después. El panel no altera Drive.'},
            {'requirement': '27, 48–54: local, GitHub, seguridad y despliegue', 'evidence': 'Revisa pytest, historial, exclusión de secretos, permisos y persistencia. Una revisión web no certifica el historial ni el equipo local.'},
            {'requirement': 'Conclusiones personales', 'evidence': 'Explica Drive API, OAuth, indexación, contexto y generación con tus propias palabras.'},
        ]
        return {'checked_at': datetime.now(timezone.utc).isoformat(), 'mode': 'web' if cloud_mode() else 'local',
                'checks': checks, 'manual': manual,
                'summary': {s: sum(c['status'] == s for c in checks) for s in ('pass','fail','pending')},
                'scope': 'Comprobación puntual. No certifica por sí sola todos los requisitos de la práctica.'}
