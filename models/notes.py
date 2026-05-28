"""Independent notes collection model."""
from collections import UserDict
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from exceptions import NoteError


@dataclass(slots=True)
class Note:
    """Represents one plain text note."""

    id: str
    name: str
    title: str
    text: str
    created_at: str

    @classmethod
    def create(cls, name: str, title: str, text: str) -> "Note":
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
            id=uuid4().hex,
            name=clean_name,
            title=clean_title,
            text=clean_text,
            created_at=datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        )

    def update_content(self, title: str, text: str) -> None:
        clean_title = title.strip()
        clean_text = text.strip()

        if not clean_title:
            raise NoteError("Note title cannot be empty")

        if not clean_text:
            raise NoteError("Note text cannot be empty")

        self.title = clean_title
        self.text = clean_text

    def __str__(self) -> str:
        if self.text == self.title:
            return f"{self.name} | {self.created_at} | {self.title}"

        return f"{self.name} | {self.created_at} | {self.title} | {self.text}"


class Notes(UserDict[str, Note]):
    max_duplicate_suffix = 999

    def create_note(self, name: str, title: str, text: str) -> Note:
        unique_name = self._build_unique_name(name)
        note = Note.create(unique_name, title, text)
        self.data[note.name] = note
        return note

    def find(self, name: str) -> Note | None:
        return self.data.get(name)

    def edit_note(self, name: str, title: str, text: str) -> None:
        note = self.find(name)

        if note is None:
            raise NoteError("Note not found")

        note.update_content(title, text)

    def delete_note(self, name: str) -> None:
        if name not in self.data:
            raise NoteError("Note not found")

        del self.data[name]

    def list_notes(self) -> list[Note]:
        return sorted(self.data.values(), key=lambda note: note.created_at)

    def normalize(self) -> None:
        """Migrate loaded notes to the current structure and keys."""
        normalized_data = {}

        for note in self.data.values():
            self._ensure_current_note_fields(note)
            note.name = self._build_unique_name(note.name, normalized_data)
            normalized_data[note.name] = note

        self.data = normalized_data

    def __str__(self) -> str:
        if not self.data:
            return "No notes found"

        return "\n".join(str(note) for note in self.list_notes())

    def _build_unique_name(self, name: str, data: dict[str, Note] | None = None) -> str:
        clean_name = name.strip()

        if not clean_name:
            raise NoteError("Note name cannot be empty")

        notes_data = self.data if data is None else data

        if clean_name not in notes_data:
            return clean_name

        for index in range(1, self.max_duplicate_suffix + 1):
            candidate = f"{clean_name}({index})"
            if candidate not in notes_data:
                return candidate

        raise NoteError("Too many notes with the same name")

    def _ensure_current_note_fields(self, note: Note) -> None:
        if not hasattr(note, "name"):
            note.name = "Note"

        if not hasattr(note, "title"):
            note.title = getattr(note, "text", "")

        if not hasattr(note, "text"):
            note.text = note.title

        if not hasattr(note, "created_at"):
            note.created_at = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
