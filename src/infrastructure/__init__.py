"""Infrastructure layer public exports.

Keep imports lazy so one broken generated repository module does not prevent
using the other repository implementations.
"""

from importlib import import_module


def __getattr__(name):
    if name.startswith("InMemory"):
        module = import_module(".in_memory_repositories", __name__)
        return getattr(module, name)

    if name == "SQLiteDatabase" or name.startswith("SQLite"):
        module = import_module(".sqlite_repositories", __name__)
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = []