"""
Re-extract characters from existing books with updated limits
Uses new settings: 50 chunks, max 50 characters
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import Book, Character, GeneratedImage, get_db
from services.rag_system import BookRAG
from services.character_service import CharacterExtractor
from services.document_processor import process_book

def reextract_characters(book_id=None):
    """Re-extract characters from books with new limits"""
    db = get_db()

    try:
        # Get books to re-extract
        if book_id:
            books = db.query(Book).filter_by(id=book_id).all()
        else:
            books = db.query(Book).all()

        if not books:
            print("No books found!")
            return

        print(f"Found {len(books)} book(s) to re-extract\n")

        for book in books:
            print(f"{'='*60}")
            print(f"Re-extracting: {book.title}")
            print(f"Book ID: {book.id}")
            print(f"Current character count: {book.character_count}")

            # Confirm before proceeding
            response = input(f"\nRe-extract characters for '{book.title}'? (yes/no): ")
            if response.lower() != 'yes':
                print("Skipped\n")
                continue

            # Delete existing characters and images
            print("\nDeleting existing characters and images...")
            old_chars = db.query(Character).filter_by(book_id=book.id).all()
            deleted_chars = 0
            deleted_images = 0

            for char in old_chars:
                # Delete images
                images = db.query(GeneratedImage).filter_by(character_id=char.id).all()
                for img in images:
                    db.delete(img)
                    deleted_images += 1

                # Delete character
                db.delete(char)
                deleted_chars += 1

            db.commit()
            print(f"✓ Deleted {deleted_chars} characters, {deleted_images} images")

            # Load FAISS index (should already exist)
            print("\nLoading FAISS index...")
            rag = BookRAG()
            try:
                faiss_indices_dir = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'static', 'faiss_indices'
                )
                rag.load_index(faiss_indices_dir, book.id)
                print("✓ FAISS index loaded")
            except Exception as e:
                print(f"⚠️  Could not load FAISS index: {e}")
                print("Need to re-process book file...")
                continue

            # Re-extract characters with NEW limits
            print("\nExtracting characters (NEW LIMITS: 50 chunks, max 50 characters)...")

            # Load book chunks from FAISS
            chunks = rag.get_all_chunks()  # Get all chunks from FAISS

            # Use first 50 chunks for character extraction
            book_text = "\n".join(chunks[:50])

            extractor = CharacterExtractor()
            character_names = extractor.extract_character_names(book_text, max_characters=50)

            print(f"✓ Extracted {len(character_names)} characters: {character_names[:10]}{'...' if len(character_names) > 10 else ''}")

            # Create character profiles
            print("\nCreating character profiles...")
            created_count = 0

            for char_name in character_names:
                try:
                    # Create canonical profile
                    profile = extractor.create_canonical_profile(
                        character_name=char_name,
                        rag_system=rag,
                        num_mentions=10
                    )

                    # Create Character record
                    character = Character(
                        book_id=book.id,
                        name=profile['name'],
                        canonical_description=profile['description'],
                        seed=profile['seed'],
                        mention_count=profile['mention_count']
                    )
                    db.add(character)
                    created_count += 1

                    print(f"  ✓ {char_name} ({profile['mention_count']} mentions)")

                except Exception as e:
                    print(f"  ✗ Failed to process {char_name}: {e}")
                    continue

            # Update book character count
            book.character_count = created_count
            db.commit()

            print(f"\n✅ Re-extraction complete!")
            print(f"   Old count: {deleted_chars} characters")
            print(f"   New count: {created_count} characters")
            print(f"   Improvement: +{created_count - deleted_chars} characters\n")

        print("="*60)
        print("All books processed!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    print("🔄 Character Re-extraction Tool")
    print("=" * 60)
    print("This will re-extract characters with NEW limits:")
    print("  - 50 chunks analyzed (was 10)")
    print("  - Max 50 characters (was 20)")
    print("=" * 60)
    print()

    # Check for book ID argument
    if len(sys.argv) > 1:
        book_id = sys.argv[1]
        print(f"Re-extracting for book ID: {book_id}\n")
        reextract_characters(book_id)
    else:
        print("Re-extracting for ALL books\n")
        reextract_characters()
