"""Shared MinIO client singleton (mirrors clients/sqlite.py's pattern).

MinIO is an optional plugin: it's only used when MINIO_ACCESS_KEY and
MINIO_SECRET_KEY are both set. If either is missing, `is_configured()`
returns False and callers are expected to skip storage instead of
constructing a client with empty credentials.
"""

import os
import threading
from typing import Optional

from minio import Minio

from talkingdb.logger.console import logger

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "data.talkingdb.io")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "")
MINIO_SECURE = os.getenv("MINIO_SECURE", "true").lower() == "true"
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "ttt")


_lock = threading.Lock()
_client: Optional[Minio] = None


def is_configured() -> bool:
    """Whether MINIO_ACCESS_KEY and MINIO_SECRET_KEY are both set.
    """
    return bool(MINIO_ACCESS_KEY) and bool(MINIO_SECRET_KEY)


def get_minio_client() -> Minio:
    if not is_configured():
        raise RuntimeError(
            "MinIO is not configured."
        )
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
    """Create the bucket if missing (idempotent).

    No-op with a startup warning when MinIO isn't configured, instead of
    erroring out - MinIO is an optional plugin.
    """
    if not is_configured():
        logger.warning(
            "MINIO_ACCESS_KEY/MINIO_SECRET_KEY not set - MinIO storage is "
            "disabled."
        )
        return

    client = get_minio_client()
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
