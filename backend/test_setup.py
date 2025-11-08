"""
Setup Validation Script
Validates that all dependencies and APIs are configured correctly
Run this before starting hackathon to catch issues early
"""

import sys
import os

def test_imports():
    """Test that all required packages are installed"""
    print("\n🔍 Testing Python package imports...")

    packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'langchain': 'LangChain',
        'langchain_google_genai': 'LangChain Google GenAI',
        'faiss': 'FAISS',
        'sentence_transformers': 'Sentence Transformers',
        'google.generativeai': 'Google Generative AI',
        'sqlalchemy': 'SQLAlchemy',
        'dotenv': 'Python Dotenv',
        'pydantic': 'Pydantic',
        'numpy': 'NumPy',
        'requests': 'Requests'
    }

    failed = []
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name} - {e}")
            failed.append(name)

    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("✅ All packages installed correctly")
    return True

def test_environment_variables():
    """Test that required environment variables are set"""
    print("\n🔍 Testing environment variables...")

    from dotenv import load_dotenv
    load_dotenv()

    required_vars = {
        'GOOGLE_API_KEY': 'Google API Key for Gemini & Imagen'
    }

    optional_vars = {
        'FLASK_SECRET_KEY': 'Flask secret key',
        'DATABASE_URL': 'Database URL',
        'ALLOWED_ORIGINS': 'CORS allowed origins'
    }

    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var} ({description})")
        else:
            print(f"  ✗ {var} ({description}) - NOT SET")
            missing.append(var)

    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var} ({description})")
        else:
            print(f"  ⚠ {var} ({description}) - not set (optional)")

    if missing:
        print(f"\n❌ Missing required environment variables: {', '.join(missing)}")
        print("Create a .env file in the backend directory with these variables")
        return False

    print("✅ Required environment variables set")
    return True

def test_gemini_api():
    """Test Gemini API connection"""
    print("\n🔍 Testing Gemini API...")

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("  ✗ GOOGLE_API_KEY not set")
            return False

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",  # or "gemini-1.5-flash" if exp not available
            google_api_key=api_key,
            temperature=0
        )

        response = llm.invoke("Say 'Hello from Gemini!' and nothing else.")
        print(f"  ✓ Gemini API connected: {response.content}")
        return True

    except Exception as e:
        print(f"  ✗ Gemini API failed: {e}")
        return False

def test_faiss():
    """Test FAISS installation"""
    print("\n🔍 Testing FAISS...")

    try:
        import faiss
        import numpy as np

        # Create a simple index
        dimension = 384  # all-MiniLM-L6-v2 dimension
        index = faiss.IndexFlatL2(dimension)

        # Add some random vectors
        test_vectors = np.random.random((10, dimension)).astype('float32')
        index.add(test_vectors)

        # Search
        query = np.random.random((1, dimension)).astype('float32')
        distances, indices = index.search(query, k=5)

        print(f"  ✓ FAISS working - indexed {index.ntotal} vectors")
        return True

    except Exception as e:
        print(f"  ✗ FAISS failed: {e}")
        return False

def test_sqlite():
    """Test SQLite database"""
    print("\n🔍 Testing SQLite...")

    try:
        import sqlite3

        # Test in-memory database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('SELECT sqlite_version()')
        version = cursor.fetchone()[0]
        print(f"  ✓ SQLite working - version {version}")
        conn.close()
        return True

    except Exception as e:
        print(f"  ✗ SQLite failed: {e}")
        return False

def test_sentence_transformers():
    """Test sentence transformers for embeddings"""
    print("\n🔍 Testing Sentence Transformers...")

    try:
        from sentence_transformers import SentenceTransformer

        # This will download the model on first run
        print("  Loading model (this may take a moment on first run)...")
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Test encoding
        test_text = ["This is a test sentence."]
        embeddings = model.encode(test_text)

        print(f"  ✓ Sentence Transformers working - embedding dimension: {embeddings.shape[1]}")
        return True

    except Exception as e:
        print(f"  ✗ Sentence Transformers failed: {e}")
        return False

def test_langchain_loaders():
    """Test LangChain document loaders"""
    print("\n🔍 Testing LangChain document loaders...")

    try:
        from langchain_community.document_loaders import UnstructuredPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        print("  ✓ UnstructuredPDFLoader imported (from langchain-community)")
        print("  ✓ RecursiveCharacterTextSplitter imported")
        print("  ⚠ PDF loading will be tested when you upload a book")
        return True

    except Exception as e:
        print(f"  ✗ LangChain loaders failed: {e}")
        print("  → Try: pip install langchain-community")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("=" * 60)
    print("StoryMind Setup Validation")
    print("=" * 60)

    tests = [
        ("Package Imports", test_imports),
        ("Environment Variables", test_environment_variables),
        ("SQLite Database", test_sqlite),
        ("FAISS Vector Store", test_faiss),
        ("Sentence Transformers", test_sentence_transformers),
        ("LangChain Loaders", test_langchain_loaders),
        ("Gemini API", test_gemini_api),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All systems go! Ready for hackathon!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Fix issues before starting.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
