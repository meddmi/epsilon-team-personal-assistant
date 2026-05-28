"""
Module for notes commands:
- add-note
- notes
- note
- search-notes
- edit-note
- delete-note
"""
from registry import register_command
from commands.utils import input_error, validate_command_args
from dto import CommandResult, CommandContext
from exceptions import NoteError


def _join_note_text(args: list[str]) -> str:
    """Build note text from command arguments."""
    return " ".join(args).strip()


def _parse_note_content(args: list[str]) -> tuple[str, str, str]:
    """Return note name, title, and text from command arguments."""
    name, title, *text_parts = args
    text = _join_note_text(text_parts) if text_parts else title
    return name, title, text


@register_command(
    "add-note",
    usage='add-note [name] [title] [text]',
    description="Create a new note by name, title, and text",
    category="notes",
)
@input_error
def add_note(context: CommandContext) -> CommandResult:
    """Create a new note."""
    validate_command_args(context.command, context.args, 3)

    name, title, text = _parse_note_content(context.args)
    note = context.notes.create_note(name, title, text)
    return CommandResult(message=f"Note created: {note.id}")


@register_command(
    "notes",
    usage="notes",
    description="Show all notes",
    category="notes",
)
@input_error
def show_notes(context: CommandContext) -> CommandResult:
    """Show all notes."""
    return CommandResult(message=str(context.notes))


@register_command(
    "note",
    usage="note [id/name]",
    description="Show one note by id or name",
    category="notes",
)
@input_error
def show_note(context: CommandContext) -> CommandResult:
    """Show one note by id or name."""
    validate_command_args(context.command, context.args, 1)

    identifier, *_ = context.args
    note = context.notes.find(identifier)

    if note is None:
        raise NoteError("Note not found")

    return CommandResult(message=str(note))


@register_command(
    "search-notes",
    usage="search-notes [query]",
    description="Search notes by text content",
    category="notes",
)
@input_error
def search_notes(context: CommandContext) -> CommandResult:
    """Search notes by text content."""
    validate_command_args(context.command, context.args, 1)

    query = " ".join(context.args).strip()
    matches = context.notes.search(query)

    if not matches:
        return CommandResult(message="No matching notes found")

    return CommandResult(message="\n".join(str(note) for note in matches))


@register_command(
    "edit-note",
    usage='edit-note [id/name] [title] [text]',
    description="Edit an existing note by id or name",
    category="notes",
)
@input_error
def edit_note(context: CommandContext) -> CommandResult:
    """Edit an existing note."""
    validate_command_args(context.command, context.args, 3)

    identifier, title, text = _parse_note_content(context.args)
    context.notes.edit_note(identifier, title, text)
    return CommandResult(message="Note updated")


@register_command(
    "delete-note",
    usage="delete-note [id/name]",
    description="Delete a note by id or name",
    category="notes",
)
@input_error
def delete_note(context: CommandContext) -> CommandResult:
    """Delete a note by id or name."""
    validate_command_args(context.command, context.args, 1)

    identifier, *_ = context.args
    context.notes.delete_note(identifier)
    return CommandResult(message="Note deleted")
