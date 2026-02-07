# Password Manager (MVP)

CLI password manager. Use `--db /path/to/vault.db` to specify vault location; otherwise a default path is used.

## Commands

### `generate`

Generates a strong, random password. The generated password is **always displayed** in the console.

-   `--length`, `-l`: Specifies the length of the password (default: 20).
-   `--include-symbols`, `-s`: Includes a restricted set of symbols (`@#$%`) in the password. Ambiguous characters (like 'l', 'I', '0', 'O', '1', 'o') are excluded by default.

**Note:** The generated password is not automatically saved to your vault. You must use the `add` command if you wish to store it.

**Examples:**

*   Generate a default 20-character password:
    ```bash
    uv run python -m apps.password_manager.main generate
    ```

*   Generate a 15-character password with symbols:
    ```bash
    uv run python -m apps.password_manager.main generate --length 15 --include-symbols
    ```

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

## Test Run

To perform a test run of the password manager's core functionalities, follow these steps:

1.  **Synchronize dependencies:**
    ```bash
    uv sync
    ```

2.  **Initialize a new database:**
    Choose `test123` as the master password when prompted.
    ```bash
    DB_PATH="./temp_vault.db" # Or specify your desired path
    uv run python -m apps.password_manager.main init --db ${DB_PATH}
    ```
    *When prompted, enter `test123` twice.*
    *Expected output:*
    ```
    Output: Choose a master password: 
    Repeat for confirmation: 
    Initialized vault at /home/ubuntu/.gemini/tmp/e7a5aef9ec39ad613dcaf007556b09df07bc0ecef213a5a74d0ede329d5cf98c/temp_vault.db
    ```

3.  **Add entries:**
    When prompted for the master password, use `test123`. For the entry password, you can use any value (e.g., `examplepassword123`, `githubpassword123`).

    *First entry:*
    ```bash
    uv run python -m apps.password_manager.main add "example.com" "user@example.com" --db ${DB_PATH}
    ```
    *When prompted, enter `test123` for the master password, and `examplepassword123` for the entry password.*
    *Expected output:*
    ```
    Output: Master password: 
    Password: 
    5c258d6a-e6c0-4481-84bc-060046b4fa41
    ```

    *Second entry:*
    ```bash
    uv run python -m apps.password_manager.main add "github.com" "my_github_user" --db ${DB_PATH}
    ```
    *When prompted, enter `test123` for the master password, and `githubpassword123` for the entry password.*
    *Expected output:*
    ```
    Output: Master password: 
    Password: 
    c851ae0e-d9d2-4d9f-9446-be0ff715ebcb
    ```

4.  **Attempt to list entries with a wrong master password:**
    Enter `wrongpassword` when prompted. This command should fail with an "Invalid master password" error.
    ```bash
    uv run python -m apps.password_manager.main list --db ${DB_PATH}
    ```
    *When prompted, enter `wrongpassword`.*
    *Expected output:*
    ```
    Output: Master password: 
    Invalid master password
    Exit Code: 1
    ```

5.  **List entries with the correct master password:**
    Enter `test123` when prompted. This command should successfully display the added entries.
    ```bash
    uv run python -m apps.password_manager.main list --db ${DB_PATH}
    ```
    *When prompted, enter `test123`.*
    *Expected output:*
    ```
    Output: Master password: 
    c851ae0e-d9d2-4d9f-9446-be0ff715ebcb  github.com  my_github_user
    5c258d6a-e6c0-4481-84bc-060046b4fa41  example.com  user@example.com
    ```

6.  **Delete the temporary database file:**
    ```bash
    rm ${DB_PATH}
    ```
    *Expected output:*
    ```
    Output: (empty)
    ```

