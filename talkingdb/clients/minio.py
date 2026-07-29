"""Shared MinIO client singleton (mirrors clients/sqlite.py's pattern)."""

import os
import threading
from typing import Optional

from minio import Minio

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "data.talkingdb.io")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "")
MINIO_SECURE = os.getenv("MINIO_SECURE", "true").lower() == "true"
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "ttt")


_lock = threading.Lock()
_client: Optional[Minio] = None


def get_minio_client() -> Minio:
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = Minio(
                    MINIO_ENDPOINT,
                    access_key=MINIO_ACCESS_KEY,
                    secret_key=MINIO_SECRET_KEY,
                    secure=MINIO_SECURE,
                )
    return _client


def ensure_bucket() -> None:
    """Create the bucket if missing (idempotent)."""
    client = get_minio_client()
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
