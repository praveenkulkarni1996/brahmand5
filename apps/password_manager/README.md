# Password Manager (MVP)

CLI password manager. Use `--db /path/to/vault.db` to specify vault location; otherwise a default path is used.

Run examples:

```bash
python -m apps.password_manager.main init --db ./vault.db
python -m apps.password_manager.main add "example.com" "me@example.com" --db ./vault.db
```
