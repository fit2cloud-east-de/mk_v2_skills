"""Shared path bootstrap for skill scripts under maxkb_func/."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_lib_on_path() -> Path:
    """Insert maxkb_func/scripts onto sys.path; return that directory."""
    scripts_root = Path(__file__).resolve().parents[1]
    if str(scripts_root) not in sys.path:
        sys.path.insert(0, str(scripts_root))
    return scripts_root


def skill_script_bootstrap() -> None:
    """Call at top of each skill script: adds ../../scripts to path."""
    import inspect

    frame = inspect.stack()[1]
    caller = Path(frame.filename).resolve()
    # maxkb_func/<domain>/scripts/xxx.py → maxkb_func
    root = caller.parents[2]
    scripts = root / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
