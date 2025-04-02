#!/usr/bin/env python3
# Library Management System - Authentication

import hashlib
import os
from .models import User


class Authentication:
    """Handles user authentication for the Library Management System."""

    def __init__(self, data_handler):
        """Initialize the authentication system."""
        self.data_handler = data_handler
        self.current_user = None

    def _hash_password(self, password):
        """Hash a password for secure storage."""
        # In a real application, use a secure hashing method
        # For simplicity, we're using a basic hash here
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, name, email=None, role='member'):
        """Register a new user."""
        # Check if username already exists
        if self.data_handler.find_user_by_username(username):
            return False, "Username already exists."

        # Create and save the new user
        hashed_password = self._hash_password(password)
        user = User(username, hashed_password, name, email, role)
        self.data_handler.add_user(user)
        return True, "User registered successfully."

    def login(self, username, password):
        """Log in a user."""
        user = self.data_handler.find_user_by_username(username)
        if not user:
            return False, "User not found."

        hashed_password = self._hash_password(password)
        if user.password != hashed_password:
            return False, "Incorrect password."

        self.current_user = user
        return True, "Login successful."

    def logout(self):
        """Log out the current user."""
        self.current_user = None
        return True, "Logged out successfully."

    def is_authenticated(self):
        """Check if a user is currently authenticated."""
        return self.current_user is not None

    def is_admin(self):
        """Check if the current user is an admin."""
        return self.is_authenticated() and self.current_user.role == 'admin'

    def is_librarian(self):
        """Check if the current user is a librarian or admin."""
        return self.is_authenticated() and (
            self.current_user.role == 'librarian' or
            self.current_user.role == 'admin'
        )

    def change_password(self, current_password, new_password):
        """Change a user's password."""
        if not self.is_authenticated():
            return False, "No user is logged in."

        hashed_current = self._hash_password(current_password)
        if self.current_user.password != hashed_current:
            return False, "Current password is incorrect."

        hashed_new = self._hash_password(new_password)
        self.current_user.password = hashed_new
        self.data_handler.update_user(self.current_user)
        return True, "Password changed successfully."
