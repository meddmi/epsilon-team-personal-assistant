"""
Module for the help command
"""
from dto import CommandResult, CommandContext
from registry import (
    CompletionSource,
    completion_source,
    get_command_spec,
    get_command_specs,
    register_command,
)


def _build_help_message() -> str:
    """Return formatted help for one command or the whole CLI."""
    grouped_specs: dict[str, list] = {}
    for spec in get_command_specs().values():
        grouped_specs.setdefault(spec.category, []).append(spec)

    lines = ["Available commands:"]
    for category in sorted(grouped_specs):
        lines.append(f"\n{category.title()}:")
        for spec in sorted(grouped_specs[category], key=lambda item: item.name):
            lines.append(f"  {spec.usage}")

    lines.append("\nUse 'help [command]' to see details for one command.")
    return "\n".join(lines)

def _build_detailed_help_message(command_name: str) -> str:
    """Return formatted help for one command or the whole CLI."""

    spec = get_command_spec(command_name)
    if spec is None:
        return f"Command '{command_name}' not found"

    return "\n".join([
        f"Command: {spec.name}",
        f"Category: {spec.category}",
        f"Usage: {spec.usage}",
        f"Description: {spec.description}",
    ])

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
