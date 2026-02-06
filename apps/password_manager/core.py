
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from . import crypto, storage


def init_vault(db_path: Path, master_password: str) -> None:
    import os
    salt = os.urandom(16)
    master_hash = crypto.hash_master_password(master_password)
    storage.initialize_db(db_path, salt, master_hash)


def unlock_vault(db_path: Path, master_password: str) -> Optional[bytes]:
    meta = storage.read_metadata(db_path)
    if not meta:
        raise RuntimeError("Vault not initialized")
    salt, master_hash = meta
    if not crypto.verify_master_password(master_hash, master_password):
        return None
    key = crypto.derive_key(master_password, salt)
    return key


def add_entry(db_path: Path, key: bytes, service: str, username: str, password: str, notes: Optional[str]) -> str:
    conn = storage.open_connection(db_path)
    cur = conn.cursor()
    entry_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    enc_password = crypto.encrypt(key, password.encode("utf-8"))
    enc_notes = crypto.encrypt(key, notes.encode("utf-8")) if notes else None
    cur.execute(
        "INSERT INTO entries(id, service, username, password, notes, created_at, updated_at) VALUES(?,?,?,?,?,?,?)",
        (entry_id, service, username, enc_password, enc_notes, now, now),
    )
    conn.commit()
    conn.close()
    return entry_id


def get_entry(db_path: Path, key: bytes, entry_id: str):
    conn = storage.open_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, service, username, password, notes, created_at, updated_at FROM entries WHERE id=?", (entry_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    id_, service, username, enc_password, enc_notes, created_at, updated_at = row
    password = crypto.decrypt(key, enc_password).decode("utf-8")
    notes = crypto.decrypt(key, enc_notes).decode("utf-8") if enc_notes else None
    return {
        "id": id_,
        "service": service,
        "username": username,
        "password": password,
        "notes": notes,
        "created_at": created_at,
        "updated_at": updated_at,
    }


def list_entries(db_path: Path) -> List[dict]:
    conn = storage.open_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, service, username, created_at, updated_at FROM entries ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "service": r[1], "username": r[2], "created_at": r[3], "updated_at": r[4]} for r in rows
    ]
