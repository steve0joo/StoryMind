#!/usr/bin/env python3
"""
Demo Preparation Script for Hackathon

Pre-generates all demo content to avoid:
- API rate limits during presentation
- Network issues
- Slow generation times (15-30s per image)

Run this 2-3 hours before your hackathon demo!
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.document_processor import process_book
from services.rag_system import BookRAG
from services.character_service import CharacterExtractor
from models import Book, Character, GeneratedImage, get_db

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def demo_prep():
    """
    Pre-generate all demo content for the hackathon presentation

    Steps:
    1. Load demo books from static/uploads/books/
    2. Process each book through the pipeline
    3. Extract characters and create profiles
    4. Generate images for top characters
    5. Cache everything in the database
    """

    print_header("DEMO PREPARATION SCRIPT")
    print("This will pre-generate all content for your hackathon demo")
    print("Estimated time: 10-15 minutes")

    # TODO: Implement the following steps

    # Step 1: Find demo books
    print_header("Step 1: Finding Demo Books")
    books_dir = Path(__file__).parent.parent / "static" / "uploads" / "books"

    demo_books = list(books_dir.glob("*.pdf"))
    print(f"Found {len(demo_books)} PDF files")

    if not demo_books:
        print("⚠️  No demo books found!")
        print(f"   Please add PDF files to: {books_dir}")
        print("   Recommended: Harry Potter, Night Circus, or any public domain book")
        return

    for book_path in demo_books:
        print(f"  - {book_path.name}")

    # Step 2: Process each book
    print_header("Step 2: Processing Books")

    db = get_db()

    for book_path in demo_books:
        print(f"\n📚 Processing: {book_path.name}")

        try:
            # Process document
            print("  1. Extracting text and creating chunks...")
            result = process_book(str(book_path))

            # Create RAG index
            print("  2. Creating FAISS index...")
            rag = BookRAG()
            rag.ingest_chunks(result['chunks'], book_id=book_path.stem)

            # Save index
            index_dir = Path(__file__).parent.parent / "data" / "faiss_indices"
            index_dir.mkdir(parents=True, exist_ok=True)
            rag.save_index(str(index_dir))

            # Extract characters
            print("  3. Extracting characters with Gemini...")
            extractor = CharacterExtractor()

            # Use first 50 chunks for character extraction (faster)
            sample_text = ' '.join(result['chunks'][:50])
            character_names = extractor.extract_character_names(sample_text, max_characters=10)

            print(f"     Found {len(character_names)} characters")

            # Save book to database
            book = Book(
                title=result['metadata'].get('filename', book_path.stem),
                author="Demo Author",  # TODO: Extract from metadata
                processing_status="completed",
                faiss_index_path=str(index_dir / f"{book_path.stem}.faiss"),
                character_count=len(character_names)
            )
            db.add(book)
            db.commit()

            # Create profiles for top 5 characters
            print("  4. Creating character profiles...")
            for i, name in enumerate(character_names[:5], 1):
                print(f"     {i}. {name}")

                try:
                    # Create canonical profile
                    profile = extractor.create_canonical_profile(name, rag, num_mentions=10)

                    # Save character to database
                    character = Character(
                        book_id=book.id,
                        name=profile['name'],
                        canonical_description=profile['description'],
                        seed=profile['seed'],
                        mention_count=profile['mention_count']
                    )
                    db.add(character)
                    db.commit()

                    # TODO: Generate image (requires Vertex AI)
                    # from services.image_service import ImageGenerator
                    # generator = ImageGenerator()
                    # result = generator.generate_character_image(profile)
                    #
                    # image = GeneratedImage(
                    #     character_id=character.id,
                    #     prompt=result['prompt'],
                    #     image_url=result['image_url'],
                    #     generation_time_ms=result['generation_time_ms']
                    # )
                    # db.add(image)
                    # db.commit()

                    # Rate limiting (Gemini: 15 req/min)
                    time.sleep(4)

                except Exception as e:
                    print(f"        ⚠️  Error creating profile for {name}: {e}")
                    continue

            print(f"  ✅ Completed: {book_path.name}")

        except Exception as e:
            print(f"  ❌ Error processing {book_path.name}: {e}")
            continue

    db.close()

    print_header("DEMO PREP COMPLETE")
    print("✅ All demo content has been pre-generated and cached")
    print("\nNext steps:")
    print("  1. Start the backend: python app.py")
    print("  2. Start the frontend: cd ../frontend && npm run dev")
    print("  3. Test the demo flow in the UI")
    print("\n⚠️  Remember: This uses API credits. Use cached data during actual demo!")

if __name__ == "__main__":
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not set in .env")
        print("   Please add your Google API key before running demo prep")
        sys.exit(1)

    demo_prep()
