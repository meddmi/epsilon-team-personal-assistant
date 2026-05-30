# epsilon-team-personal-assistant

A command-line personal assistant for managing contacts and notes. Developed as final project of the Neoversity Python course.

The app stores contacts and notes locally, provides interactive command help,
and supports shell-like quoted input for multi-word arguments.

## Requirements

- Python 3.10+
- `better-profanity`
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

## CLI Input Features

- Up and down arrows cycle through commands entered in the current session.
- The prompt shows suggestions from the current session history as you type.
- `Tab` completes command names and a small set of common arguments such as
  `help` targets, contact or note names, and common `birthdays` day values.
- Command input is parsed with shell-like quoting rules, so multi-word values
  should be wrapped in quotes when needed, for example
  `add-address John "221B Baker Street"` or
  `add-note trip "Weekend plan" "Book hotel and buy tickets"`.
- The prompt and command execution use the same parsing rules, including
  best-effort handling of unfinished quoted input while typing.

## Data Persistence

- The address book is loaded automatically when the application starts.
- The current state is saved automatically when the application exits without
  an unhandled exception.
- Data is stored in a local pickle file named `.addressbook.pkl`.
- Notes are loaded and saved independently in `.notes.pkl`.
- If a storage file does not exist or cannot be read, the application starts
  with empty data.
- Older saved notes are normalized on load to backfill newer fields such as
  `name`, `title`, `text`, `created_at`, and `tags`.

## Available Commands

| Command | Description |
| --- | --- |
| `hello` | Show a greeting. |
| `help [command]` | Show all commands or detailed help for one command. |
| `close` or `exit` | Close the app. |
| `add <name> <phone>` | Add a contact or add a phone to an existing contact. |
| `change <name> <old phone> <new phone>` | Change a phone number. |
| `delete <name>` | Delete a contact. |
| `remove-phone <name> <phone>` | Remove one phone number from a contact. |
| `contact <name>` | Show the full contact card. |
| `all` | Show all contacts. |
| `search <query>` | Search contacts by name, birthday, address, phone, or email. |
| `add-email <name> <email>` | Add new email. |
| `change-email <name> <old email> <new email>` | Change an email. |
| `remove-email <name> <email>` | Remove one email from a contact. |
| `add-birthday <name> <DD.MM.YYYY>` | Add or update birthday. |
| `show-birthday <name>` | Show birthday for one contact. |
| `birthdays [days]` | Show upcoming birthdays. |
| `add-address <name> <address>` | Add new contact address. |
| `change-address <name> <new address>` | Change the contact address. |
| `remove-address <name>` | Remove address from a contact. |
| `add-note <name> <title> [text]` | Create a note. |
| `edit-note <id/name> <title> [text]` | Edit a note by id or name. |
| `delete-note <id/name>` | Delete a note by id or name. |
| `note <id/name>` | Show one note by id or name. |
| `search-notes <query>` | Search notes by name, title, or text. |
| `notes` | Show all notes. |
| `tag-sorted-notes` | Show all notes sorted by their first alphabetical tag. |
| `add-tag <name> <tag>` | Add a tag to a note. |
| `remove-tag <name> <tag>` | Remove a tag from a note. |
| `find-by-tag <tag1> [tag2] [...]` | Find notes that match any of the given tags. |

## Validation Rules

- Contact names, note names, note titles, and note text cannot be empty.
- Phone numbers must contain exactly 10 digits.
- Birthdays must use `DD.MM.YYYY`.
- Emails are normalized to lowercase and must have a valid email format.
- Addresses must be 5 to 100 characters and may contain letters, digits,
  spaces, commas, periods, slashes, hyphens, `#`, and `+`.
- Note tags are normalized to lowercase and automatically get a `#` prefix if
  missing.

## Notes Behavior

- Contact names are used as unique keys in the address book.
- Note names are also unique. If a note name already exists, the app creates a
  unique variant such as `idea(1)`.
- Note names cannot contain inappropriate words. If a note name contains an
  inappropriate word, the note is not created.
- Note titles and text are allowed to contain inappropriate words, but those
  words are censored with `*` characters when notes are displayed.
- `notes` and `find-by-tag` display notes from newest to oldest.
- `find-by-tag` currently matches notes that contain any of the supplied tags.

## Notes

Commands are separated into modules instead of being handled by one long
`if/elif` chain. Contact commands, system commands, and help output live in
separate modules. Each command module registers handlers with
`@register_command`, and `main.py` loads command modules dynamically on startup.

The application uses a shared generic `PickleStorage` base class with
specialized `AddressBookStorage` and `NotesStorage` wrappers. These storage
classes are used as context managers, loading saved data before the CLI loop
starts and saving it again after the loop finishes successfully.

## Team

- Dmytro Medvediev - [@meddmi](https://github.com/meddmi)
- Manoilov Andrii - [@ManoylovAC](https://github.com/ManoylovAC)
- Volodymyr Lysak - [@volodumurPyt1207](https://github.com/volodumurPyt1207)
- Roma Bondarchuk - [@GHIceStar](https://github.com/GHIceStar)
