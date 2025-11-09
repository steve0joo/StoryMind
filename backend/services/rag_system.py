"""
Custom RAG (Retrieval-Augmented Generation) System

Direct FAISS implementation for full control over retrieval and ranking.
NOT using LangChain's FAISS wrapper - this gives us precise control.

Uses SentenceTransformer for embeddings (all-MiniLM-L6-v2, 384 dimensions).
"""

import os
import pickle
from typing import List, Dict, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


class BookRAG:
    """
    Custom FAISS-based RAG system for character context retrieval.

    This is the core ML component that enables accurate character extraction.
    """

    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the RAG system.

        Args:
            embedding_model: SentenceTransformer model name
                           (default: all-MiniLM-L6-v2 with 384 dimensions)
        """
        print(f"Initializing BookRAG with model: {embedding_model}")

        # Load the embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        print(f"✓ Embedding model loaded (dimension: {self.embedding_dim})")

        # FAISS index (will be created when ingesting chunks)
        self.index: faiss.Index = None

        # Store the original text chunks
        self.chunks: List[str] = []

        # Metadata
        self.book_id: str = None
        self.is_indexed: bool = False

    def ingest_chunks(self, chunks: List[str], book_id: str) -> None:
        """
        Ingest text chunks and create FAISS index.

        Args:
            chunks: List of text chunks from the book
            book_id: Unique identifier for the book
        """
        print(f"\nIngesting {len(chunks)} chunks for book: {book_id}")

        self.book_id = book_id
        self.chunks = chunks

        # Generate embeddings for all chunks
        print("Generating embeddings...")
        embeddings = self.embedding_model.encode(
            chunks,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        # Ensure embeddings are float32 (required by FAISS)
        embeddings = embeddings.astype('float32')

        # Create FAISS index (using L2 distance)
        print(f"Creating FAISS index (dimension={self.embedding_dim})")
        self.index = faiss.IndexFlatL2(self.embedding_dim)

        # Add embeddings to the index
        self.index.add(embeddings)

        self.is_indexed = True
        print(f"✓ Indexed {self.index.ntotal} chunks")

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for relevant chunks using semantic similarity.

        Args:
            query: Search query (e.g., character name or description)
            k: Number of top results to return

        Returns:
            List of dictionaries containing:
                - 'text': The chunk text
                - 'score': Similarity score (lower = more similar)
                - 'index': Position in original chunks list

        Example:
            >>> results = rag.search("Celia Bowen", k=5)
            >>> for r in results:
            ...     print(f"Score: {r['score']:.2f} - {r['text'][:100]}")
        """
        if not self.is_indexed:
            raise ValueError("RAG system not indexed. Call ingest_chunks() first.")

        # Generate embedding for the query
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True
        ).astype('float32')

        # Search the FAISS index
        distances, indices = self.index.search(query_embedding, k)

        # Format results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):  # Valid index
                results.append({
                    'text': self.chunks[idx],
                    'score': float(dist),
                    'index': int(idx)
                })

        return results

    def find_character_mentions(self, character_name: str, k: int = 10) -> List[str]:
        """
        Find text chunks that mention a specific character.

        This is optimized for character profile synthesis.

        Args:
            character_name: Name of the character
            k: Number of chunks to retrieve

        Returns:
            List of text chunks mentioning the character
        """
        # Search for character mentions
        results = self.search(character_name, k=k)

        # Return just the text chunks
        return [r['text'] for r in results]

    def save_index(self, save_dir: str) -> str:
        """
        Save the FAISS index and chunks to disk.

        Args:
            save_dir: Directory to save the index

        Returns:
            Path to the saved index file
        """
        if not self.is_indexed:
            raise ValueError("Cannot save: RAG system not indexed yet.")

        os.makedirs(save_dir, exist_ok=True)

        # Save FAISS index
        index_path = os.path.join(save_dir, f"{self.book_id}.faiss")
        faiss.write_index(self.index, index_path)

        # Save chunks and metadata
        metadata_path = os.path.join(save_dir, f"{self.book_id}.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'book_id': self.book_id,
                'embedding_dim': self.embedding_dim
            }, f)

        print(f"✓ Index saved to {index_path}")
        return index_path

    def load_index(self, load_dir: str, book_id: str) -> None:
        """
        Load a previously saved FAISS index.

        Args:
            load_dir: Directory containing the saved index
            book_id: Book ID to load
        """
        # Load FAISS index
        index_path = os.path.join(load_dir, f"{book_id}.faiss")
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found: {index_path}")

        self.index = faiss.read_index(index_path)

        # Load chunks and metadata
        metadata_path = os.path.join(load_dir, f"{book_id}.pkl")
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)

        self.chunks = metadata['chunks']
        self.book_id = metadata['book_id']
        self.is_indexed = True

        print(f"✓ Loaded index for book: {book_id} ({self.index.ntotal} chunks)")

    def get_stats(self) -> Dict:
        """
        Get statistics about the RAG system.

        Returns:
            Dictionary with index statistics
        """
        return {
            'book_id': self.book_id,
            'is_indexed': self.is_indexed,
            'total_chunks': len(self.chunks),
            'indexed_vectors': self.index.ntotal if self.index else 0,
            'embedding_dim': self.embedding_dim
        }


if __name__ == "__main__":
    # Test the RAG system
    print("Custom RAG System - Test Mode")
    print("=" * 60)

    # Create a test RAG instance
    rag = BookRAG()

    # Test with sample chunks
    test_chunks = [
        "Celia Bowen was born with magic in her blood. Her father, Prospero, trained her from childhood.",
        "Marco Alisdair studied under the mysterious man in the grey suit. He learned to manipulate reality.",
        "The Night Circus appeared without warning. Its black and white stripes were visible for miles.",
        "Celia performed in the circus as the illusionist. Her acts defied explanation.",
        "Marco worked behind the scenes, creating impossible venues and fantastical displays.",
    ]

    # Ingest the test chunks
    rag.ingest_chunks(test_chunks, book_id="test_book")

    # Test search
    print("\n" + "=" * 60)
    print("Testing search for 'Celia Bowen':")
    results = rag.search("Celia Bowen", k=3)
    for i, r in enumerate(results, 1):
        print(f"\n{i}. Score: {r['score']:.2f}")
        print(f"   Text: {r['text'][:80]}...")

    # Test character mentions
    print("\n" + "=" * 60)
    print("Finding mentions of 'Marco':")
    mentions = rag.find_character_mentions("Marco", k=2)
    for i, mention in enumerate(mentions, 1):
        print(f"\n{i}. {mention}")

    # Show stats
    print("\n" + "=" * 60)
    print("RAG Statistics:")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
