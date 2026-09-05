"""Kisan Dost terminal agent (OpenAI Agents SDK)."""

__all__ = ["main"]


def __getattr__(name: str):
    if name == "main":
        from open_sdk_1.main import start_terminal

        return start_terminal
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
