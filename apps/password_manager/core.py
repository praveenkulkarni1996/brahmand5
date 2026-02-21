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


def add_entry(
    db_path: Path,
    key: bytes,
    service: str,
    username: str,
    password: str,
    notes: Optional[str],
) -> str:
    conn = storage.open_connection(db_path)
    cur = conn.cursor()
    entry_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    enc_service = crypto.encrypt(key, service.encode("utf-8"))
    enc_username = crypto.encrypt(key, username.encode("utf-8"))
    enc_password = crypto.encrypt(key, password.encode("utf-8"))
    enc_notes = crypto.encrypt(key, notes.encode("utf-8")) if notes else None
    cur.execute(
        "INSERT INTO entries(id, service, username, password, notes, created_at, updated_at) VALUES(?,?,?,?,?,?,?)",
        (entry_id, enc_service, enc_username, enc_password, enc_notes, now, now),
    )
    conn.commit()
    conn.close()
    return entry_id


def get_entry(db_path: Path, key: bytes, entry_id: str):
    conn = storage.open_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, service, username, password, notes, created_at, updated_at FROM entries WHERE id=?",
        (entry_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    id_, enc_service, enc_username, enc_password, enc_notes, created_at, updated_at = (
        row
    )
    service = crypto.decrypt(key, enc_service).decode("utf-8")
    username = crypto.decrypt(key, enc_username).decode("utf-8")
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


def list_entries_preview(db_path: Path) -> List[dict]:
    """List entries with encrypted service/username (preview mode, no decryption)."""
    conn = storage.open_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, service, username, created_at, updated_at FROM entries ORDER BY created_at DESC"
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "service": r[1].hex() if r[1] else None,
            "username": r[2].hex() if r[2] else None,
            "created_at": r[3],
            "updated_at": r[4],
            "encrypted": True,
        }
        for r in rows
    ]


def list_entries_decrypted(db_path: Path, key: bytes) -> List[dict]:
    """List entries with decrypted service/username (requires master password key)."""
    conn = storage.open_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, service, username, created_at, updated_at FROM entries ORDER BY created_at DESC"
    )
    rows = cur.fetchall()
    conn.close()

    result = []
    for r in rows:
        try:
            service = crypto.decrypt(key, r[1]).decode("utf-8")
            username = crypto.decrypt(key, r[2]).decode("utf-8")
        except Exception:
            # Decryption failed, skip
            continue
        result.append(
            {
                "id": r[0],
                "service": service,
                "username": username,
                "created_at": r[3],
                "updated_at": r[4],
            }
        )

    return result
