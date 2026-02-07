from typer.testing import CliRunner
from apps.password_manager import main
import re

runner = CliRunner()


def test_import():
    """Basic smoke test."""
    assert hasattr(main, "main")


def test_list_requires_auth(tmp_path):
    """Test that list command requires authentication."""
    db = tmp_path / "vault.db"
    
    # Initialize vault first
    result = runner.invoke(main.app, ["init", "--db", str(db)], input="test\ntest\n")
    assert result.exit_code == 0
    
    # Try list with wrong password
    result = runner.invoke(main.app, ["list", "--db", str(db)], input="wrong\n")
    assert result.exit_code == 1
    output = result.stdout + (result.stderr or "")
    assert "Invalid master password" in output


def _extract_uuid(output: str) -> str:
    """Extract UUID from output that may contain prompts."""
    # Match UUID pattern: 8-4-4-4-12 hex digits
    pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    match = re.search(pattern, output, re.IGNORECASE)
    if match:
        return match.group(0)
    raise ValueError(f"Could not find UUID in output: {output}")


def test_list_and_preview_modes(tmp_path):
    """Test both list and preview modes after adding entries."""
    db = tmp_path / "vault.db"
    
    # Initialize vault
    result = runner.invoke(main.app, ["init", "--db", str(db)], input="test\ntest\n")
    assert result.exit_code == 0
    
    # Add an entry
    result = runner.invoke(
        main.app,
        ["add", "GitHub", "alice", "--db", str(db)],
        input="test\nsecret123\n"
    )
    assert result.exit_code == 0
    entry_id = _extract_uuid(result.stdout)
    
    # List with correct password (decrypted mode)
    result = runner.invoke(main.app, ["list", "--db", str(db)], input="test\n")
    assert result.exit_code == 0
    assert "GitHub" in result.stdout
    assert "alice" in result.stdout
    
    # List with preview mode (encrypted)
    result = runner.invoke(main.app, ["list", "--db", str(db), "--preview"], input="test\n")
    assert result.exit_code == 0
    # In preview mode, plaintext should not appear
    assert "GitHub" not in result.stdout
    assert "alice" not in result.stdout
    # But entry_id should appear in the output
    assert entry_id in result.stdout


def test_get_requires_auth(tmp_path):
    """Test that get command requires authentication."""
    db = tmp_path / "vault.db"
    
    # Initialize vault
    result = runner.invoke(main.app, ["init", "--db", str(db)], input="test\ntest\n")
    assert result.exit_code == 0
    
    # Add an entry
    result = runner.invoke(
        main.app,
        ["add", "GitHub", "alice", "--db", str(db)],
        input="test\nsecret123\n"
    )
    assert result.exit_code == 0
    entry_id = _extract_uuid(result.stdout)
    
    # Try get with wrong password
    result = runner.invoke(main.app, ["get", entry_id, "--db", str(db)], input="wrong\n")
    assert result.exit_code == 1
    output = result.stdout + (result.stderr or "")
    assert "Invalid master password" in output
    
    # Get with correct password
    result = runner.invoke(main.app, ["get", entry_id, "--db", str(db)], input="test\n")
    assert result.exit_code == 0
    assert "GitHub" in result.stdout
    assert "alice" in result.stdout
