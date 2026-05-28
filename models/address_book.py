"""Address book collection model."""
from collections import UserDict
from datetime import date, datetime, timedelta
from typing import Optional

from models.record import Record
from exceptions import ContactError


class AddressBook(UserDict[str, Record]):
    """Represents the address book, which is a collection of records."""

    def add_record(self, record: Record) -> bool:
        """Add a record to the address book.
        :param record: the Record object to add
        :return: True if added, False otherwise
        """
        if record.name.value in self.data:
            return False

        self.data[record.name.value] = record
        return True

    def find(self, name: str) -> Optional[Record]:
        """Find a record by name.
        :param name: the name of the record to find
        :return: Record object if found, else None
        """
        return self.data.get(name)

    def search(self, query: str) -> list[Record]:
        """
        Search contacts by name or phone.

        :param query: text to search for
        :return: list of matching records
        """
        normalized_query = query.strip().lower()
        results = []

        for record in self.data.values():
            searchable_values = [
                record.name.value.lower(),
                *(phone.value for phone in record.phones),
            ]

            if any(normalized_query in value for value in searchable_values):
                results.append(record)

        return results

    def delete(self, name: str) -> None:
        """
        Delete a record by name.
        :param name: the name of the record to delete
        :return: None
        """
        if name in self.data:
            del self.data[name]
            return

        raise ContactError("Contact not found")

    def get_upcoming_birthdays(self, days: int = 7) -> list[dict[str, str]]:
        """
        Find contacts who should be congratulated within the next days.
        If a birthday falls on Saturday or Sunday, the congratulation date is moved
        to the following Monday.
        :return: list of dictionaries with 'name' and 'congratulation_date' keys
        for records with birthdays in the next 7 days
        """

        def get_birthday_for_year(birthday: date, year: int) -> date:
            """Get the next birthday date for a given year, handling leap years."""
            try:
                return birthday.replace(year=year)
            except ValueError:
                return birthday.replace(year=year, day=28)

        def shift_to_weekday(date_obj: date) -> date:
            """Shift weekend dates to next Monday."""
            weekday = date_obj.weekday()

            return date_obj + timedelta(days=7 - weekday) if weekday >= 5 else date_obj

        today = datetime.today().date()
        results = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value

            next_birthday = get_birthday_for_year(birthday, today.year)

            if next_birthday < today:
                next_birthday = get_birthday_for_year(birthday, today.year + 1)

            days_difference = (next_birthday - today).days

            if 0 <= days_difference <= days:
                celebration_day = shift_to_weekday(next_birthday)
                user_to_congratulate = {
                    "name": record.name.value,
                    "birthday": birthday.strftime("%d.%m.%Y"),
                    "congratulation_date": celebration_day.strftime("%d.%m.%Y"),
                }
                results.append(user_to_congratulate)

        return results

    def __str__(self) -> str:
        records = "\n".join(str(record) for record in self.values())
        return f"AddressBook:\nTotal records: {len(self)}\n{records}"
