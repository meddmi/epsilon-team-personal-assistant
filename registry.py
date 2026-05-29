"""Module for command registry management."""
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from dto import CommandResult, CommandContext


class CompletionSource(Enum):
    """Supported sources for command argument completion."""

    COMMAND = "command"
    CONTACT = "contact"
    NOTE = "note"
    CHOICES = "choices"


@dataclass(frozen=True, slots=True)
class ArgCompletionSpec:
    """Describe how one positional CLI argument should be completed."""

    source: CompletionSource
    values: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CommandSpec:
    """Metadata and handler for one CLI command."""

    name: str
    handler: Callable[[CommandContext], CommandResult]
    usage: str
    description: str
    category: str = "general"
    arg_completions: tuple[ArgCompletionSpec, ...] = ()


_registry: dict[str, Callable[[CommandContext], CommandResult]] = {}
_command_specs: dict[str, CommandSpec] = {}


def completion_source(source: CompletionSource) -> ArgCompletionSpec:
    """Build a completion spec backed by a named dynamic source."""
    return ArgCompletionSpec(source=source)


def completion_choices(*values: str) -> ArgCompletionSpec:
    """Build a completion spec backed by a fixed list of values."""
    return ArgCompletionSpec(source=CompletionSource.CHOICES, values=values)


def register_command(
    name: str,
    *,
    usage: str | None = None,
    description: str | None = None,
    category: str = "general",
    arg_completions: tuple[ArgCompletionSpec, ...] = (),
):
    """Decorator to register a command and its metadata in the registry."""

    def decorator(func: Callable[[CommandContext], CommandResult]):
        _registry[name] = func
        _command_specs[name] = CommandSpec(
            name=name,
            handler=func,
            usage=usage or name,
            description=description or (func.__doc__ or "").strip() or name,
            category=category,
            arg_completions=arg_completions,
        )
        return func

    return decorator


def get_registry() -> dict[str, Callable[[CommandContext], CommandResult]]:
    """Get a copy of the handler registry."""
    return _registry.copy()


def get_command_specs() -> dict[str, CommandSpec]:
    """Get a copy of command metadata."""
    return _command_specs.copy()


def get_command_spec(name: str) -> CommandSpec | None:
    """Get metadata for a specific command."""
    return _command_specs.get(name)
