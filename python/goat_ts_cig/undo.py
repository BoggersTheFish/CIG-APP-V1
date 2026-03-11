"""
Backup and restore the knowledge graph DB for undo/rollback.
"""
from __future__ import annotations

import shutil


def backup_db(db_path: str) -> str | None:
    """Copy db_path to db_path + '.backup'. Returns backup path or None on failure."""
    if not db_path or db_path.strip() == ":memory:":
        return None
    try:
        backup_path = db_path.rstrip("/\\") + ".backup"
        shutil.copy2(db_path, backup_path)
        return backup_path
    except Exception:
        return None


def restore_db(db_path: str) -> bool:
    """Restore db_path from db_path + '.backup'. Returns True on success."""
    if not db_path or db_path.strip() == ":memory:":
        return False
    backup_path = db_path.rstrip("/\\") + ".backup"
    try:
        shutil.copy2(backup_path, db_path)
        return True
    except Exception:
        return False


def has_backup(db_path: str) -> bool:
    """Return True if a backup file exists for db_path."""
    if not db_path or db_path.strip() == ":memory:":
        return False
    import os
    backup_path = db_path.rstrip("/\\") + ".backup"
    return os.path.isfile(backup_path)
