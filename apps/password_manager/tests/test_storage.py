import os
from apps.password_manager import storage


def test_initialize_and_metadata(tmp_path):
    db = tmp_path / "vault.db"
    salt = os.urandom(16)
    storage.initialize_db(db, salt, "phash")
    meta = storage.read_metadata(db)
    assert meta is not None
    s, h = meta
    assert s == salt
    assert h == "phash"
