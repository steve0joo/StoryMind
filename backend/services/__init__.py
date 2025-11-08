"""
AI/ML Services for StoryMind

This package contains all ML/AI-related services:
- Document processing (LangChain loaders + splitters)
- RAG system (Custom FAISS implementation)
- Character extraction (Gemini 2.5 Flash)
- Image generation (Imagen 3)
"""

from .document_processor import process_book
from .rag_system import BookRAG
from .character_service import extract_characters, create_canonical_profile

# Image service will be imported when it's created
try:
    from .image_service import generate_character_image
    __all__ = [
        'process_book',
        'BookRAG',
        'extract_characters',
        'create_canonical_profile',
        'generate_character_image'
    ]
except ImportError:
    __all__ = [
        'process_book',
        'BookRAG',
        'extract_characters',
        'create_canonical_profile'
    ]