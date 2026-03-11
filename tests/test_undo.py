"""Tests for undo/backup (Step 10)."""
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_backup_restore():
    from goat_ts_cig.undo import backup_db, restore_db, has_backup
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
        f.write(b"sqlite db content")
        f.flush()
    try:
        assert has_backup(path) is False
        bp = backup_db(path)
        assert bp is not None
        assert bp == path + ".backup"
        assert os.path.isfile(bp)
        assert has_backup(path) is True
        with open(path, "wb") as f:
            f.write(b"modified")
        ok = restore_db(path)
        assert ok is True
        with open(path, "rb") as f:
            assert f.read() == b"sqlite db content"
        if os.path.isfile(bp):
            os.remove(bp)
    finally:
        if os.path.isfile(path):
            os.remove(path)
        backup_path = path + ".backup"
        if os.path.isfile(backup_path):
            os.remove(backup_path)


def test_backup_skip_memory():
    from goat_ts_cig.undo import backup_db, has_backup
    assert backup_db(":memory:") is None
    assert has_backup(":memory:") is False
