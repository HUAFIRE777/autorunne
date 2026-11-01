from __future__ import annotations

__all__ = ["app", "__version__"]
__version__ = "0.7.0"


def __getattr__(name: str):
    if name == "app":
        from .cli import app

        return app
    raise AttributeError(name)
