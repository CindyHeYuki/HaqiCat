"""Application bootstrap for the HaqiCat desktop pet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from haqicat.sprite_window import SpritePetWindow


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser used by development and smoke tests."""
    parser = argparse.ArgumentParser(description="Run the HaqiCat desktop pet.")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Show the native window briefly, print diagnostics, then exit.",
    )
    parser.add_argument(
        "--screenshot",
        type=Path,
        help="Save a screenshot of the pet window after it becomes visible.",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    """Create and run the Qt application."""
    args = build_parser().parse_args(argv)
    application = QApplication.instance() or QApplication(sys.argv[:1])
    application.setApplicationName("HaqiCat")
    application.setQuitOnLastWindowClosed(True)

    window = SpritePetWindow()
    window.show()

    if args.smoke_test:
        QTimer.singleShot(
            250,
            lambda: print(
                json.dumps(window.diagnostic_state(), ensure_ascii=False)
            ),
        )

    if args.screenshot:
        screenshot_path = args.screenshot.resolve()

        def save_screenshot() -> None:
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            if not window.grab().save(str(screenshot_path)):
                print(f"无法保存窗口截图：{screenshot_path}", file=sys.stderr)
                application.exit(2)
                return
            print(f"窗口截图已保存：{screenshot_path}")

        QTimer.singleShot(350, save_screenshot)

    if args.smoke_test:
        QTimer.singleShot(900, application.quit)

    return application.exec()


def main() -> int:
    """CLI entry point."""
    return run()


if __name__ == "__main__":
    raise SystemExit(main())

