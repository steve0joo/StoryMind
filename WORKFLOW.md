# StoryMind Workflow Guide

## Complete User Journey & Technical Flow

This document explains how StoryMind works from start to finish, both from the user's perspective and the technical implementation.

---

## 📚 User Workflow (What the User Sees)

### Step 1: Upload a Book

**User Action:** User uploads a book file (PDF, TXT, or EPUB)

**What They See:**

- Upload button in the frontend
- Progress indicator while processing
- Success message with character count

**Time:** 1-3 minutes (depending on book size)

---

### Step 2: Browse Extracted Characters

**User Action:** User views the list of characters extracted from their book

**What They See:**

- List of character names
- Character descriptions
- Mention count for each character
- Placeholder/generated images

**Example:**

```
Harry Potter
- Description: "A young boy, approximately ten years old. He has a scar on his forehead..."
- Mentions: 10
- Seed: 1085936863
```

---

### Step 3: Generate Character Images

**User Action:** User clicks "Generate Image" for a specific character

**What They See:**

- Style options (photorealistic, anime, sketch, etc.)
- Aspect ratio options (1:1, 16:9, etc.)
- Loading animation
- Final AI-generated image

**Time:** 8-10 seconds per image

---

### Step 4: Browse & Download Images

**User Action:** User views generated images and can download them

**What They See:**

- Gallery of character portraits
- Consistent images (same character always looks the same due to deterministic seeds)
- Download button

---

## 🔧 Technical Workflow (What Happens Behind the Scenes)

### Architecture Overview

```
┌─────────────┐
│   Frontend  │ (React + Vite)
│  (Port 5173)│
└──────┬──────┘
       │ HTTP REST API
       ▼
┌─────────────┐
│   Backend   │ (Flask)
│  (Port 5000)│
└──────┬──────┘
       │
       ├─────────────┬─────────────┬─────────────┬─────────────┐
       ▼             ▼             ▼             ▼             ▼
   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
   │Document│   │  RAG   │   │Character│  │ Image  │   │Database│
   │Processor│  │ System │   │Extractor│  │Generator│  │SQLite │
   └────────┘   └────────┘   └────────┘   └────────┘   └────────┘
        │            │            │            │            │
        ▼            ▼            ▼            ▼            ▼
   LangChain     FAISS      Gemini 2.0    Imagen 3    SQLAlchemy
   (PDF/TXT)   (Vectors)   Flash (LLM)   (GenAI)     (ORM)
```

---

## 📖 Step-by-Step Technical Flow

### **STEP 1: Book Upload & Processing**

#### 1.1 File Upload

**API Endpoint:** `POST /api/books/upload`

**Flow:**

```
User uploads file
    ↓
Frontend sends multipart/form-data to backend
    ↓
Backend validates file extension (.pdf, .txt, .epub)
    ↓
File saved to: backend/static/uploads/books/{uuid}.pdf
```

