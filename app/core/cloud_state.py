"""Private persistent state for the single-owner academic web deployment."""
import base64
import hashlib
import json
import os
import time
from contextlib import contextmanager
from cryptography.fernet import Fernet


def cipher():
    secret = os.environ.get("SESSION_SECRET", "")
    if len(secret) < 40:
        raise RuntimeError("Configura SESSION_SECRET con al menos 40 caracteres")
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest()))


def encode(data):
    return cipher().encrypt(json.dumps(data).encode())


def decode(data):
    return json.loads(cipher().decrypt(data))


class CloudState:
    """Encrypt state as well as requiring private Blob access. No filesystem writes."""
    @staticmethod
    def _read(name):
        from vercel.blob import get, BlobNotFoundError
        try:
            result = get("archivo-tic/" + name, access="private", use_cache=False)
        except BlobNotFoundError:
            return None, None
        return decode(result.content), result.etag

    @classmethod
    def read(cls, name, default=None):
        data, _ = cls._read(name)
        return default if data is None else data

    @staticmethod
    def _write(name, data, overwrite=True):
        from vercel.blob import put
        args = dict(access="private", add_random_suffix=False,
                    overwrite=overwrite, content_type="application/octet-stream")
        return put("archivo-tic/" + name, encode(data), **args)

    @classmethod
    def write(cls, name, data):
        return cls._write(name, data)

    @classmethod
    def mutate(cls, name, transform):
        with cls.exclusive(name + ".lock"):
            data = cls.read(name)
            updated = transform(data)
            cls.write(name, updated)
            return updated

    @classmethod
    @contextmanager
    def exclusive(cls, name):
        """Atomic create prevents overlapping writers across function instances.

        Fail closed after an interrupted execution: an administrator must remove
        the stale lock in private storage after checking no request is running.
        """
        from vercel.blob import delete, BlobError
        try:
            cls._write(name, {"created": time.time()}, overwrite=False)
        except BlobError:
            raise ValueError("Estado ocupado. Si persiste, revisa el bloqueo en almacenamiento privado.")
        try:
            yield
        finally:
            delete("archivo-tic/" + name)

    @classmethod
    @contextmanager
    def sync_lease(cls):
        with cls.exclusive("sync.lock"):
            yield

    @classmethod
    def consume_quota(cls, kind, maximum):
        def increment(old):
            bucket = int(time.time() // 3600)
            old = old or {}
            if old.get("hour") != bucket:
                old = {"hour": bucket, "count": 0}
            if old["count"] >= maximum:
                raise ValueError("Se alcanzó el límite por hora. Intenta más tarde.")
            return {"hour": bucket, "count": old["count"] + 1}
        cls.mutate("quota-" + kind + ".bin", increment)
