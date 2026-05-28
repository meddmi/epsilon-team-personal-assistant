# epsilon-team-personal-assistant

A command-line personal assistant for managing contacts and notes. Developed as final project of the Neoversity Python course.

## Requirements

- Python 3.10+
- `prompt_toolkit`
- `rich`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

If you use the local virtual environment:

```bash
.venv/bin/python main.py
```

## Data Persistence

- The address book is loaded automatically when the application starts.
- The current state is saved automatically when the application exits.
- Data is stored in a local pickle file named `.addressbook.pkl`.
- If the storage file does not exist or cannot be read, the application starts
  with an empty data.

## Available Commands

| Command | Description |
| --- | --- |
| `hello` | Show a greeting. |
| `add [name] [phone]` | Add a contact or add a phone to an existing contact. |
| `change [name] [old phone] [new phone]` | Change a phone number. |
| `delete [name]` | Delete a contact. |
| `remove-phone [name] [phone]` | Remove one phone number from a contact. |
| `contact [name]` | Show the full contact card. |
| `all` | Show all contacts. |
| `search [query]` | Search contacts by name or phone. Show full contact card |
| `add-birthday [name] [DD.MM.YYYY]` | Add or update birthday. |
| `show-birthday [name]` | Show birthday for one contact. |
| `birthdays [--days=7]` | Show upcoming birthdays. |
| `help [command]` | Show all commands or detailed help for one command. |
| `close` or `exit` | Close the app. |

## Validation Rules

- Phone numbers must contain 10 digits after normalization.
- Birthdays must use `DD.MM.YYYY`.

## Notes

Commands are separated into modules instead of being handled by one long
`if/elif` chain. Contact commands, system commands, and help output live in
separate modules. Each command module registers handlers with
`@register_command`, and `main.py` loads command modules dynamically on startup.

The application uses `AddressBookStorage` as a context manager, which loads the
saved address book before the CLI loop starts and saves it again after the loop
finishes.
