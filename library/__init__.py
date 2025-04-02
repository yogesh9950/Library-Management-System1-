#!/usr/bin/env python3
# Library Management System - Package Initialization

from .models import Book, User, Transaction
from .data_handler import DataHandler
from .auth import Authentication
from .service import LibraryService
from .system import LibrarySystem

__version__ = '1.0.0'
__author__ = 'Library Management System Team'
