"""
Module for the base contacts commands:
- add
- change
- phone
- all
"""
from rich.table import Table, box

from registry import CompletionSource, completion_source, register_command
from commands.utils import input_error, validate_command_args
from exceptions import ContactError
from dto import CommandResult, CommandContext
from models import Record


def _format_contact_value(values: list[object]) -> str:
    """Join repeated contact field values or return a placeholder."""
    return "\n".join(str(value) for value in values) or "-"


def _build_contacts_table(records: list[Record]) -> Table:
    """Build a Rich table for one or more contact records."""
    table = Table(
        header_style="bold cyan",
        box=box.SIMPLE,
        expand=True,
        pad_edge=False,
        show_lines=True,
    )
    column_style = "green"
    table.add_column("Name", style=column_style)
    table.add_column("Birthday", style=column_style)
    table.add_column("Phones", style=column_style)
    table.add_column("Emails", style=column_style)
    table.add_column("Address", style=column_style)

    for record in records:
        table.add_row(
            record.name.value,
            record.birthday.format() if record.birthday else "-",
            _format_contact_value(record.phones),
            _format_contact_value(record.emails),
            record.address.value if record.address else "-",
        )

    return table


@register_command(
    "add",
    usage='add <name> <phone>',
    description="Add a contact or append a phone to an existing contact",
    category="contacts"
)
@input_error
def add_contact(context: CommandContext) -> CommandResult:
    """Add a new contact with name and phone number to contacts."""
    validate_command_args(context.command, context.args, 2)

    name, phone, *_ = context.args
    record = context.book.find(name)
    result_message = "Contact updated"

    if record is None:
        record = Record(name)
        context.book.add_record(record)
        result_message = "Contact added"

    record.add_phone(phone)

    return CommandResult(message=result_message)

@register_command(
    "change",
    usage="change <name> <old phone> <new phone>",
    description="Change an existing phone number for a contact",
    category="contacts",
    arg_completions=(completion_source(CompletionSource.CONTACT),),
)
@input_error
def change_contact(context: CommandContext) -> CommandResult:
    """Change the phone number of an existing contact."""
    validate_command_args(
        context.command,
        context.args,
        3,
    )

    name, old_phone, new_phone, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    record.edit_phone(old_phone, new_phone)
    return CommandResult(message="Contact updated")

@register_command(
    "delete",
    usage="delete <name>",
    description="Delete a contact by name",
    category="contacts",
    arg_completions=(completion_source(CompletionSource.CONTACT),),
)
@input_error
def delete_contact(context: CommandContext) -> CommandResult:
    """Delete a contact by name from contacts."""
    validate_command_args(
        context.command,
        context.args,
        1,
    )

    name, *_ = context.args
    context.book.delete(name)
    return CommandResult(message="Contact deleted")

@register_command(
    "remove-phone",
    usage="remove-phone <name> <phone>",
    description="Remove one phone number from a contact",
    category="contacts",
    arg_completions=(completion_source(CompletionSource.CONTACT),),
)
@input_error
def remove_phone(context: CommandContext) -> CommandResult:
    """Delete a phone number from contact."""
    validate_command_args(
        context.command,
        context.args,
        2,
    )

    name, phone, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    record.remove_phone(phone)
    return CommandResult(message="Phone removed")

@register_command(
    "contact",
    usage="contact <name>",
    description="Show the full contact card by name",
    category="contacts",
    arg_completions=(completion_source(CompletionSource.CONTACT),),
)
@input_error
def show_contact(context: CommandContext) -> CommandResult:
    """Show the contact info by name."""
    validate_command_args(context.command, context.args, 1)

    name, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    return CommandResult(message=_build_contacts_table([record]))


@register_command(
    "search",
    usage="search <query>",
    description="Search contacts by name or phone",
    category="contacts",
)
@input_error
def search_contacts(context: CommandContext) -> CommandResult:
    """Search contacts by name, address, phone, or email."""
    validate_command_args(context.command, context.args, 1)

    query = " ".join(context.args).strip()
    matches = context.book.search(query)

    if not matches:
        return CommandResult(message="No matching contacts found")

    return CommandResult(message=_build_contacts_table(matches))

@register_command(
    "all",
    usage="all",
    description="Show all contacts",
    category="contacts",
)
@input_error
def show_all(context: CommandContext) -> CommandResult:
    """Show all contacts in the format: {name}: {phone}."""
    if not context.book:
        return CommandResult(message="No contacts found")

    records = list(context.book.values())
    records.sort(key=lambda record: record.name.value.lower())
    return CommandResult(message=_build_contacts_table(records))
