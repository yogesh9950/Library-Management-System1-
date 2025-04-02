#!/usr/bin/env python3
# Library Management System - Library Service

from datetime import datetime
from .models import Book, Transaction


class LibraryService:
    """Provides library functionality like book management and transactions."""

    def __init__(self, data_handler, auth):
        """Initialize the library service."""
        self.data_handler = data_handler
        self.auth = auth

    # Book management methods
    def add_book(self, title, author, isbn, publisher=None, year=None, copies=1):
        """Add a new book to the library."""
        if not self.auth.is_librarian():
            return False, "Only librarians can add books."

        # Check if book with same ISBN already exists
        books = self.data_handler.search_books(isbn, 'isbn')
        if books:
            # If the book exists, increase the number of copies
            book = books[0]
            book.total_copies += copies
            book.available_copies += copies
            self.data_handler.update_book(book)
            return True, f"Added {copies} copies of existing book: {book.title}"

        # Create and save a new book
        book = Book(title, author, isbn, publisher, year, copies)
        self.data_handler.add_book(book)
        return True, f"Added new book: {title}"

    def remove_book(self, book_id):
        """Remove a book from the library."""
        if not self.auth.is_librarian():
            return False, "Only librarians can remove books."

        # Check if the book exists
        book = self.data_handler.find_book_by_id(book_id)
        if not book:
            return False, "Book not found."

        # Check if the book is currently issued
        active_transactions = self.data_handler.get_book_transactions(book_id, active_only=True)
        if active_transactions:
            return False, "Cannot remove book that is currently issued."

        # Delete the book
        self.data_handler.delete_book(book_id)
        return True, f"Book removed: {book.title}"

    def search_books(self, query, field=None):
        """Search for books by title, author, or ISBN."""
        return self.data_handler.search_books(query, field)

    def get_all_books(self):
        """Get all books in the library."""
        return self.data_handler.get_all_books()

    # Transaction methods
    def issue_book(self, book_id, days=14):
        """Issue a book to the current user."""
        if not self.auth.is_authenticated():
            return False, "You must be logged in to issue a book."

        # Check if the book exists
        book = self.data_handler.find_book_by_id(book_id)
        if not book:
            return False, "Book not found."

        # Check if the book is available
        if book.available_copies <= 0:
            return False, "No copies of this book are available."

        # Check if the user already has this book
        user_id = self.auth.current_user.id
        active_transactions = self.data_handler.get_user_transactions(user_id, active_only=True)
        for transaction in active_transactions:
            if transaction.book_id == book_id:
                return False, "You already have this book issued."

        # Issue the book
        transaction = Transaction(book_id, user_id, transaction_type='issue', days=days)
        self.data_handler.add_transaction(transaction)

        # Update book availability
        book.available_copies -= 1
        self.data_handler.update_book(book)

        return True, f"Book issued: {book.title}"

    def return_book(self, book_id):
        """Return a book that was issued to the current user."""
        if not self.auth.is_authenticated():
            return False, "You must be logged in to return a book."

        # Check if the book exists
        book = self.data_handler.find_book_by_id(book_id)
        if not book:
            return False, "Book not found."

        # Check if the user has this book issued
        user_id = self.auth.current_user.id
        active_transactions = self.data_handler.get_user_transactions(user_id, active_only=True)
        transaction = None
        for t in active_transactions:
            if t.book_id == book_id:
                transaction = t
                break

        if not transaction:
            return False, "You do not have this book issued."

        # Mark the transaction as returned
        transaction.return_date = datetime.now()

        # Calculate any fines
        fine = transaction.calculate_fine()

        # Update the transaction
        self.data_handler.update_transaction(transaction)

        # Update book availability
        book.available_copies += 1
        self.data_handler.update_book(book)

        # Return with fine information if applicable
        if fine > 0:
            return True, f"Book returned: {book.title}. Fine: ${fine:.2f}"
        return True, f"Book returned: {book.title}"

    def get_user_books(self):
        """Get all books currently issued to the current user."""
        if not self.auth.is_authenticated():
            return [], "You must be logged in to view your books."

        user_id = self.auth.current_user.id
        active_transactions = self.data_handler.get_user_transactions(user_id, active_only=True)

        books = []
        for transaction in active_transactions:
            book = self.data_handler.find_book_by_id(transaction.book_id)
            if book:
                # Add transaction details to the book for display
                book.due_date = transaction.due_date
                book.transaction_id = transaction.id
                book.is_overdue = transaction.is_overdue()
                book.fine = transaction.calculate_fine()
                books.append(book)

        return books, None

    def get_overdue_books(self):
        """Get all overdue books (only for librarians)."""
        if not self.auth.is_librarian():
            return [], "Only librarians can view overdue books."

        overdue_transactions = self.data_handler.get_overdue_transactions()

        overdue_items = []
        for transaction in overdue_transactions:
            book = self.data_handler.find_book_by_id(transaction.book_id)
            user = self.data_handler.find_user_by_id(transaction.user_id)

            if book and user:
                overdue_items.append({
                    'transaction': transaction,
                    'book': book,
                    'user': user,
                    'fine': transaction.calculate_fine()
                })

        return overdue_items, None
