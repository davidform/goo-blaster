"""Portable paths shared by browser tests; GOO_ROOT selects the tested build."""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GAME_ROOT = str(Path(os.environ.get('GOO_ROOT', os.environ.get('GOO_GAME_DIR', REPO))).resolve())
ARTIFACTS = REPO / '_private' / 'test-artifacts'
ARTIFACTS.mkdir(parents=True, exist_ok=True)

BROWSER_CHANNEL = os.environ.get("GOO_BROWSER_CHANNEL") or None
