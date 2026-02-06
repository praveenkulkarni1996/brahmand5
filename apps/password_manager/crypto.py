import os
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