**Code Location:** [backend/routes/books_routes.py:42](backend/routes/books_routes.py#L42)

---

#### 1.2 Document Processing

**Service:** `document_processor.py`

**Flow:**

```
Load book file
    ↓
LangChain loaders:
- PDF: PyPDFLoader
- TXT: TextLoader
- EPUB: UnstructuredEPUBLoader
    ↓
Extract raw text from all pages
    ↓
RecursiveCharacterTextSplitter:
- chunk_size: 1000 characters
- chunk_overlap: 200 characters
    ↓
Result: List of 500-700 text chunks
```

**Example Output:**

```python
{
  'chunks': [
    "Harry Potter lived with Mr and Mrs Dursley...",
    "The Dursleys had everything they wanted...",
    # ... 632 more chunks
  ],
  'total_chunks': 634,
  'total_chars': 525391,
  'metadata': {
    'filename': 'harry-potter.pdf',
    'file_type': '.pdf',
    'num_pages': 200
  }
}
```

**Code Location:** [backend/services/document_processor.py:39](backend/services/document_processor.py#L39)

---

#### 1.3 RAG System (Semantic Search Index)

**Service:** `rag_system.py`

**Flow:**

```
Receive 634 text chunks
    ↓
Load SentenceTransformer model:
- Model: all-MiniLM-L6-v2
- Embedding dimension: 384
    ↓
Generate embeddings for each chunk (in batches of 32)
    ↓
Create FAISS IndexFlatL2:
- Index type: L2 (Euclidean distance)
- Vectors: 634 × 384 dimensions
    ↓
Save index to: backend/data/faiss_indices/{book_id}.faiss
```

**What is FAISS?**

- Facebook AI Similarity Search
- Ultra-fast vector similarity search
- Allows finding "similar" text chunks in milliseconds
- Used for: "Find all mentions of Harry Potter in the book"

**Example Query:**

```python
rag.search("Harry Potter", k=10)
# Returns 10 most relevant text chunks mentioning Harry
```

**Code Location:** [backend/services/rag_system.py:51](backend/services/rag_system.py#L51)

---

#### 1.4 Character Extraction

**Service:** `character_service.py`

**Flow:**

```
Take first ~40,000 characters of book
    ↓
Send to Gemini 2.0 Flash with prompt:
"Extract main character names from this text"
    ↓
Gemini analyzes text and returns JSON:
["Harry Potter", "Mr Dursley", "Mrs Dursley", "Dudley", "Mrs Potter"]
    ↓
For EACH character name:
  1. Query RAG system: Get 10 mentions of this character
  2. Send mentions to Gemini: "Create canonical description"
  3. Gemini synthesizes description from all mentions
  4. Generate deterministic seed: md5(character_name)
    ↓
Save to database
```

**Example Character Profile:**

```python
{
  'name': 'Harry Potter',
  'description': 'A young boy, approximately ten years old. He has a scar on his forehead, which he possessed since infancy...',
  'seed': 1085936863,  # Deterministic - always same for "Harry Potter"
  'mention_count': 10
}
```

**Why Deterministic Seeds?**

- Same character name → Same seed → Same image every time
- Consistency across regenerations
- Uses: `hashlib.md5(character_name.encode()).digest()[:4]`

**Code Location:** [backend/services/character_service.py:78](backend/services/character_service.py#L78)

---

### **STEP 2: Image Generation**

#### 2.1 User Requests Image

**API Endpoint:** `POST /api/characters/{character_id}/generate-image`

**Flow:**

```
User clicks "Generate Image" button
    ↓
Frontend sends request with options:
{
  "style": "photorealistic portrait",
  "aspect_ratio": "1:1"
}
    ↓
Backend retrieves character from database
```

**Code Location:** [backend/routes/characters_routes.py:165](backend/routes/characters_routes.py#L165)

---

#### 2.2 Image Generation with Imagen 3

**Service:** `image_service.py`

**Flow:**

```
Retrieve character profile:
- Name: "Harry Potter"
- Description: "A young boy, approximately ten years old..."
- Seed: 1085936863
    ↓
Construct prompt:
"{description}, {style} [ID: {seed}]"
    ↓
Call Vertex AI Imagen 3:
- Model: imagen-3.0-generate-001
- Project: storymind-477623
- Location: us-central1
- Parameters:
  * number_of_images: 1
  * aspect_ratio: "1:1"
  * person_generation: "allow_adult"
  * safety_filter_level: "block_some"
    ↓
Imagen generates image (8-10 seconds)
    ↓
Save image to: backend/static/uploads/images/{name}_{seed}.png
    ↓
Save record to database:
{
  'character_id': '...',
  'image_url': '/static/uploads/images/harry_potter_1085936863.png',
  'prompt': '...',
  'generation_time_ms': 9043
}
```

**Fallback for Failures:**

```
If Imagen fails (quota, content filter, etc.):
    ↓
Create placeholder file:
/static/uploads/images/placeholder_{name}_{seed}.txt
    ↓
Still save record with error info
```

**Code Location:** [backend/services/image_service.py:63](backend/services/image_service.py#L63)

---

### **STEP 3: Serving Images**

#### 3.1 Frontend Displays Images

**API Endpoint:** `GET /api/characters/{character_id}/images`

**Flow:**

```
Frontend requests character images
    ↓
Backend queries database for GeneratedImage records
    ↓
Returns list of image URLs:
[
  {
    'id': '...',
    'image_url': '/static/uploads/images/harry_potter_1085936863.png',
    'prompt': '...',
    'created_at': '2025-11-08T21:06:00'
  }
]
    ↓
Frontend renders images:
<img src="http://localhost:5000/static/uploads/images/harry_potter_1085936863.png" />
```

**Code Location:** [backend/routes/characters_routes.py:232](backend/routes/characters_routes.py#L232)

---

## 🗄️ Database Schema

### Books Table

```sql
CREATE TABLE books (
  id VARCHAR PRIMARY KEY,
  title VARCHAR,
  author VARCHAR,
  upload_date DATETIME,
  processing_status VARCHAR,  -- 'processing', 'completed', 'failed'
  faiss_index_path VARCHAR,
  character_count INTEGER
);
```

### Characters Table

```sql
CREATE TABLE characters (
  id VARCHAR PRIMARY KEY,
  book_id VARCHAR FOREIGN KEY,
  name VARCHAR,
  canonical_description TEXT,
  seed INTEGER,  -- Deterministic seed for image generation
  mention_count INTEGER
);
```

### Images Table

```sql
CREATE TABLE images (
  id VARCHAR PRIMARY KEY,
  character_id VARCHAR FOREIGN KEY,
  image_url VARCHAR,
  prompt TEXT,
  generation_time_ms INTEGER,
  created_at DATETIME
);
```

---

## 🔑 Key Technologies & Why They're Used

### Frontend

- **React + Vite**: Fast, modern UI development
- **CORS**: Allows frontend (port 5173) to talk to backend (port 5000)

### Backend

- **Flask**: Lightweight Python web framework
- **SQLAlchemy**: ORM for database operations
- **Flask-CORS**: Enable cross-origin requests

### Document Processing

- **LangChain**: Pre-built loaders for PDF/TXT/EPUB
- **RecursiveCharacterTextSplitter**: Smart text chunking
- **Why chunking?** Books are too long for AI models (context limits)

### RAG System (Semantic Search)

- **FAISS**: Ultra-fast vector similarity search
- **SentenceTransformers**: Convert text → 384D vectors
- **Why not just search?** RAG understands meaning, not just keywords
  - Search: "Find 'Harry Potter'" → Exact match
  - RAG: "Find mentions of the protagonist" → Semantic match

### AI/ML

- **Gemini 2.0 Flash**: Character extraction & description synthesis

  - Fast (< 1 second per request)
  - Good at JSON structured output
  - Free tier: 50 requests/day

- **Imagen 3**: Image generation
  - Photorealistic quality
  - Content safety filters
  - Free tier: Limited quota

### Database

- **SQLite**: File-based database (perfect for hackathons)
- **No server needed**: Just a .db file

---

## 🎯 Critical Design Decisions

### 1. **Why Custom FAISS instead of LangChain RAG?**

- **Full control** over indexing and search
- **No hidden abstractions** - you know exactly what's happening
- **Easier debugging** during hackathon
- **Better performance** for this specific use case

### 2. **Why Deterministic Seeds?**

- **Consistency**: Same character → Same image (even if regenerated)
- **Reproducibility**: Can show the same demo content reliably
- **Implementation**: `md5(character_name)` → Always returns same number

### 3. **Why Two-Step Character Extraction?**

- **Step 1**: Extract names (fast, simple)
- **Step 2**: Build profiles using RAG (accurate, detailed)
- **Benefit**: More accurate descriptions using actual book context

### 4. **Why Cache Everything?**

- **API quotas**: Limited free tier
- **Demo reliability**: Pre-generate content
- **Performance**: Instant responses for cached data

---

## 🚀 Performance Metrics

### Book Processing Time

| Book Size          | Processing | RAG Index | Characters | Total |
| ------------------ | ---------- | --------- | ---------- | ----- |
| Small (100 pages)  | 10s        | 5s        | 15s        | ~30s  |
| Medium (200 pages) | 20s        | 10s       | 30s        | ~60s  |
| Large (500 pages)  | 50s        | 25s       | 60s        | ~135s |

### Image Generation

- **Successful**: 8-10 seconds per image
- **Quota exceeded**: < 1 second (fast fail)
- **Content filtered**: ~3 seconds (API processes then rejects)

### RAG Queries

- **Index creation**: ~1-2 seconds for 600 chunks
- **Single search**: < 100ms (FAISS is FAST!)
- **10 searches**: < 500ms

---

## 🎨 User Experience Flow (Ideal Demo)

### Demo Scenario

```
1. User: "I want to visualize characters from Harry Potter"

2. Upload book (2 minutes of processing)
   → Show loading animation
   → Display progress: "Processing 634 chunks..."

3. Characters appear automatically:
   ✓ Harry Potter
   ✓ Mr Dursley
   ✓ Mrs Dursley
   ✓ Dudley
   ✓ Mrs Potter

4. User clicks "Generate Image" for Harry Potter
   → 9 seconds later
   → Photorealistic portrait appears!

5. User tries again with different style:
   → "Anime style"
   → New image in 8 seconds

6. Consistency test:
   → Regenerate with same style
   → SAME image appears (deterministic seed!)
```

---

## 🐛 Error Handling & Edge Cases

### What Happens When...

#### **1. Gemini Quota Exceeded**

```
Error: 429 Quota exceeded
Response:
{
  "error": "Character extraction failed",
  "message": "API quota exceeded. Try again tomorrow."
}
Action: Use cached characters from previous runs
```

#### **2. Imagen Content Filter**

```
Error: "No images returned from Imagen 3"
Reason: Character name is copyrighted (e.g., "Harry Potter")
Action: Create placeholder file, continue processing
```

#### **3. Invalid File Format**

```
Error: Unsupported file type
Response: "Only PDF, EPUB, and TXT files are allowed"
Action: Show error message, request valid file
```

#### **4. Book Too Large**

```
Warning: Book > 1000 pages
Action:
- Still process (might take 3-5 minutes)
- Extract from first 50,000 characters only
- Create FAISS index for full book
```

---

## 📊 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     USER UPLOADS BOOK                         │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Document Processor          │
        │   (LangChain)                 │
        │                               │
        │   PDF/TXT/EPUB → Text Chunks  │
        └───────────┬───────────────────┘
                    │
        ┌───────────┴────────────┐
        │                        │
        ▼                        ▼
┌──────────────┐        ┌──────────────┐
│  RAG System  │        │  Character   │
│   (FAISS)    │        │  Extractor   │
│              │        │  (Gemini)    │
│  Create      │◄───────┤              │
│  Index       │  Query │  Extract     │
│              │  for   │  Names       │
└──────┬───────┘  mentions              │
       │                └──────┬────────┘
       │                       │
       │                       ▼
       │              ┌──────────────┐
       │              │  For each    │
       │              │  character:  │
       │              │              │
       │              │  1. Get RAG  │◄───┐
       │              │     mentions │    │
       │              │  2. Gemini   │    │
       │              │     synthesis│    │
       │              │  3. Generate │    │
       │              │     seed     │    │
       │              └──────┬───────┘    │
       │                     │            │
       ▼                     ▼            │
┌────────────────────────────────────┐   │
│         SQLite Database             │   │
│                                     │   │
│  Books Table    Characters Table    │   │
│  ├─ id          ├─ id              │   │
│  ├─ title       ├─ name            │   │
│  └─ ...         ├─ description     │   │
│                 ├─ seed            │   │
│                 └─ ...             │   │
└────────────────┬───────────────────┘   │
                 │                       │
    ┌────────────┴──────────┐            │
    │ User clicks "Generate"│            │
    └────────────┬───────────┘            │
                 │                       │
                 ▼                       │
        ┌──────────────────┐             │
        │  Image Generator │             │
        │  (Imagen 3)      │             │
        │                  │             │
        │  Description +   │             │
        │  Seed →          │             │
        │  Imagen API →    │             │
        │  PNG Image       │             │
        └────────┬─────────┘             │
                 │                       │
                 ▼                       │
        ┌──────────────────┐             │
        │  Save Image      │             │
        │  /static/uploads/│             │
        │  images/         │             │
        └────────┬─────────┘             │
                 │                       │
                 ▼                       │
        ┌──────────────────┐             │
        │  Images Table    │             │
        │  ├─ id           │             │
        │  ├─ character_id │─────────────┘
        │  ├─ image_url    │
        │  └─ prompt       │
        └──────────────────┘
```

---

## 🎓 Learning Resources

### What is RAG?

**Retrieval-Augmented Generation** = Search + AI

Traditional AI:

```
User: "Tell me about Harry"
AI: "I don't know, I wasn't trained on Harry Potter"
```

With RAG:

```
User: "Tell me about Harry"
System:
  1. Search book for "Harry" mentions (FAISS)
  2. Send those chunks to AI
  3. AI synthesizes answer from actual book content
AI: "Harry is a young boy with a lightning scar..."
```

### Why Embeddings?

**Embeddings** = Numbers that represent meaning

```
"Harry Potter" → [0.23, -0.45, 0.67, ..., 0.12]  (384 numbers)
"The protagonist" → [0.25, -0.43, 0.69, ..., 0.10]  (similar numbers!)

Distance between vectors = Similarity of meaning
```

This is how FAISS finds "similar" text!

---

## 🔍 File Structure Reference

```
StoryMind/
├── backend/
│   ├── services/
│   │   ├── document_processor.py    ← Book → Chunks
│   │   ├── rag_system.py            ← FAISS vector search
│   │   ├── character_service.py     ← Gemini extraction
│   │   └── image_service.py         ← Imagen generation
│   ├── routes/
│   │   ├── books_routes.py          ← /api/books endpoints
│   │   └── characters_routes.py     ← /api/characters endpoints
│   ├── models.py                    ← Database schema
│   ├── app.py                       ← Flask server
│   ├── data/
│   │   ├── storymind.db            ← SQLite database
│   │   └── faiss_indices/          ← FAISS index files
│   └── static/
│       └── uploads/
│           ├── books/              ← Uploaded PDFs/TXTs
│           └── images/             ← Generated images
└── frontend/
    └── src/
        ├── components/
        └── pages/
```

---

## ✅ Quick Reference

### Start Backend

```bash
cd backend
python3 app.py
# Runs on http://localhost:5000
```

### Start Frontend

```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

### Test ML/AI Pipeline

```bash
cd backend
python3 test_formats_simple.py  # Test PDF/TXT/EPUB
python3 test_setup.py           # Verify all services
```

### Check Database

```bash
cd backend
sqlite3 data/storymind.db
.tables
SELECT * FROM characters;
```

---

## 🎯 Summary

**StoryMind Workflow in 3 Sentences:**

1. **Upload** → User uploads book → LangChain splits into chunks → FAISS creates searchable index
2. **Extract** → Gemini reads book → Identifies characters → RAG finds all mentions → Gemini writes descriptions
3. **Generate** → User clicks generate → Imagen creates image from description → Consistent results via deterministic seeds

**The Magic:**

- RAG makes AI understand YOUR book specifically
- Deterministic seeds make images reproducible
- FAISS makes search instant
- Caching makes demos reliable
