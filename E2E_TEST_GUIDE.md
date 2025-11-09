# End-to-End Testing Guide

**StoryMind - Complete Flow Verification**

Last Updated: November 9, 2025

---

## Prerequisites Checklist

Before starting, verify:

- [ ] Python 3.11 virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`backend/data/storymind.db` exists)
- [ ] `.env` file configured with `GOOGLE_API_KEY` and `FLASK_PORT=5001`
- [ ] Frontend dependencies installed (`npm install` in frontend/)

---

## Step 1: Start Backend Server

### Terminal 1 - Backend

```bash
cd /Users/steve.joo/Documents/StoryMind/backend
source venv/bin/activate
python app.py
```

### ✅ Expected Output (NO WARNINGS):

```
2025-11-09 XX:XX:XX,XXX - __main__ - INFO - Books routes registered successfully
2025-11-09 XX:XX:XX,XXX - __main__ - INFO - Characters routes registered successfully
2025-11-09 XX:XX:XX,XXX - __main__ - INFO - Starting StoryMind Backend on port 5001
2025-11-09 XX:XX:XX,XXX - __main__ - INFO - Debug mode: True
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5001
```

### ❌ Troubleshooting:

| Error                    | Solution                                                            |
| ------------------------ | ------------------------------------------------------------------- |
| Port 5001 already in use | `lsof -i :5001 \| grep Python \| awk '{print $2}' \| xargs kill -9` |
| urllib3 OpenSSL warning  | Python 3.9 still active - use `python3.11 -m venv venv`             |
| Module not found         | `pip install -r requirements.txt`                                   |

---

## Step 2: Start Frontend Server

### Terminal 2 - Frontend

```bash
cd /Users/steve.joo/Documents/StoryMind/frontend
npm run dev
```

### ✅ Expected Output:

```
VITE v5.4.10  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

### ❌ Troubleshooting:

| Error                   | Solution                                        |
| ----------------------- | ----------------------------------------------- |
| ECONNREFUSED /api/books | Backend not running - start backend first       |
| npm ERR!                | Run `npm install` first                         |
| Port 5173 in use        | Kill process: `lsof -i :5173` then `kill <PID>` |

---

## Step 3: Test Health Endpoints

### Open Browser or use curl:

```bash
# Backend health
curl http://localhost:5001/api/health

# Expected: {"status": "healthy"}

# List existing books
curl http://localhost:5001/api/books

# Expected: {"books": [...], "total": 5}
```

### ✅ Success Criteria:

- Backend responds with JSON
- Books endpoint returns your 5 existing books
- No CORS errors in browser console

---

## Step 4: Test Frontend Pages

### 4.1 Home Page

**URL:** http://localhost:5173

**Test:**

- [ ] Page loads without errors
- [ ] Search bar visible
- [ ] Upload button visible
- [ ] No console errors (open DevTools: F12)

### 4.2 Search Functionality

**Test:**

1. Type "harry" in search box
2. Press Enter or click Search

**✅ Expected:**

- Results page shows books matching "harry"
- Book cards display with title and author
- Click on a book card navigates to book detail

**❌ If search returns empty:**

- Check browser console for errors
- Verify backend `/api/books` returns data
- Check API client is using `/api` not `http://localhost:5000/api`

### 4.3 Book Detail Page

**URL:** http://localhost:5173/book/:id (click on a book from search)

**Test:**

- [ ] Book title and author displayed
- [ ] Character cards shown
- [ ] Each character has name and description
- [ ] Character images displayed (may be placeholders)

**✅ Success Criteria:**

- All 20 characters load
- No 404 errors
- Character descriptions visible

---

## Step 5: Test Book Upload (Optional - Uses Gemini Quota)

**⚠️ WARNING:** Uploading a new book uses Gemini API quota (50/day limit)

**Test:**

1. Go to Home Page
2. Click "Upload Book" or drag & drop a PDF/EPUB
3. Wait for processing (may take 30-60 seconds)

**✅ Expected Flow:**

```
1. File upload → 201 Created
2. Processing starts → Status: "processing"
3. RAG indexing → FAISS index created
4. Character extraction → Gemini API calls
5. Profile generation → Canonical descriptions
6. Database update → Status: "completed"
```

