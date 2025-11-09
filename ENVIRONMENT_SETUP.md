# StoryMind - Environment Setup Guide

**Complete setup guide for ML/AI development**

---

## Prerequisites

### Required Software

1. **Python 3.9+**

   ```bash
   python3 --version
   # Should output: Python 3.9.6 or higher
   ```

2. **pip** (Python package manager)

   ```bash
   pip3 --version
   # Should be installed with Python
   ```

3. **Git** (for version control)
   ```bash
   git --version
   ```

### Required Accounts

1. **Google AI API Key** (for Gemini)

   - Get from: https://ai.google.dev/
   - Free tier: 15 requests/minute

2. **Google Cloud Project** (for Imagen 3)
   - Create project at: https://console.cloud.google.com/
   - Enable Vertex AI API
   - Create service account with "Vertex AI User" role
   - Download service account key (JSON file)

---

## Step-by-Step Setup

### 1. Clone Repository

```bash
git clone <repository-url> StoryMind
cd StoryMind
```

### 2. Backend Setup

#### Option A: Using System Python (Recommended for Quick Start)

```bash
cd backend

# Install all dependencies
pip3 install -r requirements.txt

# Expected time: 3-5 minutes
# Disk space: ~500 MB
```

#### Option B: Using Virtual Environment (Recommended for Isolation)

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Expected time: 3-5 minutes
```

**Note:** If you encounter errors with venv installation, use Option A (system Python).

### 3. Environment Variables

Create `.env` file in `backend/` directory:

```bash
cd backend
cp .env.example .env  # If example exists
# OR create new file:
nano .env
```

Add the following content to `backend/.env`:

```bash
# ============================================================================
# Google AI/ML API Keys
# ============================================================================
GOOGLE_API_KEY=your_google_ai_api_key_here

# ============================================================================
# Google Cloud Project Settings (for Imagen 3)
# ============================================================================
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account-key.json

# ============================================================================
# Flask Settings
# ============================================================================
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_SECRET_KEY=your-random-secret-key-here
FLASK_PORT=5000

# ============================================================================
# Database
# ============================================================================
DATABASE_URL=sqlite:///data/storymind.db

# ============================================================================
# CORS Settings
# ============================================================================
ALLOWED_ORIGINS=http://localhost:5173
```

**Required Variables:**

- `GOOGLE_API_KEY` - **REQUIRED** for Gemini character extraction
- `GOOGLE_CLOUD_PROJECT` - Optional (for Imagen 3)
- `GOOGLE_APPLICATION_CREDENTIALS` - Optional (for Imagen 3)

**Optional Variables:**

- `FLASK_SECRET_KEY` - Auto-generated if not set
- `DATABASE_URL` - Defaults to SQLite in data/ folder
- `ALLOWED_ORIGINS` - Defaults to localhost:5173

### 4. Service Account Key (For Imagen 3)

If using Imagen 3 for image generation:

1. **Download service account key from Google Cloud Console:**

   - Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
   - Select your service account
   - Keys → Add Key → Create New Key → JSON
   - Download the JSON file

2. **Place in backend directory:**

   ```bash
   mv ~/Downloads/your-project-xxxxx.json backend/service-account-key.json
   ```

3. **Update .env:**

   ```bash
   GOOGLE_APPLICATION_CREDENTIALS=/Users/yourusername/Documents/StoryMind/backend/service-account-key.json
   ```

   **Important:** Use absolute path, not relative path!

### 5. Initialize Database

```bash
cd backend
python3 init_db.py
```

**Expected Output:**

```
Creating database tables...
✓ Books table created
✓ Characters table created
✓ Images table created
✅ Database initialized successfully
```

**Database Location:** `backend/data/storymind.db`

### 6. Verify Setup

Run the comprehensive verification script:

```bash
cd backend
python3 verify_ml_setup.py
```

**Expected Output:**

```
✅ FAISS (Vector Database)
✅ Sentence Transformers
✅ LangChain + Community
✅ Gemini API Connected
✅ Vertex AI Installed
✅ RAG System
✅ Character Extractor
✅ Seed Generator
✅ End-to-End Pipeline
```

---

## Verification Checklist

Run these commands to verify everything is set up:

```bash
# 1. Check Python version
python3 --version
# ✓ Should be 3.9.6 or higher

