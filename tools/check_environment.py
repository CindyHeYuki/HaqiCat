"""Report whether the local HaqiCat development prerequisites are available."""

from __future__ import annotations

import importlib.metadata
import shutil
import sys


def package_version(package_name: str) -> str | None:
    """Return an installed package version, or None when unavailable."""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> int:
    """Print a compact, non-mutating environment report."""
    git_path = shutil.which("git")
    pyside_version = package_version("PySide6")
    pyinstaller_version = package_version("PyInstaller")

    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"Git: {'可用 - ' + git_path if git_path else '未找到'}")
    print(f"PySide6: {pyside_version or '未安装'}")
    print(f"PyInstaller: {pyinstaller_version or '未安装'}")

    return 0 if git_path else 1


if __name__ == "__main__":
    raise SystemExit(main())

