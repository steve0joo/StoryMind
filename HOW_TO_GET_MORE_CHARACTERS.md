# How To Get More Characters - Quick Guide

**Issue:** Current books only show 5 and 3 characters (extracted with old limits)

**Solution:** Re-upload books to trigger re-extraction with new limits

---

## Why Only Few Characters Now?

Your existing books were extracted **before** I increased the limits:

**Old Settings (when books were uploaded):**
- Analyzed: First 10 chunks (~10,000 characters)
- Max characters: 20
- **Result:** Only found 5 main characters in Harry Potter

**New Settings (current code):**
- Analyzed: First 50 chunks (~50,000 characters) ✅
- Max characters: 50 ✅
- **Expected:** 15-30 characters in Harry Potter

---

## Solution 1: Re-upload Harry Potter (RECOMMENDED) ⭐

### Step 1: Upload the File Again

1. Go to homepage: http://localhost:5173
2. Click "Upload Book"
3. Select: `harry-potter-and-the-philosophers-stone-by-jk-rowling.pdf`
4. Click "Upload"

### Step 2: Automatic Duplicate Handling

The system will automatically:
1. Detect duplicate filename ✅
2. Delete old book + 5 characters ✅
3. Process book with NEW limits (50 chunks, 50 max) ✅
4. Extract 15-30 characters ✅
5. Create FAISS index ✅

**Processing time:** ~3-5 minutes

### Step 3: View Results

Navigate to Harry Potter book and you should see:
- Harry Potter
- Hermione Granger ✨ NEW
- Ron Weasley ✨ NEW
- Albus Dumbledore ✨ NEW
- Severus Snape ✨ NEW
- Mr Dursley
- Mrs Dursley
- Dudley
- Hagrid ✨ NEW
- Professor McGonagall ✨ NEW
- Quirrell ✨ NEW
- Vernon Dursley ✨ NEW
- Petunia Dursley ✨ NEW
- ...and more!

**Expected total:** 15-30 characters (depending on how many are mentioned in first 50 chunks)

---

## Solution 2: Upload a New Book (Alternative)

Upload a different book to test the new extraction:

**Good test books:**
- Pride and Prejudice (many characters)
- The Great Gatsby (10-15 characters)
- Alice in Wonderland (15-20 characters)

---

## Solution 3: Manual Re-extraction (Advanced)

I created a script, but it's complex and requires:
- Gemini API quota (1 extraction call per book)
- Careful handling of FAISS index
- ~10 minutes processing time

**Script:** `backend/scripts/reextract_characters.py`

**Not recommended** unless you want to keep existing generated images.

---

## What Happens to Generated Images?

### When Re-uploading:
- ✅ Old book deleted (including characters and images)
- ⚠️ Existing images lost (Mrs Dursley, Mr Dursley, etc.)
- ✅ Can regenerate images for new characters

### If You Want to Keep Images:
- Use Solution 3 (manual re-extraction script)
- Or regenerate images after re-upload (just click "Generate Image")

---

## Comparison

| Method | Time | Keeps Images | Difficulty |
|--------|------|-------------|-----------|
| **Re-upload** | 3-5 min | ❌ No | ⭐ Easy |
| **New book** | 3-5 min | N/A | ⭐ Easy |
| **Script** | 10 min | ✅ Yes | ⭐⭐⭐ Advanced |

---

## Expected Results

### Harry Potter (First 50 chunks = ~50,000 characters)

**Will definitely include:**
- Harry Potter (protagonist)
- Hermione Granger
- Ron Weasley
- Albus Dumbledore
- Hagrid
- Mr & Mrs Dursley
- Dudley
- Professor McGonagall
- Severus Snape
- Draco Malfoy
- Neville Longbottom
- Quirrell
- Petunia & Vernon Dursley
- Mrs Potter

**Might include:**
- Fred & George Weasley
- Ginny Weasley
- Molly & Arthur Weasley
- Oliver Wood
- Seamus Finnigan
- Dean Thomas
- Crabbe & Goyle
- Argus Filch
- Nearly Headless Nick

**Total:** 15-30 characters

---

## Step-by-Step: Re-upload Harry Potter

### 1. Prepare
- Ensure backend and frontend are running
- Have the PDF file ready

### 2. Upload
```
1. Go to: http://localhost:5173
2. Click "Upload Book" button
3. Select: harry-potter-and-the-philosophers-stone-by-jk-rowling.pdf
4. Click "Upload"
```

### 3. Wait for Processing

You'll see progress:
```
Uploading... → Processing... → Extracting characters... → Done!
```

Watch backend logs:
```
Duplicate book detected: harry-potter...
Deleting existing book...
Processing book with 50 chunks...
Extracted 23 characters: ['Harry Potter', 'Hermione', 'Ron', ...]
```

### 4. View Results

Navigate to the book and see all new characters!

---

## Troubleshooting

### Issue: "Quota exceeded" error

**Cause:** Gemini API daily limit (50 requests/day)

**Solutions:**
- Wait until tomorrow (quota resets daily)
- Enable Google Cloud billing ($300 free credits)
- Upload tomorrow when quota refreshed

### Issue: Processing takes >5 minutes

**Normal for first book of the day:**
- FAISS indexing: ~30 seconds
- Character extraction: ~15 seconds per character
- For 20 characters: ~5-6 minutes total

### Issue: Still only shows 5 characters

**Check:**
1. Did you upload the SAME file? (duplicate prevention triggered?)
2. Check backend logs - look for "Extracted X characters"
3. Refresh browser (F5)

---

## API Quota Management

**Character extraction uses Gemini API:**
- 1 extraction call per book upload
- Each extraction can find up to 50 characters

**Daily limits (free tier):**
- 50 requests/day
- Each book upload = 1 request
- You can upload ~50 books per day

**Recommendation:**
- Enable Google Cloud billing ($300 free credits)
- Or be strategic: only upload books you'll demo

---

## Next Steps

### Recommended Action:
1. **Re-upload Harry Potter now** (takes 3 minutes)
2. See 15-30 characters instead of 5
3. Generate images for your favorite characters
4. Ready for demo! 🎉

### Optional:
- Upload 2-3 more books for variety
- Test with books that have many characters
- Pre-generate images for top 10 characters

---

**Status:** Ready to re-upload! Just follow Step 1 above. ✅

**Last Updated:** November 9, 2025
