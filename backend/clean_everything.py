#!/usr/bin/env python3
"""
Complete Database and File Cleanup
Removes ALL books, characters, images, and FAISS indices
"""

import os
import sys
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(__file__))

from models import Book, Character, GeneratedImage, Base

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/storymind.db')
engine = create_engine(DATABASE_URL.replace('sqlite:///', f'sqlite:///{os.path.dirname(__file__)}/'))
Session = sessionmaker(bind=engine)

def clean_everything():
    """Remove all books, characters, images, and files"""

    print("=" * 60)
    print("COMPLETE CLEANUP - Remove All Data")
    print("=" * 60)

    db = Session()
    base_dir = Path(__file__).parent

    # Count current data
    book_count = db.query(Book).count()
    char_count = db.query(Character).count()
    image_count = db.query(GeneratedImage).count()

    print(f"\nCurrent database:")
    print(f"  📚 Books: {book_count}")
    print(f"  👤 Characters: {char_count}")
    print(f"  🖼️  Images: {image_count}")

    # Count files
    books_dir = base_dir / "static" / "uploads" / "books"
    images_dir = base_dir / "static" / "uploads" / "images"
    faiss_dir = base_dir / "static" / "faiss_indices"

    book_files = len(list(books_dir.glob("*"))) if books_dir.exists() else 0
    image_files = len(list(images_dir.glob("*.png"))) if images_dir.exists() else 0
    faiss_files = len(list(faiss_dir.glob("*"))) if faiss_dir.exists() else 0

    print(f"\nCurrent files:")
    print(f"  📁 Book files: {book_files}")
    print(f"  📁 Image files: {image_files}")
    print(f"  📁 FAISS indices: {faiss_files}")

    print("\n" + "=" * 60)
    print("This will DELETE:")
    print("  ❌ All book database entries")
    print("  ❌ All character database entries")
    print("  ❌ All image database entries")
    print("  ❌ All book files")
    print("  ❌ All image files")
    print("  ❌ All FAISS index files")
    print("=" * 60)

    # Step 1: Clean database
    print("\n🗑️  Cleaning database...")

    # Delete in correct order (foreign key constraints)
    deleted_images = db.query(GeneratedImage).delete()
    deleted_chars = db.query(Character).delete()
    deleted_books = db.query(Book).delete()
    db.commit()

    print(f"  ✅ Deleted {deleted_images} images")
    print(f"  ✅ Deleted {deleted_chars} characters")
    print(f"  ✅ Deleted {deleted_books} books")

    # Step 2: Clean files
    print("\n🗑️  Cleaning files...")

    # Remove book files
    if books_dir.exists():
        for file in books_dir.glob("*"):
            if file.is_file():
                file.unlink()
        print(f"  ✅ Deleted {book_files} book files")

    # Remove image files
    if images_dir.exists():
        for file in images_dir.glob("*.png"):
            file.unlink()
        print(f"  ✅ Deleted {image_files} image files")

    # Remove FAISS indices
    if faiss_dir.exists():
        shutil.rmtree(faiss_dir)
        faiss_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Deleted all FAISS indices")

    print("\n" + "=" * 60)
    print("✨ CLEANUP COMPLETE!")
    print("=" * 60)
    print("\nYour database and file system are now clean.")
    print("You can re-upload books to start fresh.")
    print("\nNext steps:")
    print("  1. Start backend: cd backend && python app.py")
    print("  2. Start frontend: cd frontend && npm run dev")
    print("  3. Upload books through UI")
    print("  4. New limits will apply: 50 chunks, 50 max characters")

if __name__ == "__main__":
    clean_everything()
