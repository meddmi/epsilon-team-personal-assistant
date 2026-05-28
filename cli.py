"""Module for the assistant bot CLI."""
from typing import Callable
import shlex
from prompt_toolkit import prompt
from rich.console import Console

from dto import CommandResult, CommandContext
from models import AddressBook, Notes
from exceptions import CommandError
from commands.utils import input_error

console = Console()

def print_message(message: str, style: str) -> None:
    """Print a message to the console with the specified style."""
    console.print(message, style=style, markup=False)

def parse_input(user_input: str) -> tuple[str, list[str]]:
    """Parse user input into command and arguments."""
    parts = shlex.split(user_input.strip())

    if not parts:
        return "", []

    cmd = parts[0].strip().lower()
    return cmd, parts[1:]

@input_error
def process_command(
    book: AddressBook,
    notes: Notes,
    registry: dict[str, Callable[[CommandContext], CommandResult]],
    user_input: str,
) -> CommandResult:
    """Parse user input and dispatch command to a matching handler."""

    command, args = parse_input(user_input)

    if not command or command not in registry:
        raise CommandError("Invalid command")

    result = registry[command](CommandContext(command, book, notes, args))

    return result

def run_bot(
    book: AddressBook,
    notes: Notes,
    registry: dict[str, Callable[..., CommandResult]]
) -> None:
    """Run assistant bot loop."""
    print_message("Welcome to the assistant bot!", "green")
    help_command = registry.get("help")
    if help_command is not None:
        help_result = help_command(CommandContext("help", book, notes, []))
        print_message(help_result.message, "green")

    try:
        while True:
            user_input = prompt("Enter a command: ")
            result = process_command(book, notes, registry, user_input)

            if result.error:
                print_message(result.error, "red")
            else:
                print_message(result.message, "green")

            if result.exit:
                break
    except KeyboardInterrupt, EOFError:
        print_message("\nGood bye!", "green")
