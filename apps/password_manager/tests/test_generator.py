import pytest
import string
from .. import crypto
from typer.testing import CliRunner
from ..main import app


runner = CliRunner()


def test_generate_strong_password_default_length():
    password = crypto.generate_strong_password()
    assert len(password) == 20
    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)
    assert not any(c in crypto._SYMBOLS for c in password)  # Default: no symbols


def test_generate_strong_password_custom_length():
    password = crypto.generate_strong_password(length=10)
    assert len(password) == 10


def test_generate_strong_password_include_symbols():
    password = crypto.generate_strong_password(length=25, include_symbols=True)
    assert len(password) == 25
    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(c in crypto._SYMBOLS for c in password)

    # Ensure only allowed symbols are used
    for char in password:
        if not (char.isalnum() or char.isspace()):  # isalnum covers lower, upper, digit
            assert char in crypto._SYMBOLS


def test_generate_strong_password_no_ambiguous_chars():
    password = crypto.generate_strong_password(
        length=100
    )  # Long password to increase chance of ambiguous chars

    # Check for excluded lowercase
    assert "l" not in password
    assert "o" not in password
    # Check for excluded uppercase
    assert "I" not in password
    assert "O" not in password
    # Check for excluded digits
    assert "0" not in password
    assert "1" not in password


def test_generate_strong_password_minimum_complexity():
    # Test that it always includes at least one of each required type
    for _ in range(100):  # Run multiple times to reduce chance of false pass
        password = crypto.generate_strong_password(length=10, include_symbols=True)
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in crypto._SYMBOLS for c in password)


def test_generate_strong_password_value_error_too_short():
    with pytest.raises(
        ValueError, match="Password length must be at least 4 to ensure complexity."
    ):
        crypto.generate_strong_password(length=3)


# CLI Integration Tests
def test_generate_command_default():
    result = runner.invoke(app, ["generate"])
    assert result.exit_code == 0
    assert "Generated password:" in result.stdout
    password = result.stdout.split(":")[1].strip()
    assert len(password) == 20  # Default length


def test_generate_command_custom_length():
    result = runner.invoke(app, ["generate", "--length", "15"])
    assert result.exit_code == 0
    password = result.stdout.split(":")[1].strip()
    assert len(password) == 15


def test_generate_command_include_symbols():
    result = runner.invoke(app, ["generate", "--include-symbols"])
    assert result.exit_code == 0
    password = result.stdout.split(":")[1].strip()
    assert any(c in crypto._SYMBOLS for c in password)


def test_generate_command_error_too_short():
    result = runner.invoke(app, ["generate", "--length", "3"])
    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)
    assert "Password length must be at least 4 to ensure complexity." in str(
        result.exception
    )
