"""
Books API Routes
Handles book upload, processing, and retrieval
"""

import os
import time
import uuid
import logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

# Import models and services
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import Book, Character, get_db
from services.document_processor import process_book
from services.rag_system import BookRAG
from services.character_service import CharacterExtractor

# Create Blueprint
books_bp = Blueprint('books', __name__)

# Set up logger for this module
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.epub', '.txt'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@books_bp.route('/upload', methods=['POST'])
def upload_book():
    """
    Upload and process a book file

    POST /api/books/upload

    Request: multipart/form-data with 'file' field

    Response:
    {
        "book_id": "abc-123",
        "title": "Harry Potter",
        "character_count": 8,
        "processing_time_seconds": 45
    }
    """
    start_time = time.time()

    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file provided',
            'message': 'Please upload a file'
        }), 400

    file = request.files['file']

    # Check if filename is empty
    if file.filename == '':
        return jsonify({
            'error': 'No file selected',
            'message': 'Please select a file to upload'
        }), 400

    # Check file extension
    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Invalid file type',
            'message': f'Only PDF, EPUB, and TXT files are allowed'
        }), 400

    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1]

        # We'll check for duplicates AFTER extracting metadata (see below)
        # This placeholder will be replaced with actual duplicate detection

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # Get upload folder from app config
        upload_folder = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'uploads', 'books'
        )

        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)

        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        logger.info(f"File saved: {file_path}")

        # Step 1: Process book with document_processor
        logger.info(f"Processing book: {filename}")
        book_result = process_book(file_path)
        chunks = book_result['chunks']
        metadata = book_result['metadata']

        logger.info(f"Processed {len(chunks)} chunks from {filename}")

        # Step 2: Create FAISS index with RAG system
        logger.info("Creating FAISS index for semantic search")
        book_id = str(uuid.uuid4())
        rag = BookRAG()
        rag.ingest_chunks(chunks, book_id)

        # Save FAISS index
        faiss_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'faiss_indices'
        )
        os.makedirs(faiss_dir, exist_ok=True)
        faiss_index_path = rag.save_index(faiss_dir)

        logger.info(f"FAISS index saved to: {faiss_index_path}")

        # Step 3: Extract characters
        logger.info("Extracting characters using Gemini")
        extractor = CharacterExtractor()

        # QUOTA OPTIMIZATION: Use 35 chunks instead of 50 (reduces token usage, still gets main characters)
        # 35 chunks = ~35,000 chars, enough for character introductions in most books
        book_text = "\n".join(chunks[:35])  # First 35 chunks for character extraction
        character_names = extractor.extract_character_names(book_text, max_characters=50)

        logger.info(f"Extracted {len(character_names)} characters: {character_names}")

        # Step 3.5: Deduplicate characters (remove aliases like "Mrs Dursley" + "Petunia")
        # QUOTA OPTIMIZATION: Use fuzzy matching only (no LLM) to save API calls
        try:
            from utils.character_deduplication import CharacterDeduplicator
            dedup = CharacterDeduplicator(use_llm=False)  # Fuzzy matching only - saves ~28 API calls/book
            character_names, alias_map = dedup.deduplicate_characters(character_names)
            logger.info(f"After deduplication: {len(character_names)} unique characters")
            if alias_map:
                logger.info(f"Merged duplicates: {alias_map}")
        except Exception as e:
            logger.warning(f"Character deduplication failed: {e}, continuing with original names")
            # Continue with original names if deduplication fails

        # Step 4: Create Book record in database
        db = get_db()
        book = None  # Initialize to prevent NameError in exception handler
        try:
            # Extract title from metadata or filename
            title = metadata.get('title', os.path.splitext(filename)[0])
            author = metadata.get('author', 'Unknown')

            logger.info(f"Extracted metadata - Title: {title}, Author: {author}")

            # AUTO-DELETE DUPLICATES: Check for existing books with same title
            from models import GeneratedImage
            existing_books = db.query(Book).filter(Book.title == title).all()
            if existing_books:
                logger.warning(f"Auto-deleting {len(existing_books)} duplicate book(s) with title: {title}")

                for existing_book in existing_books:
                    logger.info(f"Deleting duplicate: {existing_book.id}")

                    # Delete associated characters and images
                    characters = db.query(Character).filter_by(book_id=existing_book.id).all()
                    for char in characters:
                        images = db.query(GeneratedImage).filter_by(character_id=char.id).all()
                        for img in images:
                            # Delete physical image file
                            if img.image_url:
                                image_path = os.path.join(
                                    os.path.dirname(os.path.dirname(__file__)),
                                    'static',
                                    img.image_url.lstrip('/')
                                )
                                if os.path.exists(image_path):
                                    try:
                                        os.remove(image_path)
                                    except:
                                        pass
                            db.delete(img)
                        db.delete(char)

                    # Delete FAISS index files
                    if existing_book.faiss_index_path:
                        for ext in ['.faiss', '.pkl']:
                            path = existing_book.faiss_index_path.replace('.faiss', ext)
                            if os.path.exists(path):
                                try:
                                    os.remove(path)
                                except:
                                    pass

                    # Delete the book
                    db.delete(existing_book)

                db.commit()
                logger.info(f"✓ Deleted {len(existing_books)} duplicate(s), proceeding with upload")

            book = Book(
                id=book_id,
                title=title,
                author=author,
                processing_status='processing',
                faiss_index_path=faiss_index_path,
                character_count=0  # Will update after creating characters
            )

            db.add(book)
            db.commit()

            logger.info(f"Book record created in database: {book_id}")

            # Step 5: Create Character records
            characters_created = 0

            for char_name in character_names:
                try:
                    # Create canonical profile for each character
                    # QUOTA OPTIMIZATION: Use 7 chunks instead of 10 (still captures 80%+ visual details)
                    profile = extractor.create_canonical_profile(char_name, rag, num_mentions=7)

                    # Create Character record
                    character = Character(
                        book_id=book_id,
                        name=profile['name'],
                        canonical_description=profile['description'],
                        seed=profile['seed'],
                        mention_count=profile['mention_count']
                    )

                    db.add(character)
                    characters_created += 1

                    logger.info(f"Character profile created: {char_name} (seed: {profile['seed']})")

                    # QUOTA OPTIMIZATION: Add small delay to avoid rate limits (15 req/min)
                    # 4 seconds between requests = ~15 requests/minute (within free tier limits)
                    import time as time_module
                    time_module.sleep(4)

                except Exception as e:
                    logger.warning(f"Failed to create character profile for {char_name}: {e}")
                    continue

            # Update book with character count
            book.character_count = characters_created
            book.processing_status = 'completed'
            db.commit()

            logger.info(f"Book processing completed successfully: {characters_created} characters created")

            # Calculate processing time
            processing_time = time.time() - start_time

            return jsonify({
                'success': True,
                'book_id': book_id,
                'title': title,
                'author': author,
                'character_count': characters_created,
                'processing_time_seconds': round(processing_time, 2),
                'message': f'Book processed successfully with {characters_created} characters'
            }), 201

        except Exception as e:
            db.rollback()
            logger.error(f"Database error during book creation: {e}", exc_info=True)

            # Update book status to failed
            if book:
                book.processing_status = 'failed'
                db.commit()

            raise

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error processing book upload: {e}", exc_info=True)

        # Cleanup uploaded file on failure
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up uploaded file: {file_path}")
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup uploaded file: {cleanup_error}")

        # Cleanup FAISS index on failure
        try:
            if 'faiss_index_path' in locals() and os.path.exists(faiss_index_path):
                os.remove(faiss_index_path)
                # Also remove .pkl metadata file
                pkl_path = faiss_index_path.replace('.faiss', '.pkl')
                if os.path.exists(pkl_path):
                    os.remove(pkl_path)
                logger.info(f"Cleaned up FAISS index: {faiss_index_path}")
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup FAISS index: {cleanup_error}")

        return jsonify({
            'error': 'Processing failed',
            'message': str(e)
        }), 500


