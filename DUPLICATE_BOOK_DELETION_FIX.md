# Duplicate Book Deletion Fix

**Date:** November 9, 2025
**Status:** ✅ Fixed

## Problem

User uploaded the same book multiple times, resulting in duplicate "Anna_Karenina" entries showing in the UI even after manual deletion attempts.

### Root Causes:

1. **Missing DELETE endpoint** - Backend had no `DELETE /api/books/:id` endpoint
   - Frontend couldn't delete books programmatically
   - Manual deletion (e.g., via database) didn't clean up associated data

2. **Broken duplicate detection** - Upload route checked wrong field:
   ```python
   # ❌ WRONG - Checked against filename before metadata extraction
   existing_book = db.query(Book).filter(Book.title == filename).first()
   ```
   - Books are saved with `title` from PDF metadata (e.g., "Anna_Karenina")
   - But duplicate check used `filename` (e.g., "anna_karenina_v2.pdf")
   - Mismatch allowed duplicates to slip through

3. **Incomplete cleanup** - Duplicate detection didn't delete:
   - Physical image files
   - FAISS index files (.faiss and .pkl)
   - Character and image records

## Solutions Applied

### 1. Implemented DELETE Endpoint

**File:** [backend/routes/books_routes.py:391-500](backend/routes/books_routes.py#L391-L500)

```python
@books_bp.route('/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Delete a book and all associated data (characters, images, FAISS index)

    Deletes:
    - Book record from database
    - All characters associated with book
    - All images (database + physical files)
    - FAISS index files (.faiss and .pkl)

    Returns:
        JSON with deletion summary
    """
```

**What it deletes:**
- ✅ Book database record
- ✅ Character records
- ✅ Image records
- ✅ Physical image files from `/static/uploads/images/`
- ✅ FAISS index files (`.faiss` and `.pkl`)

**Usage:**
```bash
# Delete a book
curl -X DELETE http://localhost:5001/api/books/{book_id}

# Response:
{
  "message": "Book deleted successfully",
  "book_id": "abc-123",
  "book_title": "Anna_Karenina",
  "deleted_characters": 4,
  "deleted_images": 3
}
```

### 2. Fixed Automatic Duplicate Detection

**File:** [backend/routes/books_routes.py:163-206](backend/routes/books_routes.py#L163-L206)

**Before (Broken):**
```python
# Checked BEFORE extracting metadata - filename doesn't match title
db = get_db()
existing_book = db.query(Book).filter(Book.title == filename).first()
# filename = "anna_karenina.pdf"
# book.title = "Anna_Karenina" (from PDF metadata)
# No match found, duplicate created!
```

**After (Fixed):**
```python
# Extract title from metadata FIRST
title = metadata.get('title', os.path.splitext(filename)[0])

# AUTO-DELETE DUPLICATES: Check for existing books with same title
existing_books = db.query(Book).filter(Book.title == title).all()
if existing_books:
    logger.warning(f"Auto-deleting {len(existing_books)} duplicate book(s)")

    for existing_book in existing_books:
        # Delete characters, images (database + files), FAISS indices
        # ... (complete cleanup)
        db.delete(existing_book)

    db.commit()
    logger.info("✓ Deleted duplicates, proceeding with upload")
```

**Key improvements:**
- ✅ Checks AFTER metadata extraction (compares actual titles)
- ✅ Finds ALL duplicates (not just first one)
- ✅ Deletes physical files (images, FAISS indices)
- ✅ Automatic - no user intervention needed

### 3. Added Frontend deleteBook API

**File:** [frontend/src/api/client.js:79-82](frontend/src/api/client.js#L79-L82)

```javascript
export const deleteBook = async (bookId) => {
  const response = await apiClient.delete(`/books/${bookId}`);
  return response.data;
};
```

**Ready for future UI integration:**
- Can add "Delete" button to book cards
- Can implement bulk delete
- Can add "Clear All Books" admin feature

## Testing

### 1. Clean up existing duplicates

```bash
# Already done - Deleted duplicate Anna_Karenina books
sqlite3 data/storymind.db "SELECT id, title FROM books;"
# Result: Only 1 book (Harry Potter) remains
```

### 2. Test automatic duplicate detection

```bash
# Upload the same book twice
curl -F "file=@Anna_Karenina.pdf" http://localhost:5001/api/books/upload
# Wait for completion

curl -F "file=@Anna_Karenina.pdf" http://localhost:5001/api/books/upload
# Should auto-delete first upload and process second

# Check database - should only have 1 Anna_Karenina
sqlite3 data/storymind.db "SELECT COUNT(*) FROM books WHERE title = 'Anna_Karenina';"
# Expected: 1
```

### 3. Test DELETE endpoint

```bash
# Get book ID
BOOK_ID=$(sqlite3 data/storymind.db "SELECT id FROM books LIMIT 1;")

# Delete book
curl -X DELETE http://localhost:5001/api/books/$BOOK_ID

# Verify deletion
sqlite3 data/storymind.db "SELECT COUNT(*) FROM books WHERE id = '$BOOK_ID';"
# Expected: 0
```

## Impact

### Before Fix:
- ❌ Multiple duplicate books in database
- ❌ No way to delete books via API
- ❌ Manual deletion left orphaned data
- ❌ User confused why duplicates persisted

### After Fix:
- ✅ Automatic duplicate detection and deletion
- ✅ Complete cleanup (database + files)
- ✅ DELETE endpoint for programmatic deletion
- ✅ Clean database with no orphans
- ✅ **User uploads same book twice → automatically replaces old version**

## Files Modified

1. ✅ `backend/routes/books_routes.py`
   - Lines 84-85: Removed broken duplicate check
   - Lines 163-206: Added working duplicate detection
   - Lines 391-500: Added DELETE endpoint

2. ✅ `frontend/src/api/client.js`
   - Lines 79-82: Added deleteBook() function

## Database Status

**Before Fix:**
```
Books: 3 (2 duplicates + 1 unique)
- ae18aaab... | Anna_Karenina | Unknown
- 9d913a50... | Anna_Karenina | Unknown (DUPLICATE)
- 446941de... | harry-potter... | Unknown
```

**After Fix:**
```
Books: 1
- 446941de... | harry-potter-and-the-philosophers-stone-by-jk-rowling | Unknown
```

**Duplicates Removed:** 2 Anna_Karenina entries

## Next Steps

### Optional: Add Delete UI

You can now add a delete button to the frontend:

**`frontend/src/pages/HomePage.jsx`:**
```javascript
import { deleteBook } from '../api/client';

const handleDelete = async (bookId) => {
  if (confirm('Delete this book and all characters?')) {
    try {
      await deleteBook(bookId);
      // Refresh book list
      refetch();
    } catch (err) {
      console.error('Delete failed:', err);
    }
  }
};

// In book card:
<button onClick={() => handleDelete(book.id)}>
  Delete
</button>
```

### Optional: Enhance Duplicate Detection

For even smarter detection:

1. **Fuzzy title matching** - Detect "Anna_Karenina" vs "Anna Karenina"
2. **File hash comparison** - Detect identical files with different names
3. **Ask user** - "Book already exists, replace or keep both?"

## Related Documentation

- [FEATURE_IMPROVEMENTS.md](FEATURE_IMPROVEMENTS.md) - Other recent features
- [CLAUDE.md](CLAUDE.md) - Full project documentation
- [E2E_TEST_GUIDE.md](E2E_TEST_GUIDE.md) - Testing guide

---

**Result:** Books can now be deleted properly, and duplicates are automatically prevented. Database stays clean! 🎯
