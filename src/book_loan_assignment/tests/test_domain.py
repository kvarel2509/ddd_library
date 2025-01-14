import datetime
from unittest import TestCase

from ..domain.model import AgeRestriction


class BookLoanAssignmentProcessTestCase(TestCase):
    def setUp(self):
        ...

    def test_cannot_assign_book_due_to_age_restriction(self):
        book_age_restriction = AgeRestriction(min=18)
        current_date = datetime.date.today()
        reader_birthdate = current_date.replace(year=current_date.year - age_restriction.min + 1)
        book = self.create_book(age_restriction=book_age_restriction)
        book_loan_assignment_process = self.create_book_loan_assignment_process(reader_birthdate=reader_birthdate)
        with self.assertRaises(AgeRestrictionError):
            book_loan_assignment_process.assign_book(book=book)

    def test_cannot_assign_book_due_to_low_rating(self):
        min_rating_to_loan = Rating(scores=80)
        reader_rating = min_rating_to_loan - Rating(scores=40)
        book = self.create_book(min_rating_to_loan=min_rating_to_loan)
        book_loan_assignment_process = self.create_book_loan_assignment_process(reader_rating=reader_rating)
        with self.assertRaises(LowRatingError):
            book_loan_assignment_process.assign_book(book=book)

    def test_cannot_assign_book_due_to_max_books_limit(self):
        max_books_limit = 5
        book = self.create_book()
        book_loan_assignment_process = self.create_book_loan_assignment_process(assigned_book_count=max_books_limit)
        with self.assertRaises(MaxBooksLimitExceededError):
            book_loan_assignment_process.assign_book(book=book)

    def test_can_assign_book_when_conditions_met(self):
        book_age_restriction = AgeRestriction(min=18)
        min_rating_to_loan = Rating(scores=80)
        max_books_limit = 5
        reader_birthdate = current_date.replace(year=current_date.year - age_restriction.min - 1)
        reader_rating = min_rating_to_loan + Rating(scores=40)
        book = self.create_book(
            age_restriction=book_age_restriction,
            min_rating_to_loan=min_rating_to_loan,
        )
        book_loan_assignment_process = self.create_book_loan_assignment_process(
            assigned_book_count=max_books_limit - 1,
            reader_birthdate=reader_birthdate,
            reader_rating=reader_rating
        )
        book_loan_assignment_process.assign_book(book=book)
        [event] = book_loan_assignment_process.events()
        self.assertIn(book, list(book_loan_assignment_process.assigned_books()))
        self.assertIsInstance(event, BookAssignedForLoan)
        self.assertEqual(event.book_id, book.id())
        self.assertEqual(event.reader_id, reader_loan_process.reader_id())
