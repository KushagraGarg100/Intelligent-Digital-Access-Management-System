from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

from google.cloud import storage

from app.core.config import settings


@dataclass(frozen=True)
class StoredObject:
    provider: str  # "gcs" | "local"
    bucket: str | None
    object_key: str
    url: str | None


class StorageService:
    def __init__(self) -> None:
        self._bucket_name = settings.GCS_BUCKET.strip()
        self._local_dir = settings.LOCAL_STORAGE_DIR

    def _use_gcs(self) -> bool:
        return bool(self._bucket_name)

    def put_bytes(self, content: bytes, original_filename: str, content_type: str) -> StoredObject:
        object_key = f"assets/{uuid.uuid4().hex}/{os.path.basename(original_filename)}"
        if self._use_gcs():
            client = storage.Client()
            bucket = client.bucket(self._bucket_name)
            blob = bucket.blob(object_key)
            blob.upload_from_string(content, content_type=content_type)
            return StoredObject(provider="gcs", bucket=self._bucket_name, object_key=object_key, url=blob.public_url)

        os.makedirs(self._local_dir, exist_ok=True)
        path = os.path.join(self._local_dir, object_key.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)
        return StoredObject(provider="local", bucket=None, object_key=object_key, url=None)

    def resolve_local_path(self, object_key: str) -> str:
        return os.path.join(self._local_dir, object_key.replace("/", os.sep))

    def get_gcs_signed_url(self, *, object_key: str, expires_seconds: int = 900) -> str | None:
        if not self._use_gcs():
            return None
        try:
            client = storage.Client()
            bucket = client.bucket(self._bucket_name)
            blob = bucket.blob(object_key)
            return blob.generate_signed_url(expiration=expires_seconds, method="GET")
        except Exception:
            return None

    def delete_object(self, *, provider: str, object_key: str) -> None:
        if provider == "gcs" and self._use_gcs():
            try:
                client = storage.Client()
                bucket = client.bucket(self._bucket_name)
                blob = bucket.blob(object_key)
                blob.delete()
            except Exception:
                pass
        elif provider == "local":
            path = self.resolve_local_path(object_key)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    # Try to remove empty parent directory
                    parent = os.path.dirname(path)
                    if not os.listdir(parent):
                        os.rmdir(parent)
                except OSError:
                    pass


storage_service = StorageService()

