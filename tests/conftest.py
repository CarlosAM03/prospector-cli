import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def pytest_collection_modifyitems(config, items):
    """Keep live Google Maps checks opt-in and out of the default suite."""
    if os.environ.get("PROSPECTOR_RUN_E2E") == "1":
        return

    deselected = []
    selected = []
    for item in items:
        if "e2e" in item.keywords:
            deselected.append(item)
        else:
            selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected
