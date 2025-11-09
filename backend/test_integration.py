"""
Integration Tests for StoryMind Backend
Tests all endpoints, imports, and core functionality
"""

import os
import sys

# Set up path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("StoryMind Backend - Integration Test Suite")
print("=" * 70)
print()

# Test 1: Environment Variables
print("Test 1: Checking environment variables...")
from dotenv import load_dotenv
load_dotenv()

required_env_vars = [
    'GOOGLE_API_KEY',
    'GOOGLE_CLOUD_PROJECT',
    'FLASK_SECRET_KEY',
    'DATABASE_URL'
]

env_check_passed = True
for var in required_env_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if 'KEY' in var or 'SECRET' in var:
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value
        print(f"  ✓ {var}: {display_value}")
    else:
        print(f"  ✗ {var}: NOT SET")
        env_check_passed = False

if env_check_passed:
    print("  ✓ All required environment variables are set\n")
else:
    print("  ⚠ Some environment variables are missing\n")

# Test 2: Core Imports
print("Test 2: Testing core imports...")
imports_passed = True
try:
    from app import app, logger
    print("  ✓ Flask app imported")

    from models import Book, Character, GeneratedImage, get_db
    print("  ✓ Database models imported")

    from services.document_processor import process_book
    print("  ✓ Document processor imported")

    from services.rag_system import BookRAG
    print("  ✓ RAG system imported")

    from services.character_service import CharacterExtractor
    print("  ✓ Character service imported")

    # Image service is optional (requires Vertex AI setup)
    try:
        from services.image_service import ImageGenerator
        print("  ✓ Image service imported")
    except ImportError as img_err:
        print(f"  ⚠ Image service import failed (optional): {img_err}")
        print("    Note: Imagen 3 requires Vertex AI SDK and credentials")

    from routes.books_routes import books_bp
    print("  ✓ Books routes imported")

    from routes.characters_routes import characters_bp
    print("  ✓ Characters routes imported")

    print("  ✓ Core imports successful\n")
except ImportError as e:
    print(f"  ✗ Import failed: {e}\n")
    imports_passed = False

# Test 3: Database Connection
print("Test 3: Testing database connection...")
if imports_passed:
    try:
        db = get_db()

        # Test query
        book_count = db.query(Book).count()
        character_count = db.query(Character).count()
        image_count = db.query(GeneratedImage).count()

        print(f"  ✓ Database connected")
        print(f"  ✓ Books in database: {book_count}")
        print(f"  ✓ Characters in database: {character_count}")
        print(f"  ✓ Generated images in database: {image_count}")

        db.close()
        print("  ✓ Database connection test passed\n")
        db_passed = True
    except Exception as e:
        print(f"  ✗ Database test failed: {e}\n")
        db_passed = False
else:
    print("  ⊘ Skipped (imports failed)\n")
    db_passed = False

# Test 4: Flask App Configuration
print("Test 4: Testing Flask app configuration...")
if imports_passed:
    try:
        print(f"  ✓ App name: {app.name}")
        print(f"  ✓ Debug mode: {app.config.get('DEBUG', False)}")
        print(f"  ✓ Max upload size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024)}MB")
        print(f"  ✓ Upload folder: {app.config['UPLOAD_FOLDER']}")

        # Check if blueprints are registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        print(f"  ✓ Registered blueprints: {blueprint_names}")

        if 'books' in blueprint_names and 'characters' in blueprint_names:
            print("  ✓ All required blueprints registered\n")
            app_config_passed = True
        else:
            print("  ✗ Missing required blueprints\n")
            app_config_passed = False
    except Exception as e:
        print(f"  ✗ App configuration test failed: {e}\n")
        app_config_passed = False
else:
    print("  ⊘ Skipped (imports failed)\n")
    app_config_passed = False

