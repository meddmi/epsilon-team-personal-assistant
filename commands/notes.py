"""
Module for notes commands:
- add-note
- notes
- note
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


def _parse_note_content(args: list[str]) -> tuple[str, str, str]:
    """Return note name, title, and text from command arguments."""
    name, title, *text_parts = args
    text = " ".join(text_parts).strip() if text_parts else title
    return name, title, text

def _build_note_panel(note: Note) -> Panel:
    """Build a detail view for one note."""
    content = Group(
        Text(note.title, style="bold white"),
        Text(note.text, style="white"),
        Text(
            " ".join(str(tag) for tag in note.tags) or "-", style="italic cyan"
        ),
        Text(
            f"Created: {note.created_at.strftime('%d.%m.%Y %H:%M:%S')}",
            style="italic yellow",
        ),
    )

    return Panel(
        content,
        title=note.name,
        title_align="left",
        border_style="blue",
    )

def _build_note_panels(notes: list[Note]) -> Group:
    """Build a stacked set of note panels."""
    return Group(*(_build_note_panel(note) for note in notes))


@register_command(
    "add-note",
    usage='add-note <name> <title> [text]',
    description="Create a new note by name and title",
    category="notes",
)
@input_error
def add_note(context: CommandContext) -> CommandResult:
    """Create a new note."""
    validate_command_args(context.command, context.args, 2)

    name, title, text = _parse_note_content(context.args)
    note = context.notes.create_note(name, title, text)
    return CommandResult(message=f"Note created: {note.name}")


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
    "note",
    usage="note <name>",
    description="Show one note by name",
    category="notes",
    arg_completions=(completion_source(CompletionSource.NOTE),)
)
@input_error
def show_note(context: CommandContext) -> CommandResult:
    """Show one note by name."""
    validate_command_args(context.command, context.args, 1)

    name, *_ = context.args
    note = context.notes.find(name)

    if note is None:
        raise NoteError("Note not found")

    return CommandResult(message=_build_note_panel(note))


@register_command(
    "edit-note",
    usage='edit-note <name> <title> [text]',
    description="Edit an existing note by name",
    category="notes",
    arg_completions=(completion_source(CompletionSource.NOTE),)
)
@input_error
def edit_note(context: CommandContext) -> CommandResult:
    """Edit an existing note."""
    validate_command_args(context.command, context.args, 2)

    name, title, text = _parse_note_content(context.args)
    context.notes.edit_note(name, title, text)
    return CommandResult(message="Note updated")


@register_command(
    "delete-note",
    usage="delete-note <name>",
    description="Delete a note by name",
    category="notes",
    arg_completions=(completion_source(CompletionSource.NOTE),)
)
@input_error
def delete_note(context: CommandContext) -> CommandResult:
    """Delete a note by name."""
    validate_command_args(context.command, context.args, 1)

    name, *_ = context.args
    context.notes.delete_note(name)
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