# 2. Check packages installed
pip3 list | grep -E "(faiss|sentence-transformers|langchain)"
# ✓ Should show installed packages

# 3. Check environment variables
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('GOOGLE_API_KEY:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')"
# ✓ Should show: GOOGLE_API_KEY: SET

# 4. Check database
ls -la data/storymind.db
# ✓ Should exist

# 5. Test imports
python3 -c "from services.rag_system import BookRAG; print('✅ Imports work')"
# ✓ Should print: ✅ Imports work

# 6. Run verification
python3 verify_ml_setup.py
# ✓ Should show all green checkmarks
```

---

## Package Details

### Total Packages Installed

**Direct Dependencies:** 14 packages
**Total (with sub-dependencies):** ~50+ packages

### Key Packages and Their Purpose

| Package                     | Version | Purpose                             |
| --------------------------- | ------- | ----------------------------------- |
| **faiss-cpu**               | 1.9.0   | Vector similarity search for RAG    |
| **sentence-transformers**   | 3.3.1   | Text embeddings (384-dim vectors)   |
| **langchain**               | 0.3.7   | Document loading and text splitting |
| **google-generativeai**     | 0.8.3   | Gemini API for character extraction |
| **google-cloud-aiplatform** | 1.71.1  | Vertex AI for Imagen 3              |
| **flask**                   | 3.0.3   | Web framework for REST API          |
| **sqlalchemy**              | 2.0.35  | Database ORM                        |
| **pypdf**                   | 5.1.0   | PDF document processing             |

### Disk Space Requirements

- **Packages:** ~500 MB
- **Models (sentence-transformers):** ~100 MB (downloaded on first use)
- **Database:** ~50 KB (grows with data)
- **FAISS Indices:** ~1-5 MB per book
- **Total:** ~600-700 MB

---

## Troubleshooting

### Issue: "No module named 'langchain'"

**Solution:**

```bash
pip3 install -r requirements.txt
```

### Issue: "GOOGLE_API_KEY not set"

**Solution:**

```bash
# Check .env file exists
ls backend/.env

# Verify contents
cat backend/.env | grep GOOGLE_API_KEY

# Make sure it's set
export GOOGLE_API_KEY="your_key_here"
```

### Issue: "No such table: books"

**Solution:**

```bash
cd backend
python3 init_db.py
```

### Issue: Virtual environment installation fails

**Solution:** Use system Python instead:

```bash
# Exit venv
deactivate

# Install to system Python
pip3 install -r requirements.txt