# Test 5: API Endpoints (using test client)
print("Test 5: Testing API endpoints...")
if imports_passed and app_config_passed:
    try:
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/api/health')
            if response.status_code == 200:
                print(f"  ✓ GET /api/health: {response.status_code}")
            else:
                print(f"  ✗ GET /api/health: {response.status_code}")

            # Test books list endpoint
            response = client.get('/api/books')
            if response.status_code == 200:
                data = response.get_json()
                print(f"  ✓ GET /api/books: {response.status_code} (found {data.get('total', 0)} books)")
            else:
                print(f"  ✗ GET /api/books: {response.status_code}")

            # Test characters list endpoint
            response = client.get('/api/characters/')
            if response.status_code == 200:
                data = response.get_json()
                print(f"  ✓ GET /api/characters/: {response.status_code} (found {data.get('count', 0)} characters)")
            else:
                print(f"  ✗ GET /api/characters/: {response.status_code}")

            # Test characters health endpoint
            response = client.get('/api/characters/health')
            if response.status_code == 200:
                data = response.get_json()
                print(f"  ✓ GET /api/characters/health: {response.status_code} ({data.get('status', 'unknown')})")
            else:
                print(f"  ✗ GET /api/characters/health: {response.status_code}")

            # Test 404 handling
            response = client.get('/api/nonexistent')
            if response.status_code == 404:
                print(f"  ✓ 404 error handling works")
            else:
                print(f"  ✗ 404 error handling: expected 404, got {response.status_code}")

        print("  ✓ All endpoint tests completed\n")
        endpoints_passed = True
    except Exception as e:
        print(f"  ✗ Endpoint tests failed: {e}\n")
        import traceback
        traceback.print_exc()
        endpoints_passed = False
else:
    print("  ⊘ Skipped (previous tests failed)\n")
    endpoints_passed = False

# Test 6: Logging System
print("Test 6: Testing logging system...")
if imports_passed:
    try:
        import logging

        # Check if logs directory exists
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        if os.path.exists(log_dir):
            print(f"  ✓ Logs directory exists: {log_dir}")
        else:
            print(f"  ⚠ Logs directory not found (will be created on first run)")

        # Test logger
        test_logger = logging.getLogger('test')
        test_logger.info("Test log message")
        print("  ✓ Logger working")

        # Check log file
        log_file = os.path.join(log_dir, 'storymind.log')
        if os.path.exists(log_file):
            file_size = os.path.getsize(log_file)
            print(f"  ✓ Log file exists: {log_file} ({file_size} bytes)")
        else:
            print(f"  ⚠ Log file not created yet (will be created on first request)")

        print("  ✓ Logging system test passed\n")
        logging_passed = True
    except Exception as e:
        print(f"  ✗ Logging test failed: {e}\n")
        logging_passed = False
else:
    print("  ⊘ Skipped (imports failed)\n")
    logging_passed = False

# Test 7: Required Directories
print("Test 7: Testing required directories...")
try:
    required_dirs = [
        'static/uploads/books',
        'static/uploads/images',
        'static/faiss_indices',
        'data'
    ]

    all_dirs_exist = True
    for dir_path in required_dirs:
        full_path = os.path.join(os.path.dirname(__file__), dir_path)
        if os.path.exists(full_path):
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ⚠ {dir_path} (will be created on first use)")
            all_dirs_exist = False

    if all_dirs_exist:
        print("  ✓ All directories exist\n")
    else:
        print("  ⚠ Some directories missing (will be auto-created)\n")

    dirs_passed = True
except Exception as e:
    print(f"  ✗ Directory test failed: {e}\n")
    dirs_passed = False

# Summary
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)

tests = [
    ("Environment Variables", env_check_passed),
    ("Core Imports", imports_passed),
    ("Database Connection", db_passed),
    ("Flask App Configuration", app_config_passed),
    ("API Endpoints", endpoints_passed),
    ("Logging System", logging_passed),
    ("Required Directories", dirs_passed)
]

passed_count = sum(1 for _, passed in tests if passed)
total_count = len(tests)

for test_name, passed in tests:
    status = "✓ PASSED" if passed else "✗ FAILED"
    print(f"{test_name:.<50} {status}")

print()
print(f"Results: {passed_count}/{total_count} tests passed")

if passed_count == total_count:
    print()
    print("🎉 ALL TESTS PASSED! Backend is ready to use.")
    print()
    print("Next steps:")
    print("  1. Start the server: python app.py")
    print("  2. Test with a PDF upload via frontend or Postman")
    print("  3. Check logs at: backend/logs/storymind.log")
    sys.exit(0)
else:
    print()
    print("⚠️  Some tests failed. Please review the errors above.")
    print()
    print("Common fixes:")
    print("  - Missing environment variables: Check backend/.env file")
    print("  - Import errors: Run 'pip install -r requirements.txt'")
    print("  - Database errors: Run 'python init_db.py'")
    sys.exit(1)