@books_bp.route('', methods=['GET'])
def list_books():
    """
    List all books

    GET /api/books

    Optional query params:
    - limit: number of books to return (default: 50)
    - offset: pagination offset (default: 0)

    Response:
    {
        "books": [
            {
                "id": "abc-123",
                "title": "Harry Potter",
                "author": "J.K. Rowling",
                "character_count": 8,
                "processing_status": "completed"
            }
        ],
        "total": 1
    }
    """
    try:
        # Get pagination params
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        db = get_db()
        try:
            # Query books with pagination
            books = db.query(Book).limit(limit).offset(offset).all()
            total = db.query(Book).count()

            return jsonify({
                'books': [book.to_dict() for book in books],
                'total': total,
                'limit': limit,
                'offset': offset
            }), 200

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error listing books: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to list books',
            'message': str(e)
        }), 500


@books_bp.route('/<book_id>', methods=['GET'])
def get_book(book_id):
    """
    Get details of a specific book

    GET /api/books/:id

    Response:
    {
        "id": "abc-123",
        "title": "Harry Potter",
        "author": "J.K. Rowling",
        "character_count": 8,
        "processing_status": "completed",
        "upload_date": "2025-11-08T10:30:00"
    }
    """
    try:
        db = get_db()
        try:
            # Query book by ID
            book = db.query(Book).filter(Book.id == book_id).first()

            if not book:
                return jsonify({
                    'error': 'Book not found',
                    'message': f'No book found with ID: {book_id}'
                }), 404

            return jsonify(book.to_dict()), 200

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error getting book {book_id}: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to get book',
            'message': str(e)
        }), 500


