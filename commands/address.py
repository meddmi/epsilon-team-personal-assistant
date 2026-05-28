"""
Module for the contact address related commands:
- add-address
- remove-address
- change-address
"""
from registry import register_command
from commands.utils import input_error, validate_command_args
from exceptions import ContactError
from dto import CommandResult, CommandContext


@register_command(
    "add-address",
    usage='add-address [name] [address]',
    description="Add an address to existing contact",
    category="contacts",
)

@input_error
def add_address(context: CommandContext) -> CommandResult:
    """Add a new address to existing contact."""
    validate_command_args(context.command, context.args, 2)

    name, address, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    record.add_address(address)

    return CommandResult(message="Contact updated")


@register_command(
    "change-address",
    usage="change-address [name] [old address] [new address]",
    description="Change an existing address for a contact",
    category="contacts",
)

@input_error
def change_address(context: CommandContext) -> CommandResult:
    """Change the address of an existing contact."""
    validate_command_args(context.command, context.args, 2)

    name, new_address, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    record.change_address(new_address)
    return CommandResult(message="Contact updated")

@register_command(
    "remove-address",
    usage="remove-address [name] [address]",
    description="Remove one address from a contact",
    category="contacts",
)

@input_error
def remove_address(context: CommandContext) -> CommandResult:
    """Delete an address from contact."""
    validate_command_args(context.command, context.args, 1)

    name, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    record.remove_address()
    return CommandResult(message="Address removed")