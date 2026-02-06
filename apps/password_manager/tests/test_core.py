
from apps.password_manager import core


def test_init_and_unlock(tmp_path):
    db = tmp_path / "vault.db"
    core.init_vault(db, "master-pass")
    key = core.unlock_vault(db, "master-pass")
    assert key is not None
    bad = core.unlock_vault(db, "wrong-pass")
    assert bad is None
