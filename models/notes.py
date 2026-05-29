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
    created_at: datetime
    tags: list[str] = field(default_factory=list)

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
            id=uuid4().hex,
            name=clean_name,
            title=clean_title,
            text=clean_text,
            created_at=datetime.now(),
            tags=[],
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

    @staticmethod
    def _normalize_tag(tag: str) -> str:
        """Normalize tag: strip, lowercase, ensure # prefix."""
        tag = tag.strip().lower()
        return tag if tag.startswith("#") else f"#{tag}"

    def add_tag(self, tag: str) -> None:
        """Add a tag to the note."""
        normalized = self._normalize_tag(tag)

        if normalized in self.tags:
            raise NoteError(f"Tag {normalized} already exists in this note")

        self.tags.append(normalized)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the note."""
        normalized = self._normalize_tag(tag)

        if normalized not in self.tags:
            raise NoteError(f"Tag {normalized} not found in this note")

        self.tags.remove(normalized)

    def has_tag(self, tag: str) -> bool:
        """Check if the note has a specific tag."""
        return self._normalize_tag(tag) in self.tags

    def __str__(self) -> str:
        """Return a compact string representation of the note."""
        created_at_str = self.created_at.strftime("%d.%m.%Y %H:%M:%S")
        if self.text == self.title:
            return f"{self.name} | {created_at_str} | {self.title}"

        return f"{self.name} | {created_at_str} | {self.title} | {self.text}"


class Notes(UserDict[str, Note]):
    """Store and manage notes indexed by unique note names."""

    max_duplicate_suffix = 999

    def create_note(self, name: str, title: str, text: str) -> Note:
        """Create and store a note under a unique normalized name."""
        unique_name = self._build_unique_name(name)
        note = Note.create(unique_name, title, text)
        self.data[note.name] = note
        return note

    def find(self, name: str) -> Note | None:
        """Return a note by name if it exists."""
        return self.data.get(name)

    def edit_note(self, name: str, title: str, text: str) -> None:
        """Update an existing note by name."""
        note = self.find(name)

        if note is None:
            raise NoteError("Note not found")

        note.update_content(title, text)

    def delete_note(self, name: str) -> None:
        """Delete a note by name."""
        if name not in self.data:
            raise NoteError("Note not found")

        del self.data[name]

    def list_notes(self) -> list[Note]:
        """Return all notes sorted by creation timestamp."""
        return sorted(self.data.values(), key=lambda note: note.created_at)
    
    def find_by_tags_any(self, *tags: str) -> list[Note]:
        """Return notes that contain ANY of the given tags."""
        return [
            note for note in self.data.values()
            if any(note.has_tag(tag) for tag in tags)
        ]

    def find_by_tags_all(self, *tags: str) -> list[Note]:
        """Return notes that contain ALL of the given tags."""
        return [
            note for note in self.data.values()
            if all(note.has_tag(tag) for tag in tags)
        ]

    def normalize(self) -> None:
        """Migrate loaded notes to the current structure and keys."""
        normalized_data = {}

        for note in self.data.values():
            self._ensure_current_note_fields(note)
            note.name = self._build_unique_name(note.name, normalized_data)
            normalized_data[note.name] = note

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

        if clean_name not in notes_data:
            return clean_name

        for index in range(1, self.max_duplicate_suffix + 1):
            candidate = f"{clean_name}({index})"
            if candidate not in notes_data:
                return candidate

        raise NoteError("Too many notes with the same name")

    def _ensure_current_note_fields(self, note: Note) -> None:
        """Backfill missing fields on older loaded note instances."""
        if not hasattr(note, "name"):
            note.name = "Note"

        if not hasattr(note, "title"):
            note.title = getattr(note, "text", "")

        if not hasattr(note, "text"):
            note.text = note.title

        if not hasattr(note, "created_at"):
            note.created_at = datetime.now()

        if not hasattr(note, "tags"): 
            note.tags = []