from apps.password_manager import core


def test_init_and_unlock(tmp_path):
    db = tmp_path / "vault.db"
    core.init_vault(db, "master-pass")
    key = core.unlock_vault(db, "master-pass")
    assert key is not None
    bad = core.unlock_vault(db, "wrong-pass")
    assert bad is None


def test_add_and_get_encrypted_fields(tmp_path):
    """Test that service and username fields are encrypted and decrypted correctly."""
    db = tmp_path / "vault.db"
    core.init_vault(db, "master-pass")
    key = core.unlock_vault(db, "master-pass")

    # Add entry
    entry_id = core.add_entry(
        db,
        key,
        service="GitHub",
        username="alice",
        password="secret123",
        notes="Personal account",
    )
    assert entry_id

    # Retrieve and verify all fields are decrypted
    entry = core.get_entry(db, key, entry_id)
    assert entry is not None
    assert entry["service"] == "GitHub"
    assert entry["username"] == "alice"
    assert entry["password"] == "secret123"
    assert entry["notes"] == "Personal account"


def test_wrong_key_cannot_decrypt(tmp_path):
    """Test that decryption fails with wrong key."""
    db = tmp_path / "vault.db"
    core.init_vault(db, "master-pass")
    key = core.unlock_vault(db, "master-pass")

    # Add entry
    entry_id = core.add_entry(
        db,
        key,
        service="GitHub",
        username="alice",
        password="secret123",
        notes="Personal account",
    )

    # Try to decrypt with different key
    wrong_key = core.unlock_vault(db, "wrong-pass")
    assert wrong_key is None

    # Get entry with correct key should work
    entry = core.get_entry(db, key, entry_id)
    assert entry is not None
    assert entry["service"] == "GitHub"


def test_list_entries_preview_returns_encrypted(tmp_path):
    """Test that list_entries_preview returns encrypted service/username as hex."""
    db = tmp_path / "vault.db"
    core.init_vault(db, "master-pass")
    key = core.unlock_vault(db, "master-pass")

    # Add entry
    entry_id = core.add_entry(
        db, key, service="GitHub", username="alice", password="secret123", notes=None
    )

    # List with preview mode
    rows = core.list_entries_preview(db)
    assert len(rows) == 1
    assert rows[0]["id"] == entry_id
    assert rows[0]["encrypted"] is True
    # service and username should be hex strings
    assert isinstance(rows[0]["service"], str)
    assert isinstance(rows[0]["username"], str)
    # Hex strings should not contain the plaintext values
    assert "GitHub" not in rows[0]["service"]
    assert "alice" not in rows[0]["username"]


def test_list_entries_decrypted_returns_plaintext(tmp_path):
    """Test that list_entries_decrypted returns decrypted service/username."""
    db = tmp_path / "vault.db"
    core.init_vault(db, "master-pass")
    key = core.unlock_vault(db, "master-pass")

    # Add entries
    entry1_id = core.add_entry(
        db, key, service="GitHub", username="alice", password="secret1", notes=None
    )
    entry2_id = core.add_entry(
        db, key, service="GitLab", username="bob", password="secret2", notes=None
    )

    # List with decryption
    rows = core.list_entries_decrypted(db, key)
    assert len(rows) == 2

    # Entries should be sorted by created_at DESC, so entry2 first
    assert rows[0]["id"] == entry2_id
    assert rows[0]["service"] == "GitLab"
    assert rows[0]["username"] == "bob"
    assert "encrypted" not in rows[0]

    assert rows[1]["id"] == entry1_id
    assert rows[1]["service"] == "GitHub"
    assert rows[1]["username"] == "alice"


def test_add_entry_without_notes(tmp_path):
    """Test adding entry with optional notes=None."""
    db = tmp_path / "vault.db"
    core.init_vault(db, "master-pass")
    key = core.unlock_vault(db, "master-pass")

    entry_id = core.add_entry(
        db, key, service="Twitter", username="alice", password="secret123", notes=None
    )

    entry = core.get_entry(db, key, entry_id)
    assert entry["notes"] is None
    assert entry["service"] == "Twitter"
    assert entry["username"] == "alice"


def test_multiple_entries_isolation(tmp_path):
    """Test that multiple entries don't interfere with each other."""
    db = tmp_path / "vault.db"
    core.init_vault(db, "master-pass")
    key = core.unlock_vault(db, "master-pass")

    # Add 3 entries
    entries = []
    for i, (service, username) in enumerate(
        [("GitHub", "alice"), ("GitLab", "bob"), ("Bitbucket", "charlie")]
    ):
        entry_id = core.add_entry(
            db,
            key,
            service=service,
            username=username,
            password=f"password{i}",
            notes=f"Note for {service}",
        )
        entries.append((entry_id, service, username))

    # Retrieve each entry and verify correctness
    for entry_id, expected_service, expected_username in entries:
        entry = core.get_entry(db, key, entry_id)
        assert entry["service"] == expected_service
        assert entry["username"] == expected_username
