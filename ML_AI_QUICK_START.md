# ML/AI Lead - Quick Start Guide

**Your Role:** ML/AI Pipeline Development
**Status:** ✅ 80% Complete - Just needs final integration!

---

## 🚀 Get Started in 5 Minutes

### Step 1: Install Missing Package
```bash
pip install google-cloud-aiplatform vertexai
```

### Step 2: Verify Everything Works
```bash
python3 backend/verify_ml_setup.py
```

**Expected Output:**
```
✅ RAG System
✅ Character Extractor
✅ Seed Generator
✅ Document Processor
✅ End-to-End Pipeline
⚠️ Image Generator (after you install Vertex AI)
```

### Step 3: Test with Real Data
```bash
# Start backend server
cd backend
python3 app.py
# Server runs on http://localhost:5000

# In another terminal, upload a test book
curl -X POST -F "file=@path/to/book.pdf" http://localhost:5000/api/books/upload
```

---

## 📂 What You Built (Already Working!)

### 1. Custom RAG System ✅
**File:** `backend/services/rag_system.py`

**What it does:**
- Converts book text into embeddings (384-dim vectors)
- Stores them in FAISS index for fast semantic search
- Finds character mentions in the book

**Test it:**
```bash
python3 backend/services/rag_system.py
# Should show search results for "Celia Bowen"
```

---

### 2. Character Extraction ✅
**File:** `backend/services/character_service.py`

**What it does:**
- Uses Gemini 2.0 to extract character names from book
- Creates canonical character profiles using RAG + LLM synthesis
- Combines multiple mentions into single description

**Test it:**
```bash
python3 backend/services/character_service.py
# Should extract: Celia Bowen, Marco Alisdair, Prospero
```

---

### 3. Seed Generator (Your Secret Weapon!) ✅
**File:** `backend/utils/seed_generator.py`

