"""
Basic Backend Tests - Test 1 and Test 2
Tests imports and database models
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test 1: Can we import our modules?"""
    print("\n📦 Test 1: Testing imports...")
    try:
        from app import app
        print("   ✅ Flask app imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import Flask app: {e}")
        return False

    try:
        from models import Book, Character, GeneratedImage, get_db, init_db
        print("   ✅ Database models imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import models: {e}")
        return False

    return True


def test_database_models():
    """Test 2: Can we create database models?"""
    print("\n🗄️  Test 2: Testing database models...")
    try:
        from models import Book, Character, GeneratedImage, init_db

        # Initialize database
        init_db()
        print("   ✅ Database initialized successfully")

        # Test creating model instances (not saving to DB yet)
        book = Book(title="Test Book", author="Test Author")
        print(f"   ✅ Book model created: {book.title}")

        character = Character(
            book_id="test-123",
            name="Test Character",
            canonical_description="A test character",
            seed=12345
        )
        print(f"   ✅ Character model created: {character.name}")

        image = GeneratedImage(
            character_id="char-123",
            prompt="Test prompt",
            style="realistic",
            image_url="/static/test.jpg"
        )
        print(f"   ✅ GeneratedImage model created")

        # Test to_dict() methods
        book_dict = book.to_dict()
        print(f"   ✅ Book.to_dict() works: {book_dict['title']}")

        return True

    except Exception as e:
        print(f"   ❌ Database model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 RUNNING BASIC TESTS (Test 1 & 2)")
    print("=" * 60)

    # Run tests
    test1_result = test_imports()
    test2_result = test_database_models()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"{'✅ PASS' if test1_result else '❌ FAIL'} - Test 1: Imports")
    print(f"{'✅ PASS' if test2_result else '❌ FAIL'} - Test 2: Database Models")

    if test1_result and test2_result:
        print("\n🎉 Both tests passed!")
    else:
        print("\n⚠️  Some tests failed.")
    print("=" * 60)
