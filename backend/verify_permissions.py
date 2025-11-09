"""
Quick script to verify Imagen 3 permissions are working
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("Verifying Imagen 3 Permissions")
print("=" * 70)
print()

# Step 1: Check environment variables
print("1. Checking environment variables...")
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not project_id:
    print("   ❌ GOOGLE_CLOUD_PROJECT not set in .env")
    sys.exit(1)
if not credentials_file:
    print("   ❌ GOOGLE_APPLICATION_CREDENTIALS not set in .env")
    sys.exit(1)

print(f"   ✓ Project: {project_id}")
print(f"   ✓ Credentials: {credentials_file}")
print()

# Step 2: Check service account file
print("2. Checking service account file...")
import json
try:
    with open(credentials_file) as f:
        sa_data = json.load(f)
        service_account_email = sa_data["client_email"]
        print(f"   ✓ Service Account: {service_account_email}")
        print()
except FileNotFoundError:
    print(f"   ❌ File not found: {credentials_file}")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error reading file: {e}")
    sys.exit(1)

# Step 3: Initialize Vertex AI
print("3. Initializing Vertex AI...")
try:
    from google.cloud import aiplatform
    aiplatform.init(project=project_id, location="us-central1")
    print("   ✓ Vertex AI initialized")
    print()
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Step 4: Load Imagen 3 model
print("4. Loading Imagen 3 model...")
try:
    from vertexai.preview.vision_models import ImageGenerationModel
    model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
    print("   ✓ Imagen 3 model loaded")
    print()
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Step 5: Test image generation
print("5. Testing image generation (this is the critical test)...")
try:
    test_prompt = "a red apple on a white table"
    print(f"   Prompt: {test_prompt}")
    print("   Calling Imagen 3 API...")

    response = model.generate_images(
        prompt=test_prompt,
        number_of_images=1,
        aspect_ratio="1:1",
        safety_filter_level="block_some",
        person_generation="allow_adult",
    )

    if response and response.images:
        print("   ✓ API call successful!")
        print("   ✓ Image generated successfully!")
        print()
        print("=" * 70)
        print("✅ SUCCESS! Imagen 3 is working perfectly!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Run: python services/image_service.py")
        print("  2. Run: python generate_demo_images.py")
        print()
    else:
        print("   ❌ No images returned")
        sys.exit(1)

except Exception as e:
    error_msg = str(e)
    print(f"   ❌ Error: {error_msg}")
    print()

    if "403" in error_msg and "IAM_PERMISSION_DENIED" in error_msg:
        print("=" * 70)
        print("❌ PERMISSION DENIED")
        print("=" * 70)
        print()
        print("The service account doesn't have the required permissions.")
        print()
        print("📋 To fix this:")
        print()
        print("1. Go to: https://console.cloud.google.com/iam-admin/iam?project=storymind-477623")
        print()
        print("2. Find this service account (has robot icon 🤖):")
        print(f"   {service_account_email}")
        print()
        print("3. Click the pencil icon (✏️) to edit")
        print()
        print("4. Click '+ ADD ANOTHER ROLE'")
        print()
        print("5. Search for and select: 'Vertex AI User'")
        print()
        print("6. Click 'SAVE'")
        print()
        print("7. Wait 60 seconds, then run this script again")
        print()
    else:
        print("Unexpected error. Full details above.")

    sys.exit(1)
