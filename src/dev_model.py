from __future__ import annotations

import abc
import enum

import attrs


@attrs.define(kw_only=True, frozen=True)
class BookID:
    isbn: str


@attrs.define(kw_only=True, frozen=True)
class BookDescription:
    title: str
    author: str
    annotation: str


@attrs.define(kw_only=True, frozen=True)
class ReaderID:
    id: int


class Reader:
    def __init__(self, reader_id: ReaderID):
        self.reader_id = reader_id


class Book:
    def __init__(self, book_id: BookID, book_description: BookDescription) -> None:
        self.book_id = book_id
        self.book_description = book_description

    def update_book_description(self, book_description: BookDescription) -> None:
        self.book_description = book_description


class Location(enum.Enum):
    IN_RESERVE = enum.auto()
    ON_SHOWCASE = enum.auto()
    RESERVED_FOR_LOAN = enum.auto()
    ON_LOAN = enum.auto()


class LocationChangeError(Exception):
    pass


class LocationState(abc.ABC):
    def move_to_showcase(self):
        raise LocationChangeError()

    def remove_from_showcase(self):
        raise LocationChangeError()

    def reserve_for_loan(self, reader_id: ReaderID):
        raise LocationChangeError()

    def cancel_loan_reservation(self, reader_id: ReaderID):
        raise LocationChangeError()

    def loan_reserved_book(self, reader_id: ReaderID):
        raise LocationChangeError()

    def end_loan(self, reader_id: ReaderID):
        raise LocationChangeError()


class InReserveLocationState(LocationState):
    def __init__(self, book_location: BookLocation):
        self.book_location = book_location

    def move_to_showcase(self):
        self.book_location.set_location_state(location=Location.ON_SHOWCASE)


class OnShowcaseLocationState(LocationState):
    def __init__(self, book_location: BookLocation):
        self.book_location = book_location

    def remove_from_showcase(self):
        self.book_location.set_location_state(location=Location.IN_RESERVE)

    def reserve_for_loan(self, reader_id: ReaderID):
        self.book_location.set_holder(holder=reader_id)
        self.book_location.set_location_state(location=Location.RESERVED_FOR_LOAN)


class ReservedForLoanLocationState(LocationState):
    def __init__(self, book_location: BookLocation):
        self.book_location = book_location

    def cancel_loan_reservation(self, reader_id: ReaderID):
        if reader_id == self.book_location.holder:
            self.book_location.clear_holder()
            self.book_location.set_location_state(location=Location.ON_SHOWCASE)
        else:
            super().cancel_loan_reservation(reader_id=reader_id)

    def loan_reserved_book(self, reader_id: ReaderID):
        if reader_id == self.book_location.holder:
            self.book_location.set_location_state(location=Location.ON_LOAN)
        else:
            super().loan_reserved_book(reader_id)


class OnLoanLocationState(LocationState):
    def __init__(self, book_location: BookLocation):
        self.book_location = book_location

    def end_loan(self, reader_id: ReaderID):
        if reader_id == self.book_location.holder:
            self.book_location.clear_holder()
            self.book_location.set_location_state(location=Location.IN_RESERVE)
        else:
            super().end_loan(reader_id)


class BookLocation:
    def __init__(self, book_id: BookID):
        self.book_id = book_id
        self.states = {
            Location.IN_RESERVE: InReserveLocationState(book_location=self),
            Location.ON_SHOWCASE: OnShowcaseLocationState(book_location=self),
            Location.ON_LOAN: OnLoanLocationState(book_location=self),
            Location.RESERVED_FOR_LOAN: ReservedForLoanLocationState(book_location=self),
        }
        self.state = self.states[Location.IN_RESERVE]
        self.holder: ReaderID | None = None

    def set_location_state(self, location: Location):
        self.state = self.states[location]

    def move_to_showcase(self):
        self.state.move_to_showcase()

    def remove_from_showcase(self):
        self.state.remove_from_showcase()

    def reserve_for_loan(self, reader_id: ReaderID):
        self.state.reserve_for_loan(reader_id=reader_id)

    def cancel_loan_reservation(self, reader_id: ReaderID):
        self.state.cancel_loan_reservation(reader_id=reader_id)

    def loan_reserved_book(self, reader_id: ReaderID):
        self.state.loan_reserved_book(reader_id=reader_id)

    def end_loan(self, reader_id: ReaderID):
        self.state.end_loan(reader_id=reader_id)

    def set_holder(self, holder: ReaderID):
        self.holder = holder

    def clear_holder(self):
        self.holder = None


class Library:
    def __init__(self):
        self.books: dict[BookID, Book] = {}
        self.locations: dict[BookID, BookLocation] = {}
        self.readers: dict[ReaderID, Reader] = {}

    def register_book(self, book: Book):
        self.books[book.book_id] = book
        self.locations[book.book_id] = BookLocation(book_id=book.book_id)

    def get_book(self, book_id: BookID) -> Book:
        return self.books[book_id]

    def get_book_location(self, book_id: BookID) -> BookLocation:
        return self.locations[book_id]

    def register_reader(self, reader: Reader):
        self.readers[reader.reader_id] = reader

    def get_reader(self, reader_id: ReaderID) -> Reader:
        return self.readers[reader_id]
