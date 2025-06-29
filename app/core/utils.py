"""Utilities."""
from __future__ import annotations

import hashlib
from typing import Any


def hash_string(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sanitize_filename(filename: str) -> str:
    return "".join(c for c in filename if c.isalnum() or c in "._-")


def truncate_text(text: str, max_length: int) -> str:
    return text[:max_length] + "..." if len(text) > max_length else text