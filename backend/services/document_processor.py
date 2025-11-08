"""
Document Processing Service

Uses LangChain's optimized loaders and splitters
This is the "hybrid" approach - leveraging LangChain for scaffolding

Save ~1.5 hours compared to building manual PDF/EPUB parsers
"""

import os
from typing import List, Dict
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# EPUB loader might not be available in all versions
try:
    from langchain_community.document_loaders import UnstructuredEPUBLoader
except ImportError:
    UnstructuredEPUBLoader = None


def process_book(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> Dict:
    """
    Process a book file (PDF or EPUB) into text chunks for RAG.

    Uses LangChain's document loaders and text splitters for fast processing.

    Args:
        file_path: Path to the book file (.pdf or .epub)
        chunk_size: Size of each text chunk (default: 1000 characters)
        chunk_overlap: Overlap between chunks for context (default: 200 characters)

    Return:
        Dictionary containing:
            - 'chunks': List of text chunks
            - 'metadata': Book metadata (title, pages, etc.)
            - 'total_chunks': Number of chunks created
            - 'total_chars': Total characters processed

    Raise:
        FileNotFoundError: If the book file doesn't exist
        ValueError: If the file format is not supported

    Example:
        >>> result = process_book("anna_karenina.pdf")
        >>> print(f"Processed {result['total_chunks']} chunks")
        >>> print(result['chunks'][0][:100])  # First 100 chars of first chunk
    """
    # Validate the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Book file not found: {file_path}")

    # Determine file type and select appropriate loader
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == '.pdf':
        loader = UnstructuredPDFLoader(file_path)
    elif file_ext == '.epub':
        if UnstructuredEPUBLoader is None:
            raise ValueError("EPUB support not available. Install with: pip install unstructured[epub]")
        loader = UnstructuredEPUBLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Only .pdf are supported.")

    # Load the document
    print(f"Loading document: {os.path.basename(file_path)}")
    documents: List[Document] = loader.load()

    # Extract metadata
    metadata = {
        'filename': os.path.basename(file_path),
        'file_type': file_ext,
        'num_pages': len(documents) if documents else 0,
    }

    # If documents have metadata, extract it
    if documents and hasattr(documents[0], 'metadata'):
        metadata.update(documents[0].metadata)

    # Split documents into chunks using RecursiveCharacterTextSplitter
    # This splitter tries to keep semantically related text together
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Try to split on paragraphs first
    )

    print(f"Splitting into chunks (size={chunk_size}, overlap={chunk_overlap})")
    chunks_docs: List[Document] = text_splitter.split_documents(documents)

    # Extract just the text content from Document objects
    chunks = [doc.page_content for doc in chunks_docs]

    # Calculate statistics
    total_chars = sum(len(chunk) for chunk in chunks)

    result = {
        'chunks': chunks,
        'metadata': metadata,
        'total_chunks': len(chunks),
        'total_chars': total_chars,
    }

    print(f"✓ Processed {len(chunks)} chunks ({total_chars:,} characters)")

    return result


def get_supported_formats() -> List[str]:
    """
    Get list of supported book formats.

    Returns:
        List of supported file extensions
    """
    return ['.pdf', '.epub']


if __name__ == "__main__":
    # Test the document processor
    print("Document Processor - Test Mode")
    print("=" * 60)
    print("Supported formats:", get_supported_formats())
    print("\nTo test with a real book:")
    print("  result = process_book('path/to/book.pdf')")
    print("  print(f'Processed {result[\"total_chunks\"]} chunks')")