**What it does:**
- Generates deterministic seeds from character names
- Same name → same seed → consistent images EVERY TIME
- Uses hashlib.md5() (NOT Python's hash())

**Why it matters:**
This is your competitive advantage! Other teams will struggle with character consistency.

**Test it:**
```bash
python3 backend/utils/seed_generator.py
# Harry Potter → Always 1085936863
```

---

### 4. Document Processor ✅
**File:** `backend/services/document_processor.py`

**What it does:**
- Loads PDF/EPUB files using LangChain
- Splits into 1000-char chunks with 200-char overlap
- Returns processed text ready for RAG

**Test it:**
```bash
python3 backend/services/document_processor.py
# Shows supported formats
```

---

## 🔧 What You Need to Complete

### Priority 1: Image Generation (30 mins)

**File:** `backend/services/image_service.py` (already written!)

**Status:** Code complete, just needs Vertex AI library

**Fix:**
```bash
pip install google-cloud-aiplatform vertexai
python3 backend/check_imagen.py
```

**If check fails:**
1. Go to Google Cloud Console
2. Enable Vertex AI API
3. Enable Imagen API
4. Make sure your service account has permissions

---

### Priority 2: Character API Routes (1 hour)

**File:** `backend/routes/characters_routes.py` (template created!)

**TODO:**
1. Uncomment the image generation code in `generate_character_image()`
2. Test the endpoints:
   ```bash
   # Get all characters for a book
   GET /api/characters?book_id=<id>

   # Generate image for a character
   POST /api/characters/<id>/generate-image
   ```

**Starter code already provided!** Just uncomment the TODO sections.

---

### Priority 3: Demo Prep Script (1-2 hours)

**File:** `backend/scripts/demo_prep.py` (template created!)

**What it should do:**
1. Load 3-5 demo books from `static/uploads/books/`
2. Process each through the full pipeline
3. Generate images for top 5 characters per book
4. Save everything to database

**Why it's critical:**
- Imagen 3 free tier: Only 100 images/day
- Generation time: 15-30 seconds per image
- Network issues during demo = disaster

**TODO:**
- Add your demo books to `backend/static/uploads/books/`
- Uncomment the image generation section
- Run it 2-3 hours before presentation

---

## 🎯 Your Development Workflow

### Daily Development
```bash
# 1. Activate environment
cd backend
source venv/bin/activate  # If you have one

# 2. Check your ML pipeline status
python3 verify_ml_setup.py

# 3. Work on your features
# Edit services/image_service.py, routes/characters_routes.py, etc.

# 4. Test as you go
python3 services/character_service.py
python3 services/rag_system.py

# 5. Test API endpoints
python3 app.py
# Then use curl or Postman to test routes
```

### Before Committing
```bash
# Run full verification
python3 backend/verify_ml_setup.py
python3 backend/test_setup.py

# If all green, commit!
git add .
git commit -m "ML/AI: Implement [feature]"
git push origin ai-rag-pipeline
```

---

## 📊 Architecture Overview

```
User uploads book (PDF)
    ↓
DocumentProcessor (LangChain)
    ↓
text chunks (1000 chars each)
    ↓
RAG System (Custom FAISS)
    ↓
embeddings → vector index
    ↓
CharacterExtractor (Gemini 2.0)
    ↓
character names → ["Harry", "Hermione", "Ron"]
    ↓
FOR EACH CHARACTER:
    RAG.find_mentions("Harry Potter")
        ↓
    ["Harry was a wizard...", "Harry's scar hurt...", ...]
        ↓
    Gemini synthesis
        ↓
    canonical_description: "A young wizard with black hair..."
        ↓
    SeedGenerator(name)
        ↓
    seed: 1085936863 (deterministic!)
        ↓
    ImageGenerator (Imagen 3)
        ↓
    character_image.png
```

---

## 🐛 Common Issues & Solutions

### Issue: "google-cloud-aiplatform not installed"
```bash
pip install google-cloud-aiplatform vertexai
```

### Issue: "Gemini API rate limit exceeded"
**Rate limit:** 15 requests/minute

**Solution:**
```python
import time
for character in characters:
    profile = extractor.create_canonical_profile(character, rag)
    time.sleep(4)  # Wait 4 seconds between requests
```

### Issue: "FAISS dimension mismatch"
**Problem:** Loading an index with different embedding dimensions

**Solution:**
```python
# Always use the same model
rag = BookRAG(embedding_model='all-MiniLM-L6-v2')  # 384 dims
```

### Issue: "Seed not consistent"
**Problem:** Using `hash()` instead of `hashlib.md5()`

**Solution:**
```python
# ❌ WRONG
seed = hash(name) % (2**32)

# ✅ RIGHT
from utils.seed_generator import generate_character_seed
seed = generate_character_seed(name)
```

---

## 📖 Code Examples

### Process a Book End-to-End
```python
from services.document_processor import process_book
from services.rag_system import BookRAG
from services.character_service import CharacterExtractor

# 1. Process PDF
result = process_book("harry_potter.pdf")
print(f"Processed {result['total_chunks']} chunks")

# 2. Create RAG index
rag = BookRAG()
rag.ingest_chunks(result['chunks'], book_id="hp1")

# 3. Extract characters
extractor = CharacterExtractor()
book_text = ' '.join(result['chunks'][:50])  # First 50 chunks
names = extractor.extract_character_names(book_text)
print(f"Found characters: {names}")

# 4. Create profiles
for name in names[:5]:  # Top 5
    profile = extractor.create_canonical_profile(name, rag)
    print(f"\n{profile['name']}:")
    print(f"  Seed: {profile['seed']}")
    print(f"  Description: {profile['description'][:100]}...")
```

### Generate Character Image
```python
from services.image_service import ImageGenerator

# After you have a profile...
generator = ImageGenerator()

result = generator.generate_character_image(
    character_profile=profile,
    style="photorealistic portrait, detailed",
    aspect_ratio="1:1"
)

print(f"Image saved to: {result['image_url']}")
print(f"Generated in: {result['generation_time_ms']}ms")
```

---

## ✅ Verification Checklist

Before you say "I'm done":

- [ ] `python3 backend/verify_ml_setup.py` shows all green ✅
- [ ] Can process a PDF book successfully
- [ ] Can extract character names with Gemini
- [ ] Seeds are deterministic (same name → same seed)
- [ ] Can generate character images with Imagen 3
- [ ] Character API routes work (GET, POST, DELETE)
- [ ] Demo prep script generates sample data
- [ ] Full pipeline tested end-to-end

---

## 🎉 You're 80% Done!

**What's working:**
- ✅ RAG System (Custom FAISS) - PERFECT
- ✅ Character Extraction (Gemini) - WORKING
- ✅ Seed Generation - YOUR SECRET WEAPON
- ✅ Document Processing - WORKING

**What's left:**
- ⚠️ Install Vertex AI (5 mins)
- ⚠️ Test image generation (10 mins)
- ⚠️ Complete character routes (1 hour)
- ⚠️ Build demo prep script (1-2 hours)

**Total remaining work:** 3-4 hours

---

## 📞 Need Help?

**Check these files:**
- [ML_AI_SETUP_STATUS.md](ML_AI_SETUP_STATUS.md) - Detailed status report
- [README.md](README.md) - Quick start

**Run diagnostics:**
```bash
python3 backend/verify_ml_setup.py
python3 backend/test_setup.py
```

---

## 🚀 Next Command

```bash
pip install google-cloud-aiplatform vertexai
python3 backend/verify_ml_setup.py
```

**You've got this! Most of the hard work is already done.** 🎯
