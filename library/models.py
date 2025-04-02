#!/usr/bin/env python3
# Library Management System - Models

from datetime import datetime, timedelta
import uuid


class Book:
    """Represents a book in the library."""

    def __init__(self, title, author, isbn, publisher=None, year=None, copies=1):
        self.id = str(uuid.uuid4())
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher
        self.year = year
        self.total_copies = copies
        self.available_copies = copies

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"

    def to_dict(self):
        """Convert book to dictionary for storage."""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'publisher': self.publisher,
            'year': self.year,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Book instance from dictionary data."""
        book = cls(
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            publisher=data.get('publisher'),
            year=data.get('year'),
            copies=data.get('total_copies', 1)
        )
        book.id = data['id']
        book.available_copies = data.get('available_copies', book.total_copies)
        return book


class User:
    """Represents a user of the library."""

    def __init__(self, username, password, name, email=None, role='member'):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password = password  # Note: In production, this should be hashed
        self.name = name
        self.email = email
        self.role = role  # member, librarian, admin
        self.registered_date = datetime.now().strftime("%Y-%m-%d")

    def __str__(self):
        return f"{self.name} ({self.username})"

    def to_dict(self):
        """Convert user to dictionary for storage."""
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'registered_date': self.registered_date
        }

    @classmethod
    def from_dict(cls, data):
        """Create a User instance from dictionary data."""
        user = cls(
            username=data['username'],
            password=data['password'],
            name=data['name'],
            email=data.get('email'),
            role=data.get('role', 'member')
        )
        user.id = data['id']
        user.registered_date = data.get('registered_date', user.registered_date)
        return user


class Transaction:
    """Represents a book transaction (issue/return)."""

    def __init__(self, book_id, user_id, transaction_type='issue', days=14):
        self.id = str(uuid.uuid4())
        self.book_id = book_id
        self.user_id = user_id
        self.transaction_type = transaction_type  # issue or return
        self.transaction_date = datetime.now()
        self.due_date = self.transaction_date + timedelta(days=days) if transaction_type == 'issue' else None
        self.return_date = None
        self.fine = 0.0

    def __str__(self):
        transaction_info = f"{self.transaction_type.capitalize()} on {self.transaction_date.strftime('%Y-%m-%d')}"
        if self.transaction_type == 'issue':
            transaction_info += f", Due: {self.due_date.strftime('%Y-%m-%d')}"
        if self.return_date:
            transaction_info += f", Returned: {self.return_date.strftime('%Y-%m-%d')}"
        if self.fine > 0:
            transaction_info += f", Fine: ${self.fine:.2f}"
        return transaction_info

    def is_overdue(self):
        """Check if a transaction is overdue."""
        if self.transaction_type == 'issue' and not self.return_date:
            return datetime.now() > self.due_date
        return False

    def calculate_fine(self, fine_per_day=0.50):
        """Calculate fine for overdue books."""
        if self.is_overdue():
            days_overdue = (datetime.now() - self.due_date).days
            self.fine = days_overdue * fine_per_day
        return self.fine

    def to_dict(self):
        """Convert transaction to dictionary for storage."""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
            'due_date': self.due_date.strftime("%Y-%m-%d %H:%M:%S") if self.due_date else None,
            'return_date': self.return_date.strftime("%Y-%m-%d %H:%M:%S") if self.return_date else None,
            'fine': self.fine
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Transaction instance from dictionary data."""
        transaction = cls(
            book_id=data['book_id'],
            user_id=data['user_id'],
            transaction_type=data['transaction_type']
        )
        transaction.id = data['id']
        transaction.transaction_date = datetime.strptime(data['transaction_date'], "%Y-%m-%d %H:%M:%S")
        if data['due_date']:
            transaction.due_date = datetime.strptime(data['due_date'], "%Y-%m-%d %H:%M:%S")
        if data['return_date']:
            transaction.return_date = datetime.strptime(data['return_date'], "%Y-%m-%d %H:%M:%S")
        transaction.fine = data['fine']
        return transaction
