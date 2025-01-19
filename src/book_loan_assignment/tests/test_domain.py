import datetime
from unittest import TestCase


class ApproveBookLoanTestCase(TestCase):
    def setUp(self):
        ...

    def test_cannot_assign_book_due_to_age_restriction(self):
        book_age_restriction = Age(years=18)
        current_date = datetime.date.today()
        reader_birthday = current_date - book_age_restriction + datetime.timedelta(days=1)
        book = self.create_book(age_restriction=book_age_restriction)
        reader_activity_approval_process = self.create_reader_activity_approval_process(reader_birthday=reader_birthday)
        reader_activity_approval_process.approve_book_loan(book=book)
        [event] = reader_activity_approval_process.events()
        self.assertNotIn(book, reader_activity_approval_process.approved_book_loans())
        self.assertEqual(
            event,
            BookLoanRejected(
                book_id=book.id(),
                reader_id=reader_activity_approval_process.reader_id()
            )
        )

    def test_cannot_assign_book_due_to_low_rating(self):
        min_rating_to_loan = Rating(scores=80)
        reader_rating = min_rating_to_loan - Rating(scores=40)
        book = self.create_book(min_rating_to_loan=min_rating_to_loan)
        reader_activity_approval_process = self.create_reader_activity_approval_process(reader_rating=reader_rating)
        reader_activity_approval_process.approve_book_loan(book=book)
        self.assertNotIn(book, reader_activity_approval_process.approved_book_loans())
        self.assertEqual(
            event,
            BookLoanRejected(
                book_id=book.id(),
                reader_id=reader_activity_approval_process.reader_id()
            )
        )

    def test_cannot_assign_book_due_to_max_books_limit(self):
        max_books_limit = 5
        book = self.create_book()
        reader_activity_approval_process = self.create_reader_activity_approval_process(assigned_book_count=max_books_limit)
        reader_activity_approval_process.approve_book_loan(book=book)
        self.assertNotIn(book, reader_activity_approval_process.approved_book_loans())
        self.assertEqual(
            event,
            BookLoanRejected(
                book_id=book.id(),
                reader_id=reader_activity_approval_process.reader_id()
            )
        )

    def test_can_assign_book_when_conditions_met(self):
        book_age_restriction = Age(years=18)
        min_rating_to_loan = Rating(scores=80)
        max_books_limit = 5
        current_date = datetime.date.today()
        reader_birthday = current_date - book_age_restriction - datetime.timedelta(days=1)
        reader_rating = min_rating_to_loan + Rating(scores=40)
        book = self.create_book(
            age_restriction=book_age_restriction,
            min_rating_to_loan=min_rating_to_loan,
        )
        reader_activity_approval_process = self.create_reader_activity_approval_process(
            assigned_book_count=max_books_limit - 1,
            reader_birthday=reader_birthday,
            reader_rating=reader_rating
        )
        reader_activity_approval_process.approve_book_loan(book=book)
        [event] = reader_activity_approval_process.events()
        self.assertIn(book, reader_activity_approval_process.approved_book_loans())
        self.assertEqual(
            event,
            BookLoanApproved(
                book_id=book.id(),
                reader_id=reader_activity_approval_process.reader_id()
            )
        )
