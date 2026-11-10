"""Imports bin/shade-cli as a module: the executable has no .py extension, so it needs an explicit loader."""

import importlib.machinery
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "shade-cli"

_loader = importlib.machinery.SourceFileLoader("shade_cli", str(SCRIPT))
_spec = importlib.util.spec_from_loader("shade_cli", _loader)
shade = importlib.util.module_from_spec(_spec)
_loader.exec_module(shade)
