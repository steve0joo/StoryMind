#!/usr/bin/env python3
"""
Test Image Generation with Imagen 3

This script tests the complete image generation pipeline:
1. Create a test character profile
2. Generate image using Imagen 3
3. Verify the image was created
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_image_generation():
    print("=" * 70)
    print("  TESTING IMAGE GENERATION WITH IMAGEN 3")
    print("=" * 70)

    # Step 1: Check environment
    print("\n1. Checking environment...")

    if not os.getenv("GOOGLE_API_KEY"):
        print("   ❌ GOOGLE_API_KEY not set")
        return False

    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("   ❌ GOOGLE_CLOUD_PROJECT not set")
        return False

    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("   ❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        return False

    print("   ✅ All environment variables set")

    # Step 2: Test imports
    print("\n2. Testing imports...")
    try:
        from services.image_service import ImageGenerator
        from utils.seed_generator import generate_character_seed
        print("   ✅ Image service imported successfully")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

    # Step 3: Create test character profile
    print("\n3. Creating test character profile...")

    test_character = {
        'name': 'Harry Potter',
        'description': 'A young wizard with messy black hair, round glasses, and a lightning-shaped scar on his forehead. He has bright green eyes and wears a Gryffindor scarf.',
        'seed': generate_character_seed('Harry Potter')
    }

    print(f"   Character: {test_character['name']}")
    print(f"   Seed: {test_character['seed']}")
    print(f"   Description: {test_character['description'][:100]}...")

    # Step 4: Initialize ImageGenerator
    print("\n4. Initializing Imagen 3 generator...")
    try:
        generator = ImageGenerator()
        print("   ✅ ImageGenerator initialized")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False

    # Step 5: Generate image
    print("\n5. Generating image (this may take 15-30 seconds)...")
    print("   ⏳ Calling Imagen 3 API...")

    try:
        result = generator.generate_character_image(
            character_profile=test_character,
            style="photorealistic portrait, detailed, high quality",
            aspect_ratio="1:1"
        )

        print("   ✅ Image generated successfully!")
        print(f"\n   Results:")
        print(f"   - Image URL: {result['image_url']}")
        print(f"   - Generation time: {result['generation_time_ms']}ms")
        print(f"   - Seed used: {result['seed']}")
        print(f"   - Prompt: {result['prompt'][:100]}...")

        # Step 6: Verify file exists
        if result['image_url'].startswith('/static/'):
            file_path = result['image_url'].replace('/static/', 'static/')
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"   - File exists: {file_path}")
                print(f"   - File size: {file_size:,} bytes")
            else:
                print(f"   ⚠️  File not found at: {file_path}")

        return True

    except Exception as e:
        print(f"   ❌ Image generation failed!")
        print(f"   Error: {str(e)}")
        print(f"\n   This could mean:")
        print(f"   - Vertex AI API not enabled in Google Cloud Console")
        print(f"   - Service account lacks permissions")
        print(f"   - Billing not active")
        print(f"   - Network/authentication issue")
        return False

if __name__ == "__main__":
    print("\n")
    success = test_image_generation()

    print("\n" + "=" * 70)
    if success:
        print("✅ IMAGE GENERATION TEST PASSED!")
        print("\nYour Imagen 3 setup is working correctly.")
        print("You can now:")
        print("  1. Run the demo prep script: python3 scripts/demo_prep.py")
        print("  2. Upload books via API and generate character images")
    else:
        print("❌ IMAGE GENERATION TEST FAILED")
        print("\nTroubleshooting steps:")
        print("  1. Check Vertex AI API is enabled in Google Cloud Console")
        print("  2. Verify billing is active")
        print("  3. Ensure service account has 'Vertex AI User' role")
        print("  4. Run: python3 check_imagen.py for detailed diagnostics")

    print("=" * 70 + "\n")

    sys.exit(0 if success else 1)