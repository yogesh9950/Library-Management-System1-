#!/usr/bin/env python3
# Library Management System - Main System

import os
import sys
from datetime import datetime

from .data_handler import DataHandler
from .auth import Authentication
from .service import LibraryService
from .models import Book, User, Transaction


class LibrarySystem:
    """Main system class that integrates all components of the Library Management System."""

    def __init__(self, data_dir="library/data"):
        """Initialize the Library Management System."""
        self.data_handler = DataHandler(data_dir)
        self.auth = Authentication(self.data_handler)
        self.library_service = LibraryService(self.data_handler, self.auth)

        # Create an admin user if none exists
        self._create_admin_if_not_exists()

        # Add sample BCA books if no books exist
        self._add_bca_books_if_empty()

    def _create_admin_if_not_exists(self):
        """Create an admin user if no users exist in the system."""
        users = self.data_handler.get_all_users()
        if not users:
            print("Creating admin user...")
            self.auth.register_user("admin", "admin123", "Administrator", role="admin")
            print("Admin user created. Username: admin, Password: admin123")

    def start(self):
        """Start the Library Management System."""
        print("\n" + "="*50)
        print("Welcome to the Library Management System".center(50))
        print("="*50 + "\n")

        while True:
            self._display_menu()
            choice = input("\nEnter your choice (1-9): ").strip()

            if choice == '1':
                self._login()
            elif choice == '2':
                self._register()
            elif choice == '3':
                self._search_books()
            elif choice == '4':
                self._view_all_books()
            elif choice == '5':
                self._issue_book()
            elif choice == '6':
                self._return_book()
            elif choice == '7':
                self._view_my_books()
            elif choice == '8':
                self._librarian_menu()
            elif choice == '9':
                print("\nThank you for using the Library Management System. Goodbye!")
                sys.exit(0)
            else:
                print("\nInvalid choice. Please try again.")

            input("\nPress Enter to continue...")

    def _display_menu(self):
        """Display the main menu of the system."""
        print("\n" + "-"*50)
        print("MAIN MENU".center(50))
        print("-"*50)

        if self.auth.is_authenticated():
            print(f"Logged in as: {self.auth.current_user.name} ({self.auth.current_user.role})")
            print("-"*50)

        print("1. Login")
        print("2. Register")
        print("3. Search Books")
        print("4. View All Books")
        print("5. Issue Book")
        print("6. Return Book")
        print("7. View My Books")

        if self.auth.is_librarian():
            print("8. Librarian Menu")

        print("9. Exit")

    def _login(self):
        """Handle user login."""
        if self.auth.is_authenticated():
            print(f"\nYou are already logged in as {self.auth.current_user.name}.")
            choice = input("Would you like to logout? (y/n): ").strip().lower()
            if choice == 'y':
                success, message = self.auth.logout()
                print(f"\n{message}")
            return

        print("\n" + "-"*50)
        print("LOGIN".center(50))
        print("-"*50)

        username = input("Username: ").strip()
        password = input("Password: ").strip()

        success, message = self.auth.login(username, password)
        print(f"\n{message}")

    def _register(self):
        """Handle user registration."""
        print("\n" + "-"*50)
        print("REGISTER".center(50))
        print("-"*50)

        username = input("Username: ").strip()
        password = input("Password: ").strip()
        name = input("Full Name: ").strip()
        email = input("Email (optional): ").strip() or None

        success, message = self.auth.register_user(username, password, name, email)
        print(f"\n{message}")

    def _search_books(self):
        """Handle book search."""
        print("\n" + "-"*50)
        print("SEARCH BOOKS".center(50))
        print("-"*50)

        query = input("Enter search term: ").strip()
        if not query:
            print("\nSearch term cannot be empty.")
            return

        print("\nSearch results:")
        books = self.library_service.search_books(query)
        self._display_books(books)

    def _view_all_books(self):
        """Display all books in the library."""
        print("\n" + "-"*50)
        print("ALL BOOKS".center(50))
        print("-"*50)

        books = self.library_service.get_all_books()
        self._display_books(books)

    def _display_books(self, books):
        """Display a list of books."""
        if not books:
            print("\nNo books found.")
            return

        print("\n{:<5} {:<30} {:<20} {:<15} {:<10}".format(
            "ID", "Title", "Author", "ISBN", "Available"))
        print("-"*80)

        for i, book in enumerate(books, 1):
            print("{:<5} {:<30} {:<20} {:<15} {:<10}".format(
                i,
                (book.title[:27] + '...') if len(book.title) > 27 else book.title,
                (book.author[:17] + '...') if len(book.author) > 17 else book.author,
                book.isbn,
                f"{book.available_copies}/{book.total_copies}"
            ))

    def _issue_book(self):
        """Handle issuing a book to the current user."""
        if not self.auth.is_authenticated():
            print("\nYou must be logged in to issue a book.")
            return

        print("\n" + "-"*50)
        print("ISSUE BOOK".center(50))
        print("-"*50)

        # Show all books or search for books
        choice = input("Do you want to (1) View all books or (2) Search for a book? (1/2): ").strip()

        if choice == '1':
            books = self.library_service.get_all_books()
        elif choice == '2':
            query = input("\nEnter search term: ").strip()
            books = self.library_service.search_books(query)
        else:
            print("\nInvalid choice.")
            return

        self._display_books(books)

        if not books:
            return

        try:
            book_index = int(input("\nEnter the ID of the book you want to issue: ").strip()) - 1
            if book_index < 0 or book_index >= len(books):
                print("\nInvalid book ID.")
                return

            book = books[book_index]
            success, message = self.library_service.issue_book(book.id)
            print(f"\n{message}")

        except ValueError:
            print("\nInvalid input. Please enter a number.")

    def _return_book(self):
        """Handle returning a book."""
        if not self.auth.is_authenticated():
            print("\nYou must be logged in to return a book.")
            return

        print("\n" + "-"*50)
        print("RETURN BOOK".center(50))
        print("-"*50)

        books, error = self.library_service.get_user_books()

        if error:
            print(f"\n{error}")
            return

        if not books:
            print("\nYou don't have any books issued.")
            return

        print("\nYour issued books:")
        print("\n{:<5} {:<30} {:<20} {:<15} {:<10}".format(
            "ID", "Title", "Author", "Due Date", "Fine"))
        print("-"*80)

        for i, book in enumerate(books, 1):
            due_date_str = book.due_date.strftime("%Y-%m-%d") if hasattr(book, 'due_date') else "N/A"
            fine_str = f"${book.fine:.2f}" if hasattr(book, 'fine') and book.fine > 0 else "None"

            print("{:<5} {:<30} {:<20} {:<15} {:<10}".format(
                i,
                (book.title[:27] + '...') if len(book.title) > 27 else book.title,
                (book.author[:17] + '...') if len(book.author) > 17 else book.author,
                due_date_str,
                fine_str
            ))

        try:
            book_index = int(input("\nEnter the ID of the book you want to return: ").strip()) - 1
            if book_index < 0 or book_index >= len(books):
                print("\nInvalid book ID.")
                return

            book = books[book_index]
            success, message = self.library_service.return_book(book.id)
            print(f"\n{message}")

        except ValueError:
            print("\nInvalid input. Please enter a number.")

    def _view_my_books(self):
        """Display books issued to the current user."""
        if not self.auth.is_authenticated():
            print("\nYou must be logged in to view your books.")
            return

        print("\n" + "-"*50)
        print("MY BOOKS".center(50))
        print("-"*50)

        books, error = self.library_service.get_user_books()

        if error:
            print(f"\n{error}")
            return

        if not books:
            print("\nYou don't have any books issued.")
            return

        print("\n{:<5} {:<30} {:<20} {:<15} {:<10}".format(
            "ID", "Title", "Author", "Due Date", "Status"))
        print("-"*80)

        for i, book in enumerate(books, 1):
            due_date_str = book.due_date.strftime("%Y-%m-%d") if hasattr(book, 'due_date') else "N/A"
            status = "Overdue" if hasattr(book, 'is_overdue') and book.is_overdue else "Active"

            print("{:<5} {:<30} {:<20} {:<15} {:<10}".format(
                i,
                (book.title[:27] + '...') if len(book.title) > 27 else book.title,
                (book.author[:17] + '...') if len(book.author) > 17 else book.author,
                due_date_str,
                status
            ))

    def _librarian_menu(self):
        """Display and handle the librarian menu."""
        if not self.auth.is_librarian():
            print("\nAccess denied. Only librarians can access this menu.")
            return

        while True:
            print("\n" + "-"*50)
            print("LIBRARIAN MENU".center(50))
            print("-"*50)
            print("1. Add Book")
            print("2. Remove Book")
            print("3. View Overdue Books")
            print("4. Back to Main Menu")

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == '1':
                self._add_book()
            elif choice == '2':
                self._remove_book()
            elif choice == '3':
                self._view_overdue_books()
            elif choice == '4':
                break
            else:
                print("\nInvalid choice. Please try again.")

            input("\nPress Enter to continue...")

    def _add_book(self):
        """Handle adding a new book."""
        print("\n" + "-"*50)
        print("ADD BOOK".center(50))
        print("-"*50)

        title = input("Title: ").strip()
        author = input("Author: ").strip()
        isbn = input("ISBN: ").strip()
        publisher = input("Publisher (optional): ").strip() or None

        try:
            year = input("Year (optional): ").strip()
            year = int(year) if year else None
        except ValueError:
            print("\nInvalid year. Using None.")
            year = None

        try:
            copies = input("Number of copies (default: 1): ").strip()
            copies = int(copies) if copies else 1
            if copies < 1:
                copies = 1
        except ValueError:
            print("\nInvalid number of copies. Using 1.")
            copies = 1

        if not title or not author or not isbn:
            print("\nTitle, author, and ISBN are required.")
            return

        success, message = self.library_service.add_book(title, author, isbn, publisher, year, copies)
        print(f"\n{message}")

    def _remove_book(self):
        """Handle removing a book."""
        print("\n" + "-"*50)
        print("REMOVE BOOK".center(50))
        print("-"*50)

        # Show all books or search for books
        choice = input("Do you want to (1) View all books or (2) Search for a book? (1/2): ").strip()

        if choice == '1':
            books = self.library_service.get_all_books()
        elif choice == '2':
            query = input("\nEnter search term: ").strip()
            books = self.library_service.search_books(query)
        else:
            print("\nInvalid choice.")
            return

        self._display_books(books)

        if not books:
            return

        try:
            book_index = int(input("\nEnter the ID of the book you want to remove: ").strip()) - 1
            if book_index < 0 or book_index >= len(books):
                print("\nInvalid book ID.")
                return

            book = books[book_index]

            confirm = input(f"\nAre you sure you want to remove '{book.title}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("\nBook removal cancelled.")
                return

            success, message = self.library_service.remove_book(book.id)
            print(f"\n{message}")

        except ValueError:
            print("\nInvalid input. Please enter a number.")

    def _view_overdue_books(self):
        """Display all overdue books."""
        print("\n" + "-"*50)
        print("OVERDUE BOOKS".center(50))
        print("-"*50)

        overdue_items, error = self.library_service.get_overdue_books()

        if error:
            print(f"\n{error}")
            return

        if not overdue_items:
            print("\nNo overdue books found.")
            return

        print("\n{:<5} {:<25} {:<15} {:<15} {:<10} {:<10}".format(
            "ID", "Book Title", "User", "Due Date", "Days Late", "Fine"))
        print("-"*80)

        for i, item in enumerate(overdue_items, 1):
            book = item['book']
            user = item['user']
            transaction = item['transaction']
            fine = item['fine']

            due_date = transaction.due_date
            days_late = (datetime.now() - due_date).days

            print("{:<5} {:<25} {:<15} {:<15} {:<10} {:<10}".format(
                i,
                (book.title[:22] + '...') if len(book.title) > 22 else book.title,
                (user.name[:12] + '...') if len(user.name) > 12 else user.name,
                due_date.strftime("%Y-%m-%d"),
                days_late,
                f"${fine:.2f}"
            ))

    def _add_bca_books_if_empty(self):
        """Add sample BCA books if the library is empty."""
        books = self.data_handler.get_all_books()
        if not books:
            print("Adding sample BCA books to the library...")

            # Create a temporary admin login to add books
            current_user = self.auth.current_user
            admin_user = self.data_handler.find_user_by_username("admin")
            self.auth.current_user = admin_user

            # Add BCA programming books
            self.library_service.add_book(
                "Python Programming for Beginners",
                "John Smith",
                "978-1234567890",
                "Tech Publications",
                2022,
                3
            )

            self.library_service.add_book(
                "Introduction to Java Programming",
                "Daniel Liang",
                "978-0136520238",
                "Pearson",
                2021,
                2
            )

            self.library_service.add_book(
                "C Programming Language",
                "Brian Kernighan, Dennis Ritchie",
                "978-0131103627",
                "Prentice Hall",
                1988,
                5
            )

            # Add BCA database books
            self.library_service.add_book(
                "Database Management Systems",
                "Raghu Ramakrishnan",
                "978-0072465631",
                "McGraw-Hill",
                2002,
                2
            )

            self.library_service.add_book(
                "SQL: The Complete Reference",
                "James Groff",
                "978-0071592550",
                "McGraw-Hill",
                2010,
                3
            )

            # Add BCA data structures books
            self.library_service.add_book(
                "Data Structures and Algorithms in Python",
                "Michael T. Goodrich",
                "978-1118290279",
                "Wiley",
                2013,
                2
            )

            self.library_service.add_book(
                "Introduction to Algorithms",
                "Thomas H. Cormen",
                "978-0262033848",
                "MIT Press",
                2009,
                3
            )

            # Add BCA networking books
            self.library_service.add_book(
                "Computer Networks",
                "Andrew S. Tanenbaum",
                "978-0132126953",
                "Pearson",
                2010,
                2
            )

            # Add BCA software engineering books
            self.library_service.add_book(
                "Software Engineering",
                "Ian Sommerville",
                "978-0137053469",
                "Pearson",
                2015,
                2
            )

            # Add BCA web development books
            self.library_service.add_book(
                "Web Development with Node and Express",
                "Ethan Brown",
                "978-1491949306",
                "O'Reilly Media",
                2019,
                2
            )

            self.library_service.add_book(
                "HTML and CSS: Design and Build Websites",
                "Jon Duckett",
                "978-1118008188",
                "Wiley",
                2011,
                3
            )

            # Add BCA operating system books
            self.library_service.add_book(
                "Operating System Concepts",
                "Abraham Silberschatz",
                "978-1118063330",
                "Wiley",
                2012,
                2
            )

            # Add BCA mathematics books
            self.library_service.add_book(
                "Discrete Mathematics and Its Applications",
                "Kenneth Rosen",
                "978-0073383095",
                "McGraw-Hill",
                2018,
                2
            )

            self.library_service.add_book(
                "Calculus: Early Transcendentals",
                "James Stewart",
                "978-1285741550",
                "Cengage Learning",
                2015,
                2
            )

            # Add BCA artificial intelligence books
            self.library_service.add_book(
                "Artificial Intelligence: A Modern Approach",
                "Stuart Russell, Peter Norvig",
                "978-0136042594",
                "Pearson",
                2020,
                2
            )

            # Restore original user
            self.auth.current_user = current_user
            print("Sample BCA books added successfully!")
