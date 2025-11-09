#!/usr/bin/env python3
"""
Test TXT and EPUB File Processing
Tests the complete pipeline for non-PDF book formats
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from services.document_processor import process_book
from services.rag_system import BookRAG
from services.character_service import CharacterExtractor


def test_txt_file():
    """Test TXT file processing"""
    print("\n" + "="*70)
    print("  TEST 1: TXT FILE PROCESSING (Fablehaven)")
    print("="*70)

    txt_file = "static/uploads/books/fablehaven_text.txt"

    # Step 1: Document processing
    print("\n1. Processing TXT file...")
    result = process_book(txt_file)
    print(f"   ✓ Processed {result['total_chunks']} chunks")
    print(f"   ✓ Total characters: {result['total_chars']:,}")

    # Step 2: RAG system
    print("\n2. Creating FAISS index...")
    rag = BookRAG()
    rag.ingest_chunks(result['chunks'], "fablehaven_text")
    print(f"   ✓ FAISS index created")

    # Step 3: Character extraction
    print("\n3. Extracting characters with Gemini...")
    extractor = CharacterExtractor()

    # Use first 50k characters for character extraction
    sample_text = "".join(result['chunks'][:50])[:50000]
    character_names = extractor.extract_character_names(sample_text)
    print(f"   ✓ Extracted {len(character_names)} characters:")
    for name in character_names[:5]:  # Show first 5
        print(f"      - {name}")

    # Step 4: Test character profile generation
    if character_names:
        print("\n4. Testing character profile generation...")
        test_char = character_names[0]
        print(f"   Testing with: {test_char}")

        # Get mentions from RAG
        mentions = rag.get_character_mentions(test_char, top_k=5)
        print(f"   ✓ Retrieved {len(mentions)} mentions from RAG")

        # Create profile
        profile = extractor.create_character_profile(test_char, mentions)
        print(f"   ✓ Profile created")
        print(f"      Name: {profile['name']}")
        print(f"      Description: {profile['description'][:100]}...")
        print(f"      Seed: {profile['seed']}")

    print("\n✅ TXT file processing: SUCCESS")
    return True


def test_epub_file():
    """Test EPUB file processing"""
    print("\n" + "="*70)
    print("  TEST 2: EPUB FILE PROCESSING (Fablehaven)")
    print("="*70)

    epub_file = os.path.join(os.path.dirname(__file__), "static/uploads/books/Fablehaven -- Brandon Mull, Teacher's  Guide -- April 24, 2007 -- Aladdin -- 9781416947202 -- 201a62c7b4b56762f1e30f85e88aed42 -- Anna's Archive.epub")

    # Step 1: Document processing
    print("\n1. Processing EPUB file...")
    try:
        result = process_book(epub_file)
        print(f"   ✓ Processed {result['total_chunks']} chunks")
        print(f"   ✓ Total characters: {result['total_chars']:,}")
    except Exception as e:
        print(f"   ✗ EPUB processing failed: {e}")
        print("\n⚠️  EPUB support may require additional dependencies")
        print("   Install with: pip install unstructured[epub]")
        return False

    # Step 2: RAG system
    print("\n2. Creating FAISS index...")
    rag = BookRAG()
    rag.ingest_chunks(result['chunks'], "fablehaven_epub")
    print(f"   ✓ FAISS index created")

    # Step 3: Character extraction
    print("\n3. Extracting characters with Gemini...")
    extractor = CharacterExtractor()

    # Use first 50k characters for character extraction
    sample_text = "".join(result['chunks'][:50])[:50000]
    character_names = extractor.extract_character_names(sample_text)
    print(f"   ✓ Extracted {len(character_names)} characters:")
    for name in character_names[:5]:  # Show first 5
        print(f"      - {name}")

    # Step 4: Test character profile generation
    if character_names:
        print("\n4. Testing character profile generation...")
        test_char = character_names[0]
        print(f"   Testing with: {test_char}")

        # Get mentions from RAG
        mentions = rag.get_character_mentions(test_char, top_k=5)
        print(f"   ✓ Retrieved {len(mentions)} mentions from RAG")

        # Create profile
        profile = extractor.create_character_profile(test_char, mentions)
        print(f"   ✓ Profile created")
        print(f"      Name: {profile['name']}")
        print(f"      Description: {profile['description'][:100]}...")
        print(f"      Seed: {profile['seed']}")

    print("\n✅ EPUB file processing: SUCCESS")
    return True


def main():
    print("\n" + "="*70)
    print("  TESTING TXT AND EPUB FILE SUPPORT")
    print("="*70)
    print("\nThis will test the complete ML/AI pipeline with:")
    print("  - TXT file (plain text)")
    print("  - EPUB file (ebook format)")
    print("\nExpected time: 2-3 minutes\n")

    results = {
        'txt': False,
        'epub': False
    }

    # Test TXT
    try:
        results['txt'] = test_txt_file()
    except Exception as e:
        print(f"\n❌ TXT test failed: {e}")
        import traceback
        traceback.print_exc()

    # Test EPUB
    try:
        results['epub'] = test_epub_file()
    except Exception as e:
        print(f"\n❌ EPUB test failed: {e}")
        import traceback
        traceback.print_exc()

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print(f"  TXT Support:  {'✅ PASS' if results['txt'] else '❌ FAIL'}")
    print(f"  EPUB Support: {'✅ PASS' if results['epub'] else '❌ FAIL'}")
    print("="*70)

    if all(results.values()):
        print("\n🎉 All file formats working! Your project supports PDF, EPUB, and TXT!")
    elif results['txt']:
        print("\n✅ TXT support confirmed. EPUB may need additional dependencies.")
    else:
        print("\n⚠️  Some tests failed. Check error messages above.")


if __name__ == "__main__":
    main()
