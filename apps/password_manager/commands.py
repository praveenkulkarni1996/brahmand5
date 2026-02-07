
import typer
from pathlib import Path
from . import core, storage

app = typer.Typer()


@app.command()
def init(db: str = typer.Option(None, "--db", help="Path to vault DB")):
    """Initialize a new vault"""
    path = storage.resolve_db_path(db)
    master = typer.prompt("Choose a master password", hide_input=True, confirmation_prompt=True)
    core.init_vault(path, master)
    typer.echo(f"Initialized vault at {path}")


@app.command()
def add(
    service: str = typer.Argument(...),
    username: str = typer.Argument(...),
    db: str = typer.Option(None, "--db", help="Path to vault DB"),
    notes: str = typer.Option(None, "--notes"),
):
    """Add a credential"""
    path = storage.resolve_db_path(db)
    master = typer.prompt("Master password", hide_input=True)
    key = core.unlock_vault(path, master)
    if not key:
        typer.echo("Invalid master password", err=True)
        raise typer.Exit(code=1)
    pwd = typer.prompt("Password", hide_input=True)
    entry_id = core.add_entry(path, key, service, username, pwd, notes)
    typer.echo(entry_id)


@app.command()
def get(entry_id: str, db: str = typer.Option(None, "--db", help="Path to vault DB")):
    """Get a credential by ID"""
    path = storage.resolve_db_path(db)
    master = typer.prompt("Master password", hide_input=True)
    key = core.unlock_vault(path, master)
    if not key:
        typer.echo("Invalid master password", err=True)
        raise typer.Exit(code=1)
    ent = core.get_entry(path, key, entry_id)
    if not ent:
        typer.echo("Not found", err=True)
        raise typer.Exit(code=2)
    typer.echo(ent)


@app.command()
def list(
    db: str = typer.Option(None, "--db", help="Path to vault DB"),
    preview: bool = typer.Option(False, "--preview", help="Show encrypted fields without decryption"),
):
    """List entries"""
    path = storage.resolve_db_path(db)
    master = typer.prompt("Master password", hide_input=True)
    key = core.unlock_vault(path, master)
    if not key:
        typer.echo("Invalid master password", err=True)
        raise typer.Exit(code=1)
    
    if preview:
        rows = core.list_entries_preview(path)
        # Show encrypted output
        for r in rows:
            typer.echo(f"{r['id']}  service={r['service'][:16]}...  username={r['username'][:16]}...")
    else:
        rows = core.list_entries_decrypted(path, key)
        # Show decrypted output
        for r in rows:
            typer.echo(f"{r['id']}  {r['service']}  {r['username']}")
