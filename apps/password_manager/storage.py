import os
import sqlite3
from pathlib import Path
from typing import Optional


SCHEMA = '''
CREATE TABLE IF NOT EXISTS metadata (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    salt BLOB NOT NULL,
    master_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entries (
    id TEXT PRIMARY KEY,
    service BLOB NOT NULL,
    username BLOB NOT NULL,
    password BLOB NOT NULL,
    notes BLOB,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
'''


def resolve_db_path(cli_db: Optional[str]) -> Path:
    if cli_db:
        return Path(cli_db).expanduser().resolve()
    # default: platform aware minimal (Linux/macOS)
    home = Path.home()
    default = home / ".local" / "share" / "brahmand5" / "vault.db"
    return default


def ensure_parent_dir(path: Path) -> None:
    parent = path.parent
    os.makedirs(parent, exist_ok=True)
    try:
        parent.chmod(0o700)
    except Exception:
        pass


def set_file_permissions(path: Path) -> None:
    try:
        path.chmod(0o600)
    except Exception:
        pass


def open_connection(path: Path) -> sqlite3.Connection:
    ensure_parent_dir(path)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.executescript(SCHEMA)
    conn.commit()
    set_file_permissions(path)
    return conn


def initialize_db(path: Path, salt: bytes, master_hash: str) -> None:
    conn = open_connection(path)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO metadata(id, salt, master_hash) VALUES(1, ?, ?)", (salt, master_hash))
    conn.commit()
    conn.close()


def read_metadata(path: Path):
    conn = open_connection(path)
    cur = conn.cursor()
    cur.execute("SELECT salt, master_hash FROM metadata WHERE id=1")
    row = cur.fetchone()
    conn.close()
    return row if row else None

