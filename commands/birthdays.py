"""
Module for the contact' birthday related commands:
- add-birthday
- show-birthday
- birthdays
"""
from registry import CompletionSource, completion_choices, completion_source, register_command
from commands.utils import input_error, validate_command_args, parse_named_args
from exceptions import ContactError
from dto import CommandResult, CommandContext


@register_command(
    "add-birthday",
    usage="add-birthday [name] [DD.MM.YYYY]",
    description="Add or update a birthday for a contact",
    category="contacts",
    arg_completions=(completion_source(CompletionSource.CONTACT),),
)
@input_error
def add_birthday(context: CommandContext) -> CommandResult:
    """Add or update a birthday to an existing contact by name."""
    validate_command_args(
        context.command,
        context.args,
        2,
    )

    name, birthday, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    record.add_birthday(birthday)
    return CommandResult(message="Birthday added")

@register_command(
    "show-birthday",
    usage="show-birthday [name]",
    description="Show the birthday for one contact",
    category="contacts",
    arg_completions=(completion_source(CompletionSource.CONTACT),),
)
@input_error
def show_birthday(context: CommandContext) -> CommandResult:
    """Show the birthday of a contact by name."""
    validate_command_args(context.command, context.args, 1)

    name, *_ = context.args
    record = context.book.find(name)

    if record is None:
        raise ContactError("Contact not found")

    birthday = record.birthday
    message = "Birthday has not been provided" if birthday is None else birthday.format()
    return CommandResult(message=message)

@register_command(
    "birthdays",
    usage="birthdays [--days=7]",
    description="Show contacts with upcoming birthdays",
    category="contacts",
    arg_completions=(completion_choices("--days=7", "--days=14", "--days=30"),),
)
@input_error
def birthdays(context: CommandContext) -> CommandResult:
    """Show upcoming birthdays within the next 7 days."""
    _, options = parse_named_args(context.args)
    days = int(options.get("days", 7))

    upcoming_birthdays = context.book.get_upcoming_birthdays(days)

    if not upcoming_birthdays:
        return CommandResult(message="No upcoming birthdays")

    message = "\n".join(
        f"{item['name']}: birthday {item['birthday']}, congratulate on {item['congratulation_date']}"
        for item in upcoming_birthdays
    )
    return CommandResult(message=message)
