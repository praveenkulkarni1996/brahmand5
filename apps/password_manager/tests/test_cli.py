
# Basic smoke: import Typer app
from apps.password_manager import main


def test_import():
    assert hasattr(main, "main")
