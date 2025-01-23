import abc
import datetime
from collections.abc import Iterator, Iterable

import attrs


class Event(abc.ABC):
    pass


@attrs.define(kw_only=True, frozen=True)
class BookLoanRejected(Event):
    book_id = attrs.field()
    reader_id = attrs.field()


@attrs.define(kw_only=True, frozen=True)
class BookLoanApproved(Event):
    book_id = attrs.field()
    reader_id = attrs.field()


@attrs.define(kw_only=True, frozen=True, order=True)
class Age:
    _years: int = attrs.field(validator=[attrs.validators.ge(0)])

    @classmethod
    def from_birthday(cls, birthday: datetime.date):
        current_date = datetime.date.today()
        years_sub = current_date.year - birthday.year
        if birthday.replace(year=current_date.year) > current_date:
            years_sub -= 1
        return cls(years=years_sub)

    def __rsub__(self, other):
        if isinstance(other, datetime.date):
            return other.replace(year=other.year - self._years)
        return NotImplemented


@attrs.define(kw_only=True, frozen=True, order=True)
class Rating:
    scores: int = attrs.field(validator=[attrs.validators.ge(0), attrs.validators.le(100)])

    def __sub__(self, other):
        if isinstance(other, Rating):
            return Rating(scores=max([self.scores - other.scores, 0]))
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, Rating):
            return Rating(scores=min([other.scores + self.scores, 100]))
        return NotImplemented


@attrs.define(kw_only=True, frozen=True)
class BookId:
    identifier: int = attrs.field()


@attrs.define(kw_only=True, frozen=True)
class Book:
    book_id: BookId = attrs.field()
    age_restriction: Age = attrs.field()
    min_rating_to_loan: Rating = attrs.field()


@attrs.define(kw_only=True, frozen=True)
class ReaderId:
    identifier: int = attrs.field()


class ReaderActivityApprovalProcess:
    MAX_BOOKS_LIMIT = 5

    def __init__(self, reader_id: ReaderId, rating: Rating, birthday: datetime, approved_book_loans: Iterable[Book]):
        self._reader_id = reader_id
        self._rating = rating
        self._birthday = birthday
        self._events = []
        self._approved_book_loans = list(approved_book_loans)

    def approve_book_loan(self, book):
        if all([
            self._rating >= book.min_rating_to_loan,
            Age.from_birthday(self._birthday) >= book.age_restriction,
            len(self._approved_book_loans) < self.MAX_BOOKS_LIMIT
        ]):
            self._approved_book_loans.append(book)
            self._events.append(
                BookLoanApproved(
                    book_id=book.book_id,
                    reader_id=self._reader_id
                )
            )
        else:
            self._events.append(
                BookLoanRejected(
                    book_id=book.book_id,
                    reader_id=self._reader_id
                )
            )

    def events(self) -> Iterator[Event]:
        return (i for i in self._events)

    def approved_book_loans(self) -> Iterator[Book]:
        return (i for i in self._approved_book_loans)

    def reader_id(self):
        return self._reader_id
