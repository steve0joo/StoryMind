"""
Quick script to check if Imagen API is accessible
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*60)
print("CHECKING IMAGEN 3 SETUP")
print("="*60)

# Check environment variables
print("\n1. Checking environment variables...")
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if project_id:
    print(f"   ✓ GOOGLE_CLOUD_PROJECT: {project_id}")
else:
    print("   ✗ GOOGLE_CLOUD_PROJECT not set in .env")

if creds_path:
    print(f"   ✓ GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")
    # Check if file exists
    full_path = os.path.join(os.path.dirname(__file__), creds_path)
    if os.path.exists(full_path):
        print(f"   ✓ Credentials file exists at: {full_path}")
    elif os.path.exists(creds_path):
        print(f"   ✓ Credentials file exists at: {creds_path}")
    else:
        print(f"   ✗ Credentials file NOT found")
        print(f"      Tried: {full_path}")
else:
    print("   ✗ GOOGLE_APPLICATION_CREDENTIALS not set in .env")

# Try to import required libraries
print("\n2. Checking Python libraries...")
try:
    import google.cloud.aiplatform as aiplatform
    print("   ✓ google.cloud.aiplatform installed")
    print(f"      Version: {aiplatform.__version__}")
except ImportError:
    print("   ✗ google.cloud.aiplatform NOT installed")
    print("   → Run: pip install google-cloud-aiplatform")
    exit(1)

# Try to initialize Vertex AI
print("\n3. Initializing Vertex AI...")
try:
    if not project_id:
        print("   ✗ Cannot initialize without project ID")
        exit(1)

    location = "us-central1"
    aiplatform.init(project=project_id, location=location)
    print(f"   ✓ Vertex AI initialized")
    print(f"      Project: {project_id}")
    print(f"      Location: {location}")
except Exception as e:
    print(f"   ✗ Error initializing Vertex AI: {e}")
    print("\n   Troubleshooting:")
    print("   - Check that GOOGLE_CLOUD_PROJECT is correct")
    print("   - Verify service account key file exists")
    print("   - Make sure Vertex AI API is enabled in Cloud Console")
    exit(1)

# Try to access Imagen model
print("\n4. Checking Imagen 3 model access...")
try:
    from vertexai.preview.vision_models import ImageGenerationModel

    # Try to load Imagen 3
    print("   Attempting to load Imagen 3 model...")
    model = ImageGenerationModel.from_pretrained("imagen-3.0-generate")
    print("   ✓ Imagen 3 model loaded successfully!")
    print("   ✓ YOU HAVE ACCESS TO IMAGEN 3!")
    print("\n   Model details:")
    print(f"      Model: imagen-3.0-generate-001")
    print(f"      Ready for image generation")

    success = True

except Exception as e:
    error_msg = str(e)
    print(f"   ✗ Cannot access Imagen 3")
    print(f"      Error: {error_msg[:200]}")

    # Provide specific troubleshooting
    if "403" in error_msg or "permission" in error_msg.lower():
        print("\n   ISSUE: Permission denied")
        print("   → Enable Vertex AI API in Cloud Console")
        print("   → Check service account has 'Vertex AI User' role")
        print("   → Make sure billing is enabled")
    elif "404" in error_msg or "not found" in error_msg.lower():
        print("\n   ISSUE: Model not found")
        print("   → Imagen 3 might not be available in your region")
        print("   → Try us-central1 region")
        print("   → Check if you have access to Imagen in Vertex AI")
    elif "quota" in error_msg.lower():
        print("\n   ISSUE: Quota exceeded")
        print("   → Check quota limits in Cloud Console")
        print("   → Request quota increase if needed")
    else:
        print("\n   ISSUE: Unknown error")
        print("   → Check that Vertex AI API is enabled")
        print("   → Verify billing is active")
        print("   → Try visiting Vertex AI in Cloud Console manually")

    success = False

print("\n" + "="*60)
if success:
    print("✅ ALL CHECKS PASSED - READY FOR IMAGEN 3!")
else:
    print("⚠️  SETUP INCOMPLETE - SEE ERRORS ABOVE")
print("="*60)
