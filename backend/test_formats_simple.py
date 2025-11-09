#!/usr/bin/env python3
"""
Simple File Format Test (No Gemini API Required)
Tests document processing and RAG for TXT, EPUB, and PDF
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from services.document_processor import process_book
from services.rag_system import BookRAG


def test_format(file_path, format_name):
    """Test a single file format"""
    print(f"\n{'='*70}")
    print(f"  TESTING {format_name} FORMAT")
    print(f"{'='*70}")
    print(f"File: {os.path.basename(file_path)}")

    try:
        # Step 1: Document Processing
        print("\n1. Document Processing...")
        result = process_book(file_path)
        print(f"   ✓ Processed {result['total_chunks']} chunks")
        print(f"   ✓ Total characters: {result['total_chars']:,}")
        print(f"   ✓ File type: {result['metadata']['file_type']}")

        # Step 2: RAG System (FAISS Index)
        print("\n2. RAG System (FAISS Index)...")
        rag = BookRAG()
        rag.ingest_chunks(result['chunks'], f"test_{format_name.lower()}")
        print(f"   ✓ FAISS index created with {len(result['chunks'])} vectors")

        # Step 3: Test RAG Query
        print("\n3. Testing RAG Search...")
        test_query = "who are the main characters"
        results = rag.search(test_query, k=3)
        print(f"   ✓ Query: '{test_query}'")
        print(f"   ✓ Retrieved {len(results)} results")
        if results:
            print(f"   ✓ First result preview: {results[0]['text'][:100]}...")

        print(f"\n✅ {format_name} FORMAT: SUCCESS")
        return True

    except Exception as e:
        print(f"\n❌ {format_name} FORMAT: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*70)
    print("  FILE FORMAT SUPPORT TEST")
    print("="*70)
    print("\nTesting document processing and RAG for different formats")
    print("(No Gemini API calls - avoiding quota limits)\n")

    base_dir = os.path.dirname(__file__)
    books_dir = os.path.join(base_dir, "static/uploads/books")

    # Test files
    tests = [
        {
            'path': os.path.join(books_dir, "harry-potter-and-the-philosophers-stone-by-jk-rowling.pdf"),
            'name': 'PDF'
        },
        {
            'path': os.path.join(books_dir, "fablehaven_text.txt"),
            'name': 'TXT'
        },
        {
            'path': os.path.join(books_dir, "Fablehaven -- Brandon Mull, Teacher's  Guide -- April 24, 2007 -- Aladdin -- 9781416947202 -- 201a62c7b4b56762f1e30f85e88aed42 -- Anna's Archive.epub"),
            'name': 'EPUB'
        }
    ]

    results = {}

    for test in tests:
        if os.path.exists(test['path']):
            results[test['name']] = test_format(test['path'], test['name'])
        else:
            print(f"\n⚠️  {test['name']} file not found: {os.path.basename(test['path'])}")
            results[test['name']] = False

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    for format_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {format_name:6s} Support: {status}")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    if passed == total:
        print(f"\n🎉 Perfect! All {total} formats working!")
    elif passed > 0:
        print(f"\n✅ {passed}/{total} formats working")
    else:
        print(f"\n❌ No formats working - check errors above")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
