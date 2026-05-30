"""
Module for notes commands:
- add-note
- notes
- tag-sorted-notes
- note
- search-notes
- edit-note
- delete-note
- add-tag
- remove-tag
- find-by-tag
"""
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from registry import CompletionSource, completion_source, register_command
from commands.utils import input_error, validate_command_args
from dto import CommandResult, CommandContext
from exceptions import NoteError
from models import Note
from text_validation import validate_and_censor_note


def _parse_note_content(args: list[str]) -> tuple[str, str, str]:
    """Return note name, title, and text from command arguments."""
    name, title, *text_parts = args
    text = " ".join(text_parts).strip() if text_parts else title
    return name, title, text


def _sorted_note_tags(note: Note) -> list[str]:
    """Return note tags sorted alphabetically for display."""
    return sorted(str(tag) for tag in note.tags)


def _note_first_tag_sort_key(note: Note) -> tuple[str, str]:
    """Return sort key based on the note's first alphabetical tag."""
    sorted_tags = _sorted_note_tags(note)
    first_tag = sorted_tags[0] if sorted_tags else chr(127)
    return first_tag, note.name.lower()


def _build_note_panel(note: Note, *, sort_tags: bool = False) -> Panel:
    """Build a detail view for one note."""
    tags = _sorted_note_tags(note) if sort_tags else [str(tag) for tag in note.tags]
    content = Group(
        Text(validate_and_censor_note(note.title), style="bold white"),
        Text(validate_and_censor_note(note.text), style="white"),
        Text(" ".join(tags) or "-", style="italic cyan"),
        Text(
            f"Created: {note.created_at.strftime('%d.%m.%Y %H:%M:%S')}",
            style="italic yellow",
        ),
    )

    return Panel(
        content,
        title=f"{validate_and_censor_note(note.name)}({note.id})",
        title_align="left",
        border_style="blue",
        expand=False
    )


def _build_note_panels(notes: list[Note], *, sort_tags: bool = False) -> Group:
    """Build a stacked set of note panels."""
    return Group(*(_build_note_panel(note, sort_tags=sort_tags) for note in notes))


@register_command(
    "add-note",
    usage='add-note <name> <title> [text]',
    description="Create a new note by name, title, and text",
    category="notes",
)
@input_error
def add_note(context: CommandContext) -> CommandResult:
    """Create a new note."""
    validate_command_args(context.command, context.args, 2)

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
    notes = sorted(
        context.notes.list_notes(),
        key=lambda note: note.created_at,
        reverse=True,
    )
    if not notes:
        return CommandResult(message="No notes found")

    return CommandResult(message=_build_note_panels(notes))


@register_command(
    "tag-sorted-notes",
    usage="tag-sorted-notes",
    description="Show all notes sorted by their first alphabetical tag",
    category="notes",
)
@input_error
def show_tag_sorted_notes(context: CommandContext) -> CommandResult:
    """Show all notes sorted by tags."""
    notes = sorted(
        context.notes.list_notes(),
        key=_note_first_tag_sort_key,
    )
    if not notes:
        return CommandResult(message="No notes found")

    return CommandResult(message=_build_note_panels(notes, sort_tags=True))

@register_command(
    "note",
    usage="note <id/name>",
    description="Show one note by id or name",
    category="notes",
    arg_completions=(completion_source(CompletionSource.NOTE),)
)
@input_error
def show_note(context: CommandContext) -> CommandResult:
    """Show one note by id or name."""
    validate_command_args(context.command, context.args, 1)

    identifier, *_ = context.args
    note = context.notes.find(identifier)

    if note is None:
        raise NoteError("Note not found")

    return CommandResult(message=_build_note_panel(note))

@register_command(
    "search-notes",
    usage="search-notes [query]",
    description="Search notes by name, title, or text",
    category="notes",
)
@input_error
def search_notes(context: CommandContext) -> CommandResult:
    """Search notes by name, title, or text."""
    validate_command_args(context.command, context.args, 1)

    query = " ".join(context.args).strip()
    matches = context.notes.search(query)

    if not matches:
        return CommandResult(message="No matching notes found")

    return CommandResult(message=_build_note_panels(matches))

@register_command(
    "edit-note",
    usage='edit-note <id/name> <title> [text]',
    description="Edit an existing note by id or name",
    category="notes",
    arg_completions=(completion_source(CompletionSource.NOTE),)
)
@input_error
def edit_note(context: CommandContext) -> CommandResult:
    """Edit an existing note."""
    validate_command_args(context.command, context.args, 2)

    identifier, title, text = _parse_note_content(context.args)
    context.notes.edit_note(identifier, title, text)
    return CommandResult(message="Note updated")

@register_command(
    "delete-note",
    usage="delete-note <id/name>",
    description="Delete a note by id or name",
    category="notes",
    arg_completions=(completion_source(CompletionSource.NOTE),)
)
@input_error
def delete_note(context: CommandContext) -> CommandResult:
    """Delete a note by id or name."""
    validate_command_args(context.command, context.args, 1)

    identifier, *_ = context.args
    context.notes.delete_note(identifier)
    return CommandResult(message="Note deleted")

@register_command(
    "add-tag",
    usage="add-tag <name> <tag>",
    description="Add a tag to an existing note",
    category="notes",
    arg_completions=(completion_source(CompletionSource.NOTE),)
)
@input_error
def add_tag(context: CommandContext) -> CommandResult:
    """Add a tag to an existing note."""
    validate_command_args(context.command, context.args, 2)

    name, tag, *_ = context.args
    note = context.notes.find(name)

    if note is None:
        raise NoteError("Note not found")

    note.add_tag(tag)
    return CommandResult(message=f"Tag added to note: {note.name}")

@register_command(
    "remove-tag",
    usage="remove-tag <name> <tag>",
    description="Remove a tag from an existing note",
    category="notes",
    arg_completions=(completion_source(CompletionSource.NOTE),)
)
@input_error
def remove_tag(context: CommandContext) -> CommandResult:
    """Remove a tag from an existing note."""
    validate_command_args(context.command, context.args, 2)

    name, tag, *_ = context.args
    note = context.notes.find(name)

    if note is None:
        raise NoteError("Note not found")

    note.remove_tag(tag)
    return CommandResult(message=f"Tag removed from note: {note.name}")

@register_command(
    "find-by-tag",
    usage="find-by-tag <tag1> [tag2] [...]",
    description="Find notes by tags (returns notes with ANY of the given tags)",
    category="notes"
)
@input_error
def find_by_tag(context: CommandContext) -> CommandResult:
    """Find notes by one or more tags."""
    validate_command_args(context.command, context.args, 1)

    notes = context.notes.find_by_tags_any(*context.args)

    if not notes:
        return CommandResult(message="No notes found for given tags")

    notes = sorted(notes, key=lambda note: note.created_at, reverse=True)
    return CommandResult(message=_build_note_panels(notes))
