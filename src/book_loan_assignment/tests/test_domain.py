import datetime
from collections.abc import Iterable
from unittest import TestCase

from src.book_loan_assignment.domain.model import Age, ReaderActivityApprovalProcess, BookLoanRejected, Book, ReaderId, \
    Rating, BookId, BookLoanApproved


class ApproveBookLoanTestCase(TestCase):
    def create_book(
            self,
            book_id: BookId = BookId(identifier=0),
            min_rating_to_loan: Rating = Rating(scores=0),
            age_restriction: Age = Age(years=0),
    ):
        return Book(
            book_id=book_id,
            min_rating_to_loan=min_rating_to_loan,
            age_restriction=age_restriction
        )

    def create_reader_activity_approval_process(
            self,
            reader_id: ReaderId = ReaderId(identifier=0),
            birthday: datetime.date = datetime.date.min,
            rating: Rating = Rating(scores=100),
            approved_book_loans: Iterable[Book] = None
    ):
        return ReaderActivityApprovalProcess(
            reader_id=reader_id,
            rating=rating,
            birthday=birthday,
            approved_book_loans=approved_book_loans or []
        )

    def test_cannot_approve_book_loan_due_to_age_restriction(self):
        book_age_restriction = Age(years=18)
        current_date = datetime.date.today()
        reader_birthday = current_date - book_age_restriction + datetime.timedelta(days=1)
        book = self.create_book(age_restriction=book_age_restriction)
        reader_activity_approval_process = self.create_reader_activity_approval_process(birthday=reader_birthday)
        reader_activity_approval_process.approve_book_loan(book=book)
        [event] = reader_activity_approval_process.events()
        self.assertNotIn(book, list(reader_activity_approval_process.approved_book_loans()))
        self.assertEqual(
            event,
            BookLoanRejected(
                book_id=book.book_id,
                reader_id=reader_activity_approval_process.reader_id()
            )
        )

    def test_cannot_approve_book_loan_due_to_low_rating(self):
        min_rating_to_loan = Rating(scores=80)
        reader_rating = min_rating_to_loan - Rating(scores=40)
        book = self.create_book(min_rating_to_loan=min_rating_to_loan)
        reader_activity_approval_process = self.create_reader_activity_approval_process(rating=reader_rating)
        reader_activity_approval_process.approve_book_loan(book=book)
        [event] = reader_activity_approval_process.events()
        self.assertNotIn(book, list(reader_activity_approval_process.approved_book_loans()))
        self.assertEqual(
            event,
            BookLoanRejected(
                book_id=book.book_id,
                reader_id=reader_activity_approval_process.reader_id()
            )
        )

    def test_cannot_approve_book_loan_due_to_max_books_limit(self):
        reader_activity_approval_process = self.create_reader_activity_approval_process(
            approved_book_loans=[
                self.create_book(book_id=BookId(identifier=i))
                for i in range(ReaderActivityApprovalProcess.MAX_BOOKS_LIMIT)
            ]
        )
        book = self.create_book(book_id=BookId(identifier=ReaderActivityApprovalProcess.MAX_BOOKS_LIMIT + 1))
        reader_activity_approval_process.approve_book_loan(book=book)
        [event] = reader_activity_approval_process.events()
        self.assertNotIn(book, list(reader_activity_approval_process.approved_book_loans()))
        self.assertEqual(
            event,
            BookLoanRejected(
                book_id=book.book_id,
                reader_id=reader_activity_approval_process.reader_id()
            )
        )

    def test_can_approve_book_loan_when_conditions_met(self):
        book_age_restriction = Age(years=18)
        current_date = datetime.date.today()
        reader_birthday = current_date - book_age_restriction - datetime.timedelta(days=1)
        min_rating_to_loan = Rating(scores=80)
        reader_rating = min_rating_to_loan + Rating(scores=40)
        book = self.create_book(
            age_restriction=book_age_restriction,
            min_rating_to_loan=min_rating_to_loan,
        )
        reader_activity_approval_process = self.create_reader_activity_approval_process(
            birthday=reader_birthday,
            rating=reader_rating
        )
        reader_activity_approval_process.approve_book_loan(book=book)
        [event] = reader_activity_approval_process.events()
        self.assertIn(book, list(reader_activity_approval_process.approved_book_loans()))
        self.assertEqual(
            event,
            BookLoanApproved(
                book_id=book.book_id,
                reader_id=reader_activity_approval_process.reader_id()
            )
        )
