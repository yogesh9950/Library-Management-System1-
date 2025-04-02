#!/usr/bin/env python3
# Library Management System - Main Script

from library.system import LibrarySystem

def main():
    """Main entry point for the Library Management System"""
    library_system = LibrarySystem()
    library_system.start()

if __name__ == "__main__":
    main()
