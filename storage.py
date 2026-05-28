"""Persistence layer for saving and loading application data with pickle."""
import pickle
from pathlib import Path

from models import AddressBook, Notes


DEFAULT_STORAGE_FILE = ".addressbook.pkl"
DEFAULT_NOTES_STORAGE_FILE = ".notes.pkl"

class AddressBookStorage:
    """Manage address book persistence on disk using pickle serialization."""

    def __init__(self, filename: str = DEFAULT_STORAGE_FILE) -> None:
        self.filename = filename
        self._data = AddressBook()

    @property
    def path(self) -> Path:
        """Return the absolute path to the storage file."""
        return Path(__file__).resolve().parent / self.filename

    def load(self) -> AddressBook:
        """Load the address book from disk or return a new empty one."""
        try:
            with self.path.open("rb") as file:
                data = pickle.load(file)

            if not isinstance(data, AddressBook):
                data = AddressBook()
        except (
            FileNotFoundError,
            EOFError,
            pickle.PickleError,
            AttributeError,
            ImportError
        ):
            data = AddressBook()

        self._data = data
        return data

    def save(self) -> None:
        """Save the current address book state to disk."""
        with self.path.open("wb") as file:
            pickle.dump(self._data, file)

    def __enter__(self) -> AddressBook:
        """Load data when entering the storage context."""
        return self.load()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Save data when leaving the storage context."""
        self.save()

class NotesStorage:
    """Manage notes persistence on disk using pickle serialization."""

    def __init__(self, filename: str = DEFAULT_NOTES_STORAGE_FILE) -> None:
        self.filename = filename
        self._data = Notes()

    @property
    def path(self) -> Path:
        """Return the absolute path to the storage file."""
        return Path(__file__).resolve().parent / self.filename

    def load(self) -> Notes:
        """Load notes from disk or return a new empty collection."""
        try:
            with self.path.open("rb") as file:
                data = pickle.load(file)

            if not isinstance(data, Notes):
                data = Notes()
            else:
                data.normalize()
        except (
            FileNotFoundError,
            EOFError,
            pickle.PickleError,
            AttributeError,
            ImportError
        ):
            data = Notes()

        self._data = data
        return data

    def save(self) -> None:
        """Save the current notes state to disk."""
        with self.path.open("wb") as file:
            pickle.dump(self._data, file)

    def __enter__(self) -> Notes:
        """Load notes when entering the storage context."""
        return self.load()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Save notes when leaving the storage context."""
        self.save()