@books_bp.route('/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Delete a book and all associated data (characters, images, FAISS index)

    DELETE /api/books/:id

    Response:
    {
        "message": "Book deleted successfully",
        "book_id": "abc-123",
        "deleted_characters": 8,
        "deleted_images": 5
    }
    """
    try:
        db = get_db()
        try:
            # Find the book
            book = db.query(Book).filter(Book.id == book_id).first()

            if not book:
                return jsonify({
                    'error': 'Book not found',
                    'message': f'No book found with ID: {book_id}'
                }), 404

            book_title = book.title
            faiss_index_path = book.faiss_index_path

            logger.info(f"Deleting book: {book_title} (ID: {book_id})")

            # Delete associated data
            from models import GeneratedImage

            # Get all characters for this book
            characters = db.query(Character).filter(Character.book_id == book_id).all()
            deleted_characters = len(characters)
            deleted_images = 0

            for char in characters:
                # Delete all images for this character
                images = db.query(GeneratedImage).filter(GeneratedImage.character_id == char.id).all()
                for img in images:
                    # Delete physical image file
                    if img.image_url:
                        image_path = os.path.join(
                            os.path.dirname(os.path.dirname(__file__)),
                            'static',
                            img.image_url.lstrip('/')
                        )
                        if os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                                logger.info(f"Deleted image file: {image_path}")
                            except Exception as e:
                                logger.warning(f"Failed to delete image file {image_path}: {e}")

                    db.delete(img)
                    deleted_images += 1

                # Delete character
                db.delete(char)

            # Delete FAISS index files
            if faiss_index_path:
                # Remove .faiss file
                if os.path.exists(faiss_index_path):
                    try:
                        os.remove(faiss_index_path)
                        logger.info(f"Deleted FAISS index: {faiss_index_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete FAISS index: {e}")

                # Remove .pkl metadata file
                pkl_path = faiss_index_path.replace('.faiss', '.pkl')
                if os.path.exists(pkl_path):
                    try:
                        os.remove(pkl_path)
                        logger.info(f"Deleted FAISS metadata: {pkl_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete FAISS metadata: {e}")

            # Delete the book itself
            db.delete(book)
            db.commit()

            logger.info(f"Successfully deleted book: {book_title} ({deleted_characters} characters, {deleted_images} images)")

            return jsonify({
                'message': 'Book deleted successfully',
                'book_id': book_id,
                'book_title': book_title,
                'deleted_characters': deleted_characters,
                'deleted_images': deleted_images
            }), 200

        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error deleting book {book_id}: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to delete book',
            'message': str(e)
        }), 500


@books_bp.route('/<book_id>/characters', methods=['GET'])
def get_book_characters(book_id):
    """
    Get all characters for a specific book

    GET /api/books/:id/characters

    Response:
    {
        "book_id": "abc-123",
        "characters": [
            {
                "id": "char-456",
                "name": "Harry Potter",
                "canonical_description": "...",
                "seed": 2847593921,
                "mention_count": 15
            }
        ],
        "total": 8
    }
    """
    try:
        db = get_db()
        try:
            # First check if book exists
            book = db.query(Book).filter(Book.id == book_id).first()

            if not book:
                return jsonify({
                    'error': 'Book not found',
                    'message': f'No book found with ID: {book_id}'
                }), 404

            # Query characters for this book
            characters = db.query(Character).filter(Character.book_id == book_id).all()

            return jsonify({
                'book_id': book_id,
                'book_title': book.title,
                'characters': [char.to_dict() for char in characters],
                'total': len(characters)
            }), 200

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error getting characters for book {book_id}: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to get characters',
            'message': str(e)
        }), 500
