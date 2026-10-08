"""Build a local Windows onedir candidate; no tag, upload or publication."""

from __future__ import annotations

import importlib.metadata as metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from version import __version__  # noqa: E402


LICENSE_PACKAGES = (
    "beautifulsoup4", "et-xmlfile", "greenlet", "markdown-it-py", "mdurl",
    "openpyxl", "playwright", "pyee", "pygments", "rich", "soupsieve",
    "pyinstaller",
)


def _copy_licenses(destination: Path) -> None:
    destination.mkdir()
    for package in LICENSE_PACKAGES:
        distribution = metadata.distribution(package)
        copied = 0
        for entry in distribution.files or ():
            name = Path(str(entry)).name.lower()
            if not name.startswith(("license", "licence", "notice", "copying")):
                continue
            source = Path(distribution.locate_file(entry))
            if not source.is_file() or "dist-info" not in str(source):
                continue
            target = destination / f"{package}-{distribution.version}-{copied}-{source.name}"
            shutil.copy2(source, target)
            copied += 1
        if copied == 0:
            raise RuntimeError(f"No distributable license text found for {package}")


def main() -> None:
    if sys.platform != "win32" or sys.maxsize <= 2**32:
        raise RuntimeError("Windows x64 Python is required")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    # Short staging also avoids unrelated Windows path-length failures.
    build_root = REPO / "temp" / f"b-{stamp}"
    if build_root.exists():
        raise FileExistsError(build_root)
    build_root.mkdir(parents=True)
    command = [
        sys.executable, "-m", "PyInstaller", "--onedir", "--console",
        "--name", "prospector", "--paths", str(REPO / "src"),
        "--collect-all", "playwright", "--distpath", str(build_root / "dist"),
        # openpyxl's optional image/numeric paths are not used by our 7-column exports.
        "--exclude-module", "numpy", "--exclude-module", "PIL",
        "--workpath", str(build_root / "work"),
        "--specpath", str(build_root / "spec"), str(REPO / "src" / "main.py"),
    ]
    subprocess.run(command, cwd=REPO, check=True)
    generated = build_root / "dist" / "prospector"
    if not (generated / "prospector.exe").is_file():
        raise RuntimeError("PyInstaller did not produce prospector.exe")
    portable = build_root / f"Prospector-CLI-v{__version__}-win64"
    shutil.copytree(generated, portable)
    forbidden = {"chrome.exe", "chrome-headless-shell.exe", "msedge.exe", "chromium.exe"}
    bundled = [path for path in portable.rglob("*.exe") if path.name.lower() in forbidden]
    if bundled or (portable / "browsers").exists():
        raise RuntimeError(f"A browser executable/cache was unexpectedly bundled: {bundled}")
    for folder in ("exports", "logs"):
        (portable / folder).mkdir()
    shutil.copy2(REPO / "LICENSE", portable / "LICENSE")
    shutil.copy2(Path(sys.base_prefix) / "LICENSE.txt", portable / "PYTHON_LICENSE.txt")
    shutil.copy2(REPO / "THIRD_PARTY_NOTICES.md", portable / "THIRD_PARTY_NOTICES.md")
    shutil.copy2(REPO / "docs" / "portable-windows.md", portable / "README_PORTABLE.md")
    _copy_licenses(portable / "THIRD_PARTY_LICENSES")
    print(json.dumps({
        "source_version": __version__, "portable": str(portable),
        "browser_runtime": "installed Microsoft Edge Stable (msedge channel)",
        "browser_executable_redistributed": False,
        "python": sys.version.split()[0], "pyinstaller": metadata.version("pyinstaller"),
        "playwright": metadata.version("playwright"), "rich": metadata.version("rich"),
    }, indent=2))


if __name__ == "__main__":
    main()
