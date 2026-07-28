"""Dynamic module and handler loading utilities."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType


def load_modules(directory: str | Path, exclude: list[str] | None = None) -> dict[str, ModuleType]:
    """Recursively load all .py modules from a directory.

    Modules are keyed by their file stem (filename without .py).

    Args:
        directory: The directory path to scan.
        exclude: Optional list of module names to skip.

    Returns:
        A mapping of module names to loaded module objects.
    """
    exclude = set(exclude or [])
    base = Path(directory)
    if not base.is_dir():
        return {}

    modules: dict[str, ModuleType] = {}

    for root, _, filenames in base.walk():
        for filename in filenames:
            if not filename.endswith(".py") or filename.startswith("_"):
                continue

            stem = filename[:-3]
            if stem in exclude:
                continue

            rel = root.relative_to(base)
            parts = list(rel.parts) + [stem]
            qualname = ".".join(parts)

            try:
                spec = importlib.util.spec_from_file_location(
                    f"autosecure._discovered.{qualname}",
                    root / filename,
                )
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    modules[stem] = mod
            except Exception:
                continue

    return modules


def load_commands(directory: str | Path) -> list[ModuleType]:
    """Load command modules from a directory.

    Scans for .py files and imports them. Used for loading slash commands
    or prefix commands into the bot.

    Args:
        directory: The directory containing command modules.

    Returns:
        A list of loaded command module objects.
    """
    modules = load_modules(directory, exclude=["__init__"])
    return list(modules.values())


def load_handlers(directory: str | Path) -> dict[str, callable]:  # type: ignore[type-arg]
    """Load handler modules keyed by their module name.

    Each module should define a top-level `handle` callable.

    Args:
        directory: The directory containing handler modules.

    Returns:
        A mapping of handler names to their `handle` functions.
    """
    modules = load_modules(directory, exclude=["__init__"])
    handlers: dict[str, callable] = {}  # type: ignore[type-arg]

    for name, mod in modules.items():
        handler = getattr(mod, "handle", None)
        if callable(handler):
            handlers[name] = handler

    return handlers
