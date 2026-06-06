"""Entry point for the MAANG Prep Dashboard & Resume Generator.

Run with: python -m dashboard_generator.main
or:      python dashboard_generator/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from dashboard_generator.app import App


def main() -> int:
    try:
        import tkinter  # noqa: F401
    except ImportError:
        sys.stderr.write(
            "tkinter is required but not installed.\n"
            "On Debian/Ubuntu: sudo apt-get install python3-tk\n"
            "On macOS (Homebrew): brew install python-tk\n"
            "On Windows: tkinter ships with the standard python.org installer.\n"
        )
        return 1

    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
