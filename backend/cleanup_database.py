#!/usr/bin/env python3
"""
Database Cleanup Script
Removes orphaned book entries that don't have corresponding physical files.
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from models import Book, Character, GeneratedImage, Base

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/storymind.db')
engine = create_engine(DATABASE_URL.replace('sqlite:///', f'sqlite:///{os.path.dirname(__file__)}/'))
Session = sessionmaker(bind=engine)

def get_db():
    """Get database session"""
    return Session()

def cleanup_orphaned_books():
    """Remove book entries without corresponding physical files"""

    db = get_db()
    books_dir = Path(__file__).parent / "static" / "uploads" / "books"

    print("=" * 60)
    print("Database Cleanup - Orphaned Books")
    print("=" * 60)

    # Get all books from database
    all_books = db.query(Book).all()
    print(f"\nTotal books in database: {len(all_books)}")

    # Get all physical files
    physical_files = set()
    if books_dir.exists():
        for file in books_dir.iterdir():
            if file.is_file() and file.suffix in ['.pdf', '.epub', '.txt']:
                physical_files.add(file.name)

    print(f"Physical files found: {len(physical_files)}")
    print(f"Files: {list(physical_files)}\n")

    # Find orphaned books
    orphaned = []
    valid = []

    # Extract UUIDs from physical files (files are named {uuid}.pdf)
    physical_uuids = set()
    for filename in physical_files:
        # Extract UUID from filename (e.g., "UUID.pdf" -> "UUID")
        uuid_part = os.path.splitext(filename)[0]
        physical_uuids.add(uuid_part)

    for book in all_books:
        # Check if book ID has a corresponding physical file
        if book.id in physical_uuids:
            valid.append(book)
            print(f"✅ VALID: {book.title[:50]} (ID: {book.id[:8]}...)")
        else:
            orphaned.append(book)
            print(f"❌ ORPHAN: {book.title[:50]} (ID: {book.id[:8]}..., No file)")

    print(f"\n" + "=" * 60)
    print(f"Summary: {len(valid)} valid, {len(orphaned)} orphaned")
    print("=" * 60)

    if not orphaned:
        print("\n✨ Database is clean! No orphaned entries found.")
        return

    # Confirm deletion
    print(f"\n⚠️  Found {len(orphaned)} orphaned book entries to delete:")
    for book in orphaned:
        char_count = db.query(Character).filter_by(book_id=book.id).count()
        print(f"  - {book.title} ({char_count} characters)")

    response = input(f"\n❓ Delete these {len(orphaned)} orphaned entries? (yes/no): ").strip().lower()

    if response != 'yes':
        print("❌ Cleanup cancelled.")
        return

    # Delete orphaned books
    deleted_count = 0
    for book in orphaned:
        book_id = book.id
        book_title = book.title

        # Delete associated characters and images
        characters = db.query(Character).filter_by(book_id=book_id).all()
        for char in characters:
            # Delete images first (foreign key constraint)
            images = db.query(GeneratedImage).filter_by(character_id=char.id).all()
            for img in images:
                db.delete(img)
            db.delete(char)

        # Delete the book
        db.delete(book)
        deleted_count += 1
        print(f"🗑️  Deleted: {book_title} (ID: {book_id[:8]}...)")

    db.commit()

    print(f"\n✅ Cleanup complete! Deleted {deleted_count} orphaned book entries.")
    print(f"✨ Database now has {len(valid)} valid book entries.")

if __name__ == "__main__":
    cleanup_orphaned_books()
