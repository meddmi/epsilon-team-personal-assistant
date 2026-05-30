"""Field value objects for address book records."""
import re
from datetime import datetime
from typing import Optional

from exceptions import ContactError


class Field:
    """Base class for fields in the address book."""

    def __init__(self, value) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Represents a name field in the address book."""

    def __init__(self, value: str) -> None:
        if not value.strip():
            raise ContactError("Name cannot be empty")

        super().__init__(value.strip())


class Birthday(Field):
    """Represents a birthday field in the address book."""
    date_format: str = "%d.%m.%Y"

    def __init__(self, value: str) -> None:
        try:
            birthday_date = datetime.strptime(str(value).strip(), Birthday.date_format).date()
            super().__init__(birthday_date)
        except ValueError as exc:
            raise ContactError("Invalid date format. Use DD.MM.YYYY") from exc

    def format(self, out_format: Optional[str] = None) -> str:
        """
        Return formatted date value.

        :param out_format: Optional output format override.
        """
        return self.value.strftime(
            out_format
            if out_format is not None
            else Birthday.date_format
        )


class Phone(Field):
    """Represents a phone number field in the address book."""

    def __init__(self, value: str) -> None:
        self.validate(value)

        super().__init__(value)

    @classmethod
    def validate(cls, value: str) -> None:
        """Validate that phone number containing only digits."""
        if not re.fullmatch(r"^\d{10}$", value):
            raise ContactError("Phone number must contain 10 digits")

class Email(Field):
    """Represents an email address field in the address book."""

    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def __init__(self, value: str) -> None:
        normalized_email = self.normalize(value)
        self.validate(normalized_email)

        super().__init__(normalized_email)

    @staticmethod
    def normalize(value: str) -> str:
        """Normalize email address."""

        if not isinstance(value, str):
            raise ContactError("Email must be a string")

        return value.strip().lower()

    @classmethod
    def validate(cls, value: str) -> None:
        """Validate email address."""

        if not cls.EMAIL_REGEX.fullmatch(value):
            raise ContactError("Invalid email format")

class Address(Field):
    """Represents an address contacts field in the address book."""

    ADDRESS_REGEX = re.compile(
        r"^[a-zA-Z0-9\s,.\-/#+]{5,100}$"
    )

    def __init__(self, value: str) -> None:
        normalized_address = self.normalize(value)
        self.validate(normalized_address)

        super().__init__(normalized_address)

    @staticmethod
    def normalize(value: str) -> str:
        """Normalize address contacts."""

        if not isinstance(value, str):
            raise ContactError("Address must be a string")

        return value.strip()

    @classmethod
    def validate(cls, value: str) -> None:
        """Validate address contats."""

        if not cls.ADDRESS_REGEX.fullmatch(value):
            raise ContactError("Invalid address format")
