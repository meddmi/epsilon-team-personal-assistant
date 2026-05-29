"""Prompt-toolkit helpers for the assistant CLI."""
from collections.abc import Iterable
from typing import Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory

from dto import CommandResult
from models import AddressBook, Notes
from registry import ArgCompletionSpec, CompletionSource, get_command_specs


class AssistantCompleter(Completer):
    """Provide command and argument completion for the assistant CLI."""

    def __init__(
        self,
        book: AddressBook,
        notes: Notes,
        registry: dict[str, Callable[..., CommandResult]],
    ) -> None:
        self.book = book
        self.notes = notes
        self.registry = registry

    def get_completions(
        self, document: Document, complete_event: object
    ) -> Iterable[Completion]:
        """Yield completions based on the current input."""
        del complete_event

        text = document.text_before_cursor
        stripped_text = text.lstrip()
        ends_with_space = text.endswith(" ")
        words = stripped_text.split()

        if not words:
            yield from self._complete_commands("")
            return

        if len(words) == 1 and not ends_with_space:
            yield from self._complete_commands(words[0])
            return

        command = words[0].lower()
        current_arg = "" if ends_with_space else words[-1]
        arg_index = len(words) - 1 if ends_with_space else len(words) - 2
        yield from self._complete_arguments(command, current_arg, arg_index)

    def _complete_commands(self, prefix: str) -> Iterable[Completion]:
        """Complete the first token as a command name."""
        specs = get_command_specs()

        for command_name in sorted(self.registry):
            spec = specs.get(command_name)
            if spec is None or not spec.name.startswith(prefix.lower()):
                continue

            yield Completion(
                spec.name,
                start_position=-len(prefix),
                display_meta=spec.description,
            )

    def _complete_arguments(
        self,
        command: str,
        current_arg: str,
        arg_index: int,
    ) -> Iterable[Completion]:
        """Complete command arguments based on command metadata."""
        spec = get_command_specs().get(command)
        if spec is None or arg_index < 0 or arg_index >= len(spec.arg_completions):
            return

        completion = spec.arg_completions[arg_index]
        yield from self._yield_matches(
            current_arg,
            self._values_for_completion(completion),
            self._meta_for_completion(completion),
        )

    def _values_for_completion(self, completion: ArgCompletionSpec) -> Iterable[str]:
        """Resolve completion values from a command metadata source."""
        if completion.source is CompletionSource.COMMAND:
            return sorted(self.registry)

        if completion.source is CompletionSource.CONTACT:
            return sorted(self.book.keys())

        if completion.source is CompletionSource.NOTE:
            return sorted(self.notes.keys())

        if completion.source is CompletionSource.CHOICES:
            return completion.values

        return ()

    def _meta_for_completion(self, completion: ArgCompletionSpec) -> str:
        """Return display metadata for completion items."""
        if completion.source is CompletionSource.COMMAND:
            return "Command"

        if completion.source is CompletionSource.CONTACT:
            return "Contact name"

        if completion.source is CompletionSource.NOTE:
            return "Note name"

        if completion.source is CompletionSource.CHOICES:
            return "Suggested value"

        return ""

    def _yield_matches(
        self,
        prefix: str,
        values: Iterable[str],
        meta: str,
    ) -> Iterable[Completion]:
        """Yield case-insensitive string matches for one argument position."""
        normalized_prefix = prefix.lower()

        for value in values:
            if not value.lower().startswith(normalized_prefix):
                continue

            yield Completion(
                value,
                start_position=-len(prefix),
                display_meta=meta,
            )


def create_prompt_session(
    book: AddressBook,
    notes: Notes,
    registry: dict[str, Callable[..., CommandResult]],
) -> PromptSession:
    """Build a prompt session with in-memory history and CLI completion."""
    return PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        completer=AssistantCompleter(book, notes, registry),
        complete_while_typing=True,
    )
