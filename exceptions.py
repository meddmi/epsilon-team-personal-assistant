"""Module for exceptions in the application."""

class ContactError(Exception):
    """Base user-facing record error."""

class CommandError(Exception):
    """Base command error."""

class NoteError(Exception):
    """Base user-facing note error."""
