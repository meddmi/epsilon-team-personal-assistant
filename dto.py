"""Module for core application data structures."""
from dataclasses import dataclass
from models import AddressBook, Notes


@dataclass(frozen=True, slots=True)
class CommandContext:
    """
    Runtime context passed to command handlers.
    """
    command: str
    book: AddressBook
    notes: Notes
    args: list[str]

@dataclass(frozen=True, slots=True)
class CommandResult:
    """
    Represent command execution result.
    message: str - user-facing message to display after command execution.
    exit: bool - if True tells the main loop to stop the application.
    """
    message: str
    error: str = ""
    exit: bool = False
