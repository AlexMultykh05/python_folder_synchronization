import subprocess
import shutil
import time
from pathlib import Path
import pytest

# Paths
TEST_ROOT = Path("sync_test_env")
SOURCE = TEST_ROOT / "source"
REPLICA = TEST_ROOT / "replica"
LOG_FILE = TEST_ROOT / "log.txt"
SCRIPT = Path("folder_sync.py")

# Helper: run the sync script
def run_sync():
    subprocess.run([
        "python3", str(SCRIPT), str(SOURCE), str(REPLICA), "1", "1", str(LOG_FILE)
    ], check=True)

# Helper: clean and set up dirs
def reset_env():
    if TEST_ROOT.exists():
        shutil.rmtree(TEST_ROOT)
    SOURCE.mkdir(parents=True)
    REPLICA.mkdir()
    if LOG_FILE.exists():
        LOG_FILE.unlink()

### TEST CASES ###

def test_basic_copy():
    reset_env()
    (SOURCE / "a.txt").write_text("Hello A")
    (SOURCE / "b.txt").write_text("Hello B")
    run_sync()
    assert (REPLICA / "a.txt").read_text() == "Hello A"
    assert (REPLICA / "b.txt").read_text() == "Hello B"

def test_update_file():
    reset_env()
    (SOURCE / "file.txt").write_text("new")
    (REPLICA / "file.txt").write_text("old")
    run_sync()
    assert (REPLICA / "file.txt").read_text() == "new"

def test_remove_extra_file():
    reset_env()
    (REPLICA / "extra.txt").write_text("remove me")
    run_sync()
    assert not (REPLICA / "extra.txt").exists()

def test_nested_directory_copy():
    reset_env()
    nested = SOURCE / "dir"
    nested.mkdir()
    (nested / "file.txt").write_text("inside")
    run_sync()
    assert (REPLICA / "dir" / "file.txt").read_text() == "inside"

def test_remove_extra_dir():
    reset_env()
    extra = REPLICA / "old"
    extra.mkdir()
    (extra / "x.txt").write_text("bye")
    run_sync()
    assert not extra.exists()

# Optional: delay between tests if needed
def teardown_module(module):
    time.sleep(0.5)
