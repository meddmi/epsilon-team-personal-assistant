"""Persistence layer for saving and loading application data with pickle."""
import pickle
from collections.abc import Callable
from pathlib import Path
from typing import Generic, TypeVar

from models import AddressBook, Notes


DEFAULT_STORAGE_FILE = ".addressbook.pkl"
DEFAULT_NOTES_STORAGE_FILE = ".notes.pkl"

T = TypeVar("T")


class PickleStorage(Generic[T]):
    """Reusable pickle-backed storage with optional post-load normalization."""

    def __init__(
        self,
        filename: str,
        data_factory: Callable[[], T],
        data_type: type[T],
        post_load: Callable[[T], None] | None = None,
    ) -> None:
        self.filename = filename
        self._data_factory = data_factory
        self._data_type = data_type
        self._post_load = post_load
        self._data = data_factory()

    @property
    def path(self) -> Path:
        """Return the absolute path to the storage file."""
        return Path(__file__).resolve().parent / self.filename

    def load(self) -> T:
        """Load persisted data from disk or return a new empty collection."""
        try:
            with self.path.open("rb") as file:
                data = pickle.load(file)
        except (
            FileNotFoundError,
            EOFError,
            pickle.PickleError,
            AttributeError,
            ImportError,
        ):
            data = self._data_factory()

        if not isinstance(data, self._data_type):
            data = self._data_factory()
        elif self._post_load is not None:
            self._post_load(data)

        self._data = data
        return data

    def save(self) -> None:
        """Save the current state to disk."""
        with self.path.open("wb") as file:
            pickle.dump(self._data, file)

    def __enter__(self) -> T:
        """Load data when entering the storage context."""
        return self.load()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Save data when leaving the storage context."""
        if exc_type is None:
            self.save()


class AddressBookStorage(PickleStorage[AddressBook]):
    """Manage address book persistence on disk using pickle serialization."""

    def __init__(self, filename: str = DEFAULT_STORAGE_FILE) -> None:
        super().__init__(
            filename=filename,
            data_factory=AddressBook,
            data_type=AddressBook,
        )


class NotesStorage(PickleStorage[Notes]):
    """Manage notes persistence on disk using pickle serialization."""

    def __init__(self, filename: str = DEFAULT_NOTES_STORAGE_FILE) -> None:
        super().__init__(
            filename=filename,
            data_factory=Notes,
            data_type=Notes,
            post_load=lambda notes: notes.normalize(),
        )
