"""Independent notes collection model."""
from collections import UserDict
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from exceptions import NoteError


NOTE_ID_LENGTH = 8


@dataclass(slots=True)
class Note:
    """Represents one plain text note."""

    id: str
    name: str
    title: str
    text: str
    created_at: datetime

    @classmethod
    def create(cls, name: str, title: str, text: str) -> "Note":
        """Create a note with validated and normalized fields."""
        clean_name = name.strip()
        clean_title = title.strip()
        clean_text = text.strip()

        if not clean_name:
            raise NoteError("Note name cannot be empty")

        if not clean_title:
            raise NoteError("Note title cannot be empty")

        if not clean_text:
            raise NoteError("Note text cannot be empty")

        return cls(
            id=uuid4().hex[:NOTE_ID_LENGTH],
            name=clean_name,
            title=clean_title,
            text=clean_text,
            created_at=datetime.now(),
        )

    def update_content(self, title: str, text: str) -> None:
        """Update note title and text after validation."""
        clean_title = title.strip()
        clean_text = text.strip()

        if not clean_title:
            raise NoteError("Note title cannot be empty")

        if not clean_text:
            raise NoteError("Note text cannot be empty")

        self.title = clean_title
        self.text = clean_text

    def __str__(self) -> str:
        """Return a compact string representation of the note."""
        created_at_str = self.created_at.strftime("%d.%m.%Y %H:%M:%S")
        if self.text == self.title:
            return f"{self.id} | {self.name} | {created_at_str} | {self.title}"

        return f"{self.id} | {self.name} | {created_at_str} | {self.title} | {self.text}"


class Notes(UserDict[str, Note]):
    """Store and manage notes indexed by unique note ids."""

    max_duplicate_suffix = 999

    def create_note(self, name: str, title: str, text: str) -> Note:
        """Create and store a note with unique name and id."""
        unique_name = self._build_unique_name(name)
        note = Note.create(unique_name, title, text)
        note.id = self._build_unique_id()
        self.data[note.id] = note
        return note

    def find(self, identifier: str) -> Note | None:
        """Return a note by id or name if it exists."""
        note = self.data.get(identifier)

        if note is not None:
            return note

        for note in self.data.values():
            if note.id == identifier or note.name == identifier:
                return note

        return None

    def search(self, query: str) -> list[Note]:
        """Return notes whose text contains the query."""
        normalized_query = query.strip().lower()

        if not normalized_query:
            return []

        return [
            note
            for note in self.list_notes()
            if normalized_query in note.text.lower()
        ]

    def edit_note(self, identifier: str, title: str, text: str) -> None:
        """Update an existing note by id or name."""
        note = self.find(identifier)

        if note is None:
            raise NoteError("Note not found")

        note.update_content(title, text)

    def delete_note(self, identifier: str) -> None:
        """Delete a note by id or name."""
        note = self.find(identifier)

        if note is None:
            raise NoteError("Note not found")

        del self.data[note.id]

    def list_notes(self) -> list[Note]:
        """Return all notes sorted by creation timestamp."""
        return sorted(self.data.values(), key=lambda note: note.created_at)

    def normalize(self) -> None:
        """Migrate loaded notes to the current structure and keys."""
        normalized_data = {}

        for note in self.data.values():
            self._ensure_current_note_fields(note, normalized_data)
            note.name = self._build_unique_name(note.name, normalized_data)
            normalized_data[note.id] = note

        self.data = normalized_data

    def __str__(self) -> str:
        """Render all notes as newline-separated text."""
        if not self.data:
            return "No notes found"

        return "\n".join(str(note) for note in self.list_notes())

    def _build_unique_name(self, name: str, data: dict[str, Note] | None = None) -> str:
        """Generate a unique note name, appending a numeric suffix if needed."""
        clean_name = name.strip()

        if not clean_name:
            raise NoteError("Note name cannot be empty")

        notes_data = self.data if data is None else data

        if not any(note.name == clean_name for note in notes_data.values()):
            return clean_name

        for index in range(1, self.max_duplicate_suffix + 1):
            candidate = f"{clean_name}({index})"
            if not any(note.name == candidate for note in notes_data.values()):
                return candidate

        raise NoteError("Too many notes with the same name")

    def _build_unique_id(self, data: dict[str, Note] | None = None) -> str:
        """Generate a short unique id for a note."""
        notes_data = self.data if data is None else data

        while True:
            note_id = uuid4().hex[:NOTE_ID_LENGTH]
            if not self._check_id_exists(note_id, notes_data):
                return note_id

    def _ensure_current_note_fields(self, note: Note, data: dict[str, Note] | None = None) -> None:
        """Backfill missing fields on older loaded note instances."""
        if not hasattr(note, "name"):
            note.name = "Note"

        notes_data = self.data if data is None else data

        if (
            not hasattr(note, "id")
            or len(note.id) > NOTE_ID_LENGTH
            or self._check_id_exists(note.id, notes_data, note)
        ):
            note.id = self._build_unique_id(notes_data)

        if not hasattr(note, "title"):
            note.title = getattr(note, "text", "")

        if not hasattr(note, "text"):
            note.text = note.title

        if not hasattr(note, "created_at"):
            note.created_at = datetime.now()

    def _check_id_exists(
        self,
        note_id: str,
        data: dict[str, Note],
        ignore_note: Note | None = None,
    ) -> bool:
        """Return True if the note id exists in keys or values."""
        keyed_note = data.get(note_id)

        if keyed_note is not None and keyed_note is not ignore_note:
            return True

        return any(note.id == note_id and note is not ignore_note for note in data.values())
