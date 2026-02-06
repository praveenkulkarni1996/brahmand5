from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Entry:
    id: str
    service: str
    username: str
    password: bytes  # encrypted blob
    notes: Optional[bytes]
    created_at: datetime
    updated_at: datetime
