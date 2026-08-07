import os
import sqlite3
import threading
from contextlib import contextmanager

GRAPH_DB = os.getenv("GRAPH_DB", "data/graphs.db")

DICTIONARY_DB = os.getenv("DICTIONARY_DB", "data/dictionary.db")
ENTITY_DB = os.getenv("ENTITY_DB", "data/entities.db")
REGEX_DB = os.getenv("REGEX_DB", "data/regex.db")

SQLITE_BUSY_TIMEOUT_MS = int(
    os.getenv("TDB_SQLITE_BUSY_TIMEOUT_MS", "30000")
)

_thread_local = threading.local()


def _ensure_db_path(db_path: str):
    db_dir = os.path.dirname(db_path)

    if db_dir:
        os.makedirs(db_dir, exist_ok=True)


def _create_connection(db_path: str) -> sqlite3.Connection:
    _ensure_db_path(db_path)

    conn = sqlite3.connect(
        db_path,
        check_same_thread=False,
        isolation_level=None,
    )

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS};")

    return conn


def get_connection(db_path: str) -> sqlite3.Connection:
    connections = getattr(_thread_local, "connections", None)

    if connections is None:
        connections = {}
        _thread_local.connections = connections

    conn = connections.get(db_path)

    if conn is None:
        conn = _create_connection(db_path)
        connections[db_path] = conn

    return conn


@contextmanager
def sqlite_conn(db_path: str):
    conn = get_connection(db_path)

    try:
        yield conn
    finally:
        pass
