"""
Clean up duplicate books from the database
Keeps only one copy of each unique book
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import Book, Character, GeneratedImage, get_db
from sqlalchemy import func

def cleanup_duplicate_books():
    """Remove duplicate books, keeping the one with most characters"""
    db = get_db()

    try:
        # Get all books
        books = db.query(Book).all()

        print(f"Found {len(books)} total books in database")
        print("\nAnalyzing duplicates...\n")

        # Group books by title
        book_groups = {}
        for book in books:
            title = book.title
            if title not in book_groups:
                book_groups[title] = []
            book_groups[title].append(book)

        # Find duplicates
        duplicates_to_delete = []
        for title, group in book_groups.items():
            if len(group) > 1:
                print(f"📚 {title}")
                print(f"   Found {len(group)} copies:")

                # Sort by character count (descending) - keep the one with most characters
                group_sorted = sorted(group, key=lambda b: b.character_count or 0, reverse=True)

                for i, book in enumerate(group_sorted):
                    char_count = db.query(Character).filter_by(book_id=book.id).count()
                    if i == 0:
                        print(f"   ✅ KEEP: {book.id[:8]}... ({char_count} characters)")
                    else:
                        print(f"   ❌ DELETE: {book.id[:8]}... ({char_count} characters)")
                        duplicates_to_delete.append(book)
                print()

        if not duplicates_to_delete:
            print("✅ No duplicates found!")
            return

        # Confirm deletion
        print(f"\n⚠️  Ready to delete {len(duplicates_to_delete)} duplicate books")
        print("This will also delete their characters and generated images.")
        response = input("Continue? (yes/no): ")

        if response.lower() != 'yes':
            print("❌ Cancelled")
            return

        # Delete duplicates
        deleted_books = 0
        deleted_characters = 0
        deleted_images = 0

        for book in duplicates_to_delete:
            print(f"\nDeleting: {book.title} ({book.id[:8]}...)")

            # Delete associated characters and images
            characters = db.query(Character).filter_by(book_id=book.id).all()
            for char in characters:
                # Delete images
                images = db.query(GeneratedImage).filter_by(character_id=char.id).all()
                for img in images:
                    db.delete(img)
                    deleted_images += 1

                # Delete character
                db.delete(char)
                deleted_characters += 1

            # Delete book
            db.delete(book)
            deleted_books += 1

        # Commit changes
        db.commit()

        print(f"\n✅ Cleanup complete!")
        print(f"   Deleted: {deleted_books} books, {deleted_characters} characters, {deleted_images} images")

        # Show remaining books
        remaining_books = db.query(Book).all()
        print(f"\n📚 Remaining books ({len(remaining_books)}):")
        for book in remaining_books:
            char_count = db.query(Character).filter_by(book_id=book.id).count()
            print(f"   - {book.title} ({char_count} characters)")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise

    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 Database Cleanup - Remove Duplicate Books")
    print("=" * 60)
    cleanup_duplicate_books()
