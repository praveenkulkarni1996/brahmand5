# Password Manager (MVP)

CLI password manager. Use `--db /path/to/vault.db` to specify vault location; otherwise a default path is used.

## Setup

First, synchronize dependencies using `uv`:

```bash
uv sync
```

## Run examples:

```bash
uv run python -m apps.password_manager.main init --db ./vault.db
uv run python -m apps.password_manager.main add "example.com" "me@example.com" --db ./vault.db
```
