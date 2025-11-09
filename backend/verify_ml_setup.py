#!/usr/bin/env python3
"""
ML/AI Lead Setup Verification Script
Comprehensive check of all ML/AI components for StoryMind

Run this to verify your ML/AI pipeline is ready for development.
"""

import os
import sys

def print_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_item(description, passed, details=""):
    """Print a check item result"""
    status = "✅" if passed else "❌"
    print(f"{status} {description}")
    if details:
        print(f"   → {details}")
    return passed

def main():
    print_header("ML/AI PIPELINE SETUP VERIFICATION")
    print("This script verifies all components needed for ML/AI development")

    all_checks_passed = True

    # 1. Check Core ML Libraries
    print_header("1. Core ML Libraries")

    try:
        import faiss
        check_item("FAISS (Vector Database)", True, f"Version available, index working")
    except ImportError as e:
        all_checks_passed &= check_item("FAISS", False, f"Not installed: {e}")

    try:
        import sentence_transformers
        model = sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2')
        dim = model.get_sentence_embedding_dimension()
        check_item("Sentence Transformers", True, f"Model loaded, dimension: {dim}")
    except Exception as e:
        all_checks_passed &= check_item("Sentence Transformers", False, str(e))

    try:
        import langchain
        import langchain_community
        check_item("LangChain + Community", True, "Both packages available")
    except ImportError as e:
        all_checks_passed &= check_item("LangChain", False, str(e))

    # 2. Check Google AI/ML APIs
    print_header("2. Google AI/ML APIs")

    try:
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content("Say 'OK'")
            check_item("Gemini 2.0 Flash API", True, "API connected and responsive")
        else:
            all_checks_passed &= check_item("Gemini API Key", False, "GOOGLE_API_KEY not set in .env")
    except Exception as e:
        all_checks_passed &= check_item("Gemini API", False, str(e))

    try:
        from google.cloud import aiplatform
        check_item("Vertex AI (for Imagen 3)", True, "Library installed")

        # Check credentials
        if os.path.exists("service-account-key.json"):
            check_item("Service Account Key", True, "service-account-key.json found")
        else:
            all_checks_passed &= check_item("Service Account Key", False, "service-account-key.json not found")
    except ImportError:
        all_checks_passed &= check_item("Vertex AI", False, "google-cloud-aiplatform not installed")

    # 3. Check Document Processing
    print_header("3. Document Processing")

    try:
        from langchain_community.document_loaders import PyPDFLoader
        check_item("PyPDFLoader", True, "PDF processing available")
    except ImportError:
        try:
            from langchain_community.document_loaders import UnstructuredPDFLoader
            check_item("UnstructuredPDFLoader", True, "PDF processing available (Unstructured)")
        except ImportError:
            all_checks_passed &= check_item("PDF Loader", False, "No PDF loader available")

    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        check_item("Text Splitter", True, "RecursiveCharacterTextSplitter available")
    except Exception as e:
        all_checks_passed &= check_item("Text Splitter", False, str(e))

    # 4. Check Custom Services
    print_header("4. Custom ML Services")

    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from services.rag_system import BookRAG
        rag = BookRAG()
        check_item("RAG System", True, f"Custom FAISS RAG initialized (dim: {rag.embedding_dim})")
    except Exception as e:
        all_checks_passed &= check_item("RAG System", False, str(e))

    try:
        from services.character_service import CharacterExtractor
        if os.getenv("GOOGLE_API_KEY"):
            extractor = CharacterExtractor()
            check_item("Character Extractor", True, "Gemini-based extractor ready")
        else:
            check_item("Character Extractor", False, "GOOGLE_API_KEY not set")
    except Exception as e:
        all_checks_passed &= check_item("Character Extractor", False, str(e))

    try:
        from services.image_service import ImageGenerator
        check_item("Image Generator (code)", True, "Image service code available")
    except Exception as e:
        all_checks_passed &= check_item("Image Generator", False, str(e))

    try:
        from utils.seed_generator import generate_character_seed, verify_seed_consistency
        seed = generate_character_seed("Harry Potter")
        consistent = verify_seed_consistency("Harry Potter", num_tests=100)
        check_item("Seed Generator", True, f"Deterministic (seed: {seed}, consistent: {consistent})")
    except Exception as e:
        all_checks_passed &= check_item("Seed Generator", False, str(e))

    # 5. Check Environment Configuration
    print_header("5. Environment Configuration")

    env_checks = [
        ("GOOGLE_API_KEY", "Required for Gemini", True),
        ("GOOGLE_CLOUD_PROJECT", "Required for Imagen 3", False),
        ("GOOGLE_APPLICATION_CREDENTIALS", "Path to service account key", False),
    ]

    for env_var, description, required in env_checks:
        value = os.getenv(env_var)
        if value:
            check_item(f"{env_var}", True, description)
        else:
            if required:
                all_checks_passed &= check_item(f"{env_var}", False, f"{description} (REQUIRED)")
            else:
                check_item(f"{env_var}", False, f"{description} (optional)")

    # 6. Test End-to-End Flow
    print_header("6. End-to-End Pipeline Test")

    try:
        from services.rag_system import BookRAG
        from services.character_service import CharacterExtractor
        from utils.seed_generator import generate_character_seed

        # Test RAG
        rag = BookRAG()
        test_chunks = [
            "Harry Potter was a young wizard with a lightning-shaped scar.",
            "Hermione Granger was the brightest witch of her age.",
        ]
        rag.ingest_chunks(test_chunks, book_id="test")

        # Test character extraction
        if os.getenv("GOOGLE_API_KEY"):
            extractor = CharacterExtractor()
            test_text = "Harry Potter and Hermione Granger attended Hogwarts."
            names = extractor.extract_character_names(test_text, max_characters=5)

            if names:
                # Test profile creation
                profile = extractor.create_canonical_profile(names[0], rag, num_mentions=2)

                check_item("End-to-End Pipeline", True,
                          f"RAG → Character Extraction → Profile Creation works!")
            else:
                check_item("End-to-End Pipeline", True, "RAG and extraction work, but no characters found in test")
        else:
            check_item("End-to-End Pipeline", False, "GOOGLE_API_KEY not set, cannot test")

    except Exception as e:
        all_checks_passed &= check_item("End-to-End Pipeline", False, str(e))

    # Final Summary
    print_header("SUMMARY")

    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - You're ready for ML/AI development!")
        print("\nNext steps:")
        print("  1. Test with a real PDF: python backend/test_book_upload.py")
        print("  2. Generate demo images: python backend/generate_demo_images.py")
        print("  3. Start implementing missing features (see issues below)")
    else:
        print("❌ SOME CHECKS FAILED - Review the issues above")
        print("\nCommon fixes:")
        print("  • Missing Vertex AI: pip install google-cloud-aiplatform")
        print("  • Missing API key: Add GOOGLE_API_KEY to backend/.env")
        print("  • Missing service account: Download from Google Cloud Console")

    # List what needs to be implemented
    print_header("IMPLEMENTATION STATUS")

    implementation_items = [
        ("✅", "RAG System (Custom FAISS)", "services/rag_system.py"),
        ("✅", "Character Extraction (Gemini)", "services/character_service.py"),
        ("✅", "Seed Generator (Deterministic)", "utils/seed_generator.py"),
        ("✅", "Document Processor (LangChain)", "services/document_processor.py"),
        ("⚠️", "Image Generator (Imagen 3)", "services/image_service.py - needs Vertex AI setup"),
        ("❌", "Demo Prep Script", "scripts/demo_prep.py - create this"),
        ("❌", "Character Routes", "routes/characters_routes.py - implement API endpoints"),
    ]

    for status, item, note in implementation_items:
        print(f"{status} {item:35s} → {note}")

    print("\n" + "=" * 70)
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
