"""
Module for the contact' emails related commands:
- add-email
- remove-email
- change-email
"""
from registry import CompletionSource, completion_source, register_command
from commands.utils import input_error, validate_command_args
from exceptions import ContactError
from dto import CommandResult, CommandContext


@register_command(
    "add-email",
    usage='add-email <name> <email>',
    description="Add an email to existing contact",
    category="contacts",
    arg_completions=(completion_source(CompletionSource.CONTACT),),
)
@input_error
def add_email(context: CommandContext) -> CommandResult:
    """Add a new email to existing contact."""
    validate_command_args(context.command, context.args, 2)

    name, email, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    if email is not None:
        record.add_email(email)

    return CommandResult(message="Contact updated")


@register_command(
    "change-email",
    usage="change-email <name> <old email> <new email>",
    description="Change an existing email for a contact",
    category="contacts",
    arg_completions=(completion_source(CompletionSource.CONTACT),),
)
@input_error
def change_email(context: CommandContext) -> CommandResult:
    """Change the email of an existing contact."""
    validate_command_args(
        context.command,
        context.args,
        3,
    )

    name, old_email, new_email, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    record.edit_email(old_email, new_email)
    return CommandResult(message="Contact updated")


@register_command(
    "remove-email",
    usage="remove-email <name> <email>",
    description="Remove one email from a contact",
    category="contacts",
    arg_completions=(completion_source(CompletionSource.CONTACT),),
)
@input_error
def remove_email(context: CommandContext) -> CommandResult:
    """Delete an email from contact."""
    validate_command_args(
        context.command,
        context.args,
        2,
    )

    name, email, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    record.remove_email(email)
    return CommandResult(message="Email removed")
