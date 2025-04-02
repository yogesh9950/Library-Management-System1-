#!/usr/bin/env python3
# Library Management System - Data Handler

import json
import os
from datetime import datetime
from .models import Book, User, Transaction


class DataHandler:
    """Handles data operations for the Library Management System."""

    def __init__(self, data_dir="library/data"):
        """Initialize the data handler."""
        self.data_dir = data_dir
        self.books_file = os.path.join(data_dir, "books.json")
        self.users_file = os.path.join(data_dir, "users.json")
        self.transactions_file = os.path.join(data_dir, "transactions.json")

        # Create the data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

        # Create empty files if they don't exist
        for file_path in [self.books_file, self.users_file, self.transactions_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)

    def _read_data(self, file_path):
        """Read data from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_data(self, file_path, data):
        """Write data to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    # Book operations
    def get_all_books(self):
        """Get all books from the data store."""
        books_data = self._read_data(self.books_file)
        return [Book.from_dict(book_data) for book_data in books_data]

    def add_book(self, book):
        """Add a new book to the data store."""
        books_data = self._read_data(self.books_file)
        books_data.append(book.to_dict())
        self._write_data(self.books_file, books_data)

    def update_book(self, book):
        """Update an existing book in the data store."""
        books_data = self._read_data(self.books_file)
        for i, book_data in enumerate(books_data):
            if book_data['id'] == book.id:
                books_data[i] = book.to_dict()
                break
        self._write_data(self.books_file, books_data)

    def delete_book(self, book_id):
        """Delete a book from the data store."""
        books_data = self._read_data(self.books_file)
        books_data = [book_data for book_data in books_data if book_data['id'] != book_id]
        self._write_data(self.books_file, books_data)

    def find_book_by_id(self, book_id):
        """Find a book by its ID."""
        books_data = self._read_data(self.books_file)
        for book_data in books_data:
            if book_data['id'] == book_id:
                return Book.from_dict(book_data)
        return None

    def search_books(self, query, field=None):
        """Search for books by title, author, or ISBN."""
        books = self.get_all_books()
        query = query.lower()

        if not field:
            # Search in all fields
            return [book for book in books if
                    query in book.title.lower() or
                    query in book.author.lower() or
                    query in book.isbn.lower()]
        elif field == 'title':
            return [book for book in books if query in book.title.lower()]
        elif field == 'author':
            return [book for book in books if query in book.author.lower()]
        elif field == 'isbn':
            return [book for book in books if query in book.isbn.lower()]
        else:
            return []

    # User operations
    def get_all_users(self):
        """Get all users from the data store."""
        users_data = self._read_data(self.users_file)
        return [User.from_dict(user_data) for user_data in users_data]

    def add_user(self, user):
        """Add a new user to the data store."""
        users_data = self._read_data(self.users_file)
        users_data.append(user.to_dict())
        self._write_data(self.users_file, users_data)

    def update_user(self, user):
        """Update an existing user in the data store."""
        users_data = self._read_data(self.users_file)
        for i, user_data in enumerate(users_data):
            if user_data['id'] == user.id:
                users_data[i] = user.to_dict()
                break
        self._write_data(self.users_file, users_data)

    def delete_user(self, user_id):
        """Delete a user from the data store."""
        users_data = self._read_data(self.users_file)
        users_data = [user_data for user_data in users_data if user_data['id'] != user_id]
        self._write_data(self.users_file, users_data)

    def find_user_by_id(self, user_id):
        """Find a user by ID."""
        users_data = self._read_data(self.users_file)
        for user_data in users_data:
            if user_data['id'] == user_id:
                return User.from_dict(user_data)
        return None

    def find_user_by_username(self, username):
        """Find a user by username."""
        users_data = self._read_data(self.users_file)
        for user_data in users_data:
            if user_data['username'].lower() == username.lower():
                return User.from_dict(user_data)
        return None

    # Transaction operations
    def get_all_transactions(self):
        """Get all transactions from the data store."""
        transactions_data = self._read_data(self.transactions_file)
        return [Transaction.from_dict(transaction_data) for transaction_data in transactions_data]

    def add_transaction(self, transaction):
        """Add a new transaction to the data store."""
        transactions_data = self._read_data(self.transactions_file)
        transactions_data.append(transaction.to_dict())
        self._write_data(self.transactions_file, transactions_data)

    def update_transaction(self, transaction):
        """Update an existing transaction in the data store."""
        transactions_data = self._read_data(self.transactions_file)
        for i, transaction_data in enumerate(transactions_data):
            if transaction_data['id'] == transaction.id:
                transactions_data[i] = transaction.to_dict()
                break
        self._write_data(self.transactions_file, transactions_data)

    def find_transaction_by_id(self, transaction_id):
        """Find a transaction by ID."""
        transactions_data = self._read_data(self.transactions_file)
        for transaction_data in transactions_data:
            if transaction_data['id'] == transaction_id:
                return Transaction.from_dict(transaction_data)
        return None

    def get_user_transactions(self, user_id, active_only=False):
        """Get all transactions for a specific user."""
        transactions = self.get_all_transactions()
        if active_only:
            return [t for t in transactions if t.user_id == user_id and t.transaction_type == 'issue' and not t.return_date]
        return [t for t in transactions if t.user_id == user_id]

    def get_book_transactions(self, book_id, active_only=False):
        """Get all transactions for a specific book."""
        transactions = self.get_all_transactions()
        if active_only:
            return [t for t in transactions if t.book_id == book_id and t.transaction_type == 'issue' and not t.return_date]
        return [t for t in transactions if t.book_id == book_id]

    def get_overdue_transactions(self):
        """Get all overdue transactions."""
        transactions = self.get_all_transactions()
        today = datetime.now()
        overdue = []

        for t in transactions:
            if (t.transaction_type == 'issue' and
                not t.return_date and
                t.due_date):

                # Compare dates
                if isinstance(t.due_date, str):
                    due_date = datetime.strptime(t.due_date, "%Y-%m-%d %H:%M:%S")
                    if today > due_date:
                        overdue.append(t)
                elif today > t.due_date:
                    overdue.append(t)

        return overdue