**Monitor in Terminal 1 (Backend Logs):**

```
File saved: backend/static/uploads/books/...
Processing book: filename.pdf
Processed X chunks from filename.pdf
Creating FAISS index for semantic search
FAISS index saved to: ...
Extracting characters using Gemini
Extracted N characters: [...]
Character profile created: Name (seed: XXXXX)
Book processing completed successfully
```

**❌ Common Errors:**

| Error                 | Cause                    | Solution                             |
| --------------------- | ------------------------ | ------------------------------------ |
| 429 Quota Exceeded    | Hit Gemini 50/day limit  | Use existing 5 books for demo        |
| 500 Processing Failed | Document parsing error   | Try different PDF/EPUB               |
| CORS error            | API client misconfigured | Check `baseURL: '/api'` in client.js |

---

## Step 6: Verify Database Updates

```bash
cd backend
source venv/bin/activate
python -c "
import sqlite3
conn = sqlite3.connect('data/storymind.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM books')
print(f'Books: {c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM characters')
print(f'Characters: {c.fetchone()[0]}')
c.execute('SELECT name, title FROM characters JOIN books ON characters.book_id = books.id LIMIT 5')
print('Sample characters:', c.fetchall())
conn.close()
"
```

**✅ Expected:**

```
Books: 5 (or 6 if you uploaded a new book)
Characters: 20 (or more)
Sample characters: [('Harry Potter', 'Harry Potter...'), ...]
```

---

## Step 7: Performance Check

### Backend Response Times:

```bash
# Test API performance
time curl http://localhost:5001/api/books
time curl http://localhost:5001/api/characters?book_id=<some-id>
```

**✅ Target Times:**

- `/api/books`: < 100ms
- `/api/characters`: < 200ms

### Frontend Load Times:

Open DevTools → Network tab:

- Home page: < 500ms
- Book detail: < 1s
- Search results: < 300ms

---

## Step 8: Character Image Generation (Optional)

**⚠️ WARNING:** Uses Imagen 3 quota (very limited on free tier)

**Test via API:**

```bash
curl -X POST http://localhost:5001/api/characters/<character_id>/generate-image \
  -H "Content-Type: application/json" \
  -d '{"style": "photorealistic portrait", "aspect_ratio": "1:1"}'
```

**Expected:**

- Success: Image URL returned
- Quota exceeded: Placeholder image returned (this is OK!)

---

## Complete Test Checklist

### Backend:

- [ ] Server starts with no warnings
- [ ] Health endpoint responds
- [ ] Books API returns 5 books
- [ ] Characters API returns 20 characters
- [ ] No Python errors in logs

### Frontend:

- [ ] Home page loads
- [ ] Search works (partial match)
- [ ] Book detail shows characters
- [ ] No console errors
- [ ] No CORS errors

### Integration:

- [ ] Frontend connects to backend
- [ ] API proxy working (requests go to port 5001)
- [ ] Database queries successful
- [ ] Images display (placeholder or real)

### Performance:

- [ ] Page loads < 1 second
- [ ] API responses < 500ms
- [ ] No memory leaks (DevTools → Memory)

---

## Success Criteria ✅

**Minimum (Demo Ready):**

- ✅ Both servers running without errors
- ✅ Home page and search working
- ✅ Can view existing 5 books
- ✅ Characters display with descriptions
- ✅ No CORS errors

**Ideal (Full Demo):**

- ✅ All of above +
- ✅ Character relationship graph visible
- ✅ Book upload tested (at least once)
- ✅ Image generation tested (if quota available)
- ✅ Performance < 1s page loads

---

## Next Steps After Testing

Once E2E testing passes:

1. **Implement Character Relationship Graph** (see RELATIONSHIP_GRAPH_GUIDE.md)
2. **Pre-generate Demo Data** (run `python scripts/demo_prep.py`)
3. **Prepare Demo Script** (practice walkthrough)
4. **Test on Different Browser** (Chrome, Firefox, Safari)

---

## Support

If tests fail, check:

1. Review MD files
2. Backend logs in Terminal 1
3. Browser DevTools console (F12)
4. `python test_setup.py` for environment validation

---

**Last Updated:** November 9, 2025
**Status:** Ready for E2E Testing
