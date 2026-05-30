"""Shared command-line parsing helpers for execution and interactive prompt UI."""
import shlex


def split_command_input(user_input: str, *, allow_partial: bool = False) -> list[str]:
    """Split command input with shell-like quoting rules."""
    source = user_input.lstrip() if allow_partial else user_input.strip()
    if not source:
        return []

    try:
        return shlex.split(source)
    except ValueError:
        if not allow_partial:
            raise

    repaired_source = _close_open_quote(source)
    if repaired_source is not None:
        try:
            return shlex.split(repaired_source)
        except ValueError:
            pass

    return source.split()


def _close_open_quote(source: str) -> str | None:
    """Append a missing closing quote when input ends mid-token."""
    quote_char = _find_unclosed_quote(source)
    if quote_char is None:
        return None

    return f"{source}{quote_char}"


def _find_unclosed_quote(source: str) -> str | None:
    """Return the currently open quote character, if any."""
    active_quote: str | None = None
    escaped = False

    for char in source:
        if escaped:
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if active_quote is None and char in {"'", '"'}:
            active_quote = char
            continue

        if char == active_quote:
            active_quote = None

    return active_quote