# Run scripts with python3 (not python)
python3 scripts/demo_prep.py
```

### Issue: "Imagen 3 quota exceeded"

**Solution:** This is expected with free tier. The placeholder system handles it:

- Placeholders are created in `static/uploads/images/`
- Your code works perfectly
- To get real images: upgrade billing or request quota increase

### Issue: "Permission denied" when creating directories

**Solution:**

```bash
# Create directories manually
mkdir -p backend/static/uploads/books
mkdir -p backend/static/uploads/images
mkdir -p backend/data/faiss_indices
```

---

## Environment Files Summary

### Files That Must Be Created

1. **`backend/.env`** - Environment variables
2. **`backend/service-account-key.json`** - Google Cloud credentials (optional)

### Files That Are Auto-Created

1. **`backend/data/storymind.db`** - SQLite database
2. **`backend/data/faiss_indices/*.faiss`** - Vector indices
3. **`backend/static/uploads/books/`** - Book uploads
4. **`backend/static/uploads/images/`** - Generated images

---

## Directory Structure

```
StoryMind/
├── backend/
│   ├── .env                    # ← CREATE THIS (environment variables)
│   ├── service-account-key.json # ← ADD THIS (Google Cloud key)
│   ├── requirements.txt        # ✓ Exists (package list)
│   ├── init_db.py             # ✓ Exists (database setup)
│   ├── verify_ml_setup.py     # ✓ Exists (verification)
│   ├── app.py                 # ✓ Exists (Flask server)
│   ├── models.py              # ✓ Exists (database models)
│   ├── services/              # ✓ Exists (ML/AI services)
│   │   ├── rag_system.py
│   │   ├── character_service.py
│   │   ├── image_service.py
│   │   └── document_processor.py
│   ├── routes/                # ✓ Exists (API endpoints)
│   ├── scripts/               # ✓ Exists (automation)
│   │   └── demo_prep.py
│   ├── utils/                 # ✓ Exists (utilities)
│   │   └── seed_generator.py
│   ├── data/                  # Auto-created
│   │   └── storymind.db       # Auto-created
│   └── static/                # Auto-created
│       └── uploads/           # Auto-created
│           ├── books/         # Add PDFs here
│           └── images/        # Auto-populated
└── frontend/                  # Frontend code (separate setup)
```

---

## Quick Start Commands

### First Time Setup

```bash
# 1. Install packages
cd backend
pip3 install -r requirements.txt

# 2. Create .env file
nano .env
# Add your GOOGLE_API_KEY

# 3. Initialize database
python3 init_db.py

# 4. Verify setup
python3 verify_ml_setup.py
```

### Daily Development

```bash
# Start backend server
cd backend
python3 app.py

# Process a book
python3 scripts/demo_prep.py

# Run tests
python3 verify_ml_setup.py
```

---

## Testing Your Setup

### 1. Quick Test

```bash
cd backend
python3 -c "
from services.rag_system import BookRAG
rag = BookRAG()
print('✅ Setup working!')
"
```

### 2. End-to-End Test

```bash
# Add a test book to books directory
# Then run demo prep
python3 scripts/demo_prep.py
```

### 3. API Test

```bash
# Start server
python3 app.py

# In another terminal, test endpoint
curl http://localhost:5000/api/health
# Should return: {"status": "healthy"}
```

---

## Environment Variables Reference

### Required for Basic Functionality

```bash
GOOGLE_API_KEY=<your-key>        # Gemini API for character extraction
```

### Optional (Image Generation)

```bash
GOOGLE_CLOUD_PROJECT=<project>   # Your GCP project ID
GOOGLE_APPLICATION_CREDENTIALS=<path>  # Service account key path
```

### Optional (Defaults Provided)

```bash
FLASK_DEBUG=True                 # Development mode
FLASK_PORT=5000                  # Server port
DATABASE_URL=sqlite:///data/storymind.db  # Database location
ALLOWED_ORIGINS=http://localhost:5173     # CORS settings
```

---

## Production Considerations

### For Hackathon Demo

**Minimum Required:**

- ✅ GOOGLE_API_KEY (Gemini)
- ✅ Database initialized
- ✅ Packages installed

**Optional but Recommended:**

- ⚠️ Imagen 3 setup (or use placeholders)
- ⚠️ Pre-generated demo data

### For Production Deployment

**Additional Requirements:**

- PostgreSQL instead of SQLite
- Redis for caching
- Google Cloud Storage for files
- Proper secrets management
- Load balancer
- Monitoring/logging

---

## Summary

✅ **Environment setup is complete when:**

1. All packages install without errors
2. `verify_ml_setup.py` shows all green checks
3. Database is initialized
4. `.env` file has GOOGLE_API_KEY
5. Demo prep script can process a test book

📊 **Setup Time:** 10-15 minutes
💾 **Disk Space:** ~600 MB
🔧 **Difficulty:** Easy (well documented)

---

**You're ready to develop! 🚀**
