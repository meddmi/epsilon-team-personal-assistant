"""
Module for the help command
"""
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from dto import CommandResult, CommandContext
from registry import (
    CommandSpec,
    CompletionSource,
    completion_source,
    get_command_spec,
    get_command_specs,
    register_command,
)


def _style_usage_text(usage: str) -> Text:
    """Return styled usage text with highlighted argument placeholders."""
    usage_text = Text(usage, style="bold green")
    usage_text.highlight_regex(r"<[^>]+>", style="bold cyan")
    usage_text.highlight_regex(r"\[[^\]]+\]", style="bold yellow")
    usage_text.highlight_regex(r"--[\w-]+(?:=\S+)?", style="cyan")
    return usage_text


def _build_help_message() -> RenderableType:
    """Return formatted help for the whole CLI."""
    grouped_specs: dict[str, list[CommandSpec]] = {}
    for spec in get_command_specs().values():
        grouped_specs.setdefault(spec.category, []).append(spec)

    sections: list[RenderableType] = []
    for category in sorted(grouped_specs):
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=None,
            expand=True,
            pad_edge=False,
        )
        table.add_column("Usage", ratio=2)
        table.add_column("Description", ratio=3, style="white")

        for spec in sorted(grouped_specs[category], key=lambda item: item.name):
            table.add_row(_style_usage_text(spec.usage), spec.description)

        sections.append(
            Panel(
                table,
                title=category.title(),
                title_align="left",
                border_style="blue",
            )
        )

    sections.append(
        Text(
            "Use 'help [command]' to see details for one command.",
            style="italic cyan",
        )
    )
    return Group(*sections)


def _build_detailed_help_message(command_name: str) -> RenderableType:
    """Return formatted help for one command."""

    spec = get_command_spec(command_name)
    if spec is None:
        return Text(f"Command '{command_name}' not found", style="bold red")

    details = Table.grid(padding=(0, 1))
    details.add_column(style="bold cyan", no_wrap=True)
    details.add_column(style="white")
    details.add_row("Command", spec.name)
    details.add_row("Category", spec.category)
    details.add_row("Usage", _style_usage_text(spec.usage))
    details.add_row("Description", spec.description)

    return Panel(
        details,
        title=f"Help: {spec.name}",
        title_align="left",
        border_style="blue",
    )

@register_command(
    "help",
    usage="help [command]",
    description="Show all commands or detailed help for one command",
    category="system",
    arg_completions=(completion_source(CompletionSource.COMMAND),),
)
def help_command(context: CommandContext) -> CommandResult:
    """Show available commands."""
    command_name = context.args[0].lower() if context.args else None
    message = _build_detailed_help_message(command_name) if command_name else _build_help_message()
    return CommandResult(message)
