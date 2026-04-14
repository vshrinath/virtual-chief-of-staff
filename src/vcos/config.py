"""
config.py — Vault path and environment resolution.

All path logic goes through here. Never hardcode a path anywhere else.
Fails loud with actionable messages if configuration is missing.
"""

import os
import shutil
from pathlib import Path


def get_vault() -> Path:
    """
    Return the vault root path from VCOS_VAULT_PATH.

    Raises RuntimeError with actionable guidance if not set or doesn't exist.
    """
    vault = os.environ.get("VCOS_VAULT_PATH")
    if not vault:
        raise RuntimeError(
            "VCOS_VAULT_PATH is not set.\n"
            "Run 'vcos init --vault /path/to/your/vault' to create a vault,\n"
            "then set VCOS_VAULT_PATH in your .env file."
        )
    path = Path(vault).expanduser().resolve()
    if not path.exists():
        raise RuntimeError(
            f"VCOS_VAULT_PATH points to a path that does not exist: {path}\n"
            f"Run 'vcos init --vault {path}' to create it."
        )
    return path


def get_mempalace_bin() -> str:
    """
    Find the mempalace binary on PATH.

    Raises RuntimeError if not found.
    """
    mp = shutil.which("mempalace")
    if not mp:
        raise RuntimeError(
            "mempalace not found on PATH.\n"
            "Install with: pip install mempalace\n"
            "Then initialise: mempalace init ~/.mempalace/palace"
        )
    return mp


def get_palace_path() -> Path:
    """
    Return the MemPalace palace path.

    Uses MEMPALACE_PALACE_PATH env var if set, otherwise defaults to ~/.mempalace/palace.
    """
    palace = os.environ.get("MEMPALACE_PALACE_PATH")
    if palace:
        return Path(palace).expanduser().resolve()
    return Path.home() / ".mempalace" / "palace"
