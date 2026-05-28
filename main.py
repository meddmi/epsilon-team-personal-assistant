"""Main entry point for the Address Book CLI application."""
import importlib
import pkgutil

from storage import AddressBookStorage, NotesStorage
from cli import run_bot
from registry import get_registry


def load_commands() -> None:
    """Dynamically load command modules from the commands package."""
    import commands

    for _, module_name, _ in pkgutil.iter_modules(commands.__path__):
        if module_name == "utils":
            continue
        importlib.import_module(f"commands.{module_name}")

def main() -> None:
    """Initialize application and start CLI bot."""
    load_commands()
    commands_registry=get_registry()

    with AddressBookStorage() as book, NotesStorage() as notes:
        run_bot(book=book, notes=notes, registry=commands_registry)

if __name__ == "__main__":
    main()
