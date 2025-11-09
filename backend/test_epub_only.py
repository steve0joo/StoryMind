#!/usr/bin/env python3
import os
import glob
from services.document_processor import process_book

# Find EPUB file
epub_files = glob.glob("static/uploads/books/*.epub")
print(f"Found {len(epub_files)} EPUB files:")
for f in epub_files:
    print(f"  - {f}")

if epub_files:
    epub_file = epub_files[0]
    print(f"\nTesting EPUB: {epub_file}")
    print(f"File exists: {os.path.exists(epub_file)}")

    try:
        result = process_book(epub_file)
        print(f"\n✅ EPUB Processing SUCCESS!")
        print(f"   Chunks: {result['total_chunks']}")
        print(f"   Characters: {result['total_chars']:,}")
        print(f"   File type: {result['metadata']['file_type']}")
        print(f"   First chunk: {result['chunks'][0][:100]}...")
    except Exception as e:
        print(f"\n❌ EPUB Processing FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\nNo EPUB files found")
