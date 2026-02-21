import os
import string
import secrets
from typing import Tuple
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


PH = PasswordHasher()


def derive_key(master_password: str, salt: bytes, length: int = 32) -> bytes:
    """Derive a symmetric key from the master password and salt using Argon2id.

    Returns raw bytes of .
    """
    if isinstance(master_password, str):
        master_bytes = master_password.encode("utf-8")
    else:
        master_bytes = master_password
    key = hash_secret_raw(
        secret=master_bytes,
        salt=salt,
        time_cost=2,
        memory_cost=65536,
        parallelism=1,
        hash_len=length,
        type=Type.ID,
    )
    return key


def hash_master_password(master_password: str) -> str:
    return PH.hash(master_password)


def verify_master_password(hash_str: str, master_password: str) -> bool:
    try:
        return PH.verify(hash_str, master_password)
    except Exception:
        return False


def encrypt(key: bytes, plaintext: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ct


def decrypt(key: bytes, blob: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = blob[:12]
    ct = blob[12:]
    return aesgcm.decrypt(nonce, ct, None)


# Character sets for password generation, excluding ambiguous characters
_LOWERCASE = "abcdefghijkmnpqrstuvwxyz"  # Excludes l, o
_UPPERCASE = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # Excludes I, O
_DIGITS = "23456789"  # Excludes 0, 1
_SYMBOLS = "@#$%"  # Restricted symbol set


def generate_strong_password(length: int = 20, include_symbols: bool = False) -> str:
    """
    Generates a cryptographically strong password.

    Excludes ambiguous characters (l, I, 0, O, 1, o) by default.
    Ensures at least one character from each included type (lowercase, uppercase, digit,
    and symbol if include_symbols is True).

    Args:
        length (int): The desired length of the password. Defaults to 20.
        include_symbols (bool): Whether to include symbols (@#$%) in the password.
                                Defaults to False.

    Returns:
        str: The generated strong password.
    """
    if length < 4:
        raise ValueError("Password length must be at least 4 to ensure complexity.")

    char_pool = [_LOWERCASE, _UPPERCASE, _DIGITS]
    password_chars = []

    # Ensure at least one from each required character type
    password_chars.append(secrets.choice(_LOWERCASE))
    password_chars.append(secrets.choice(_UPPERCASE))
    password_chars.append(secrets.choice(_DIGITS))

    if include_symbols:
        char_pool.append(_SYMBOLS)
        password_chars.append(secrets.choice(_SYMBOLS))

    # Fill the rest of the password length
    all_chars = "".join(char_pool)
    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(all_chars))

    # Shuffle the list to randomize the position of forced characters
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)
