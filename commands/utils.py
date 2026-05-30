"""Shared helpers for command handlers."""
from functools import wraps


from dto import CommandResult
from exceptions import ContactError, CommandError, NoteError
from registry import get_command_spec

def input_error(func):
    """Decorator to convert exeptions into command results."""
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (
            CommandError,
            ContactError,
            NoteError,
            ValueError,
            IndexError,
            KeyError,
        ) as error:
            error_message = error.args[0] if error.args else str(error)

        return CommandResult(message="", error=error_message)

    return inner

def validate_command_args(command_name: str, args: list[str], count: int) -> None:
    """Validate that a command received enough arguments."""
    if len(args) < count:
        command_spec = get_command_spec(command_name)
        usage = command_spec.usage if command_spec is not None else command_name
        raise CommandError(f"Usage: {usage}")
