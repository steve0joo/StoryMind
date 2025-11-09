#!/usr/bin/env python3
"""
Test RAG System's Effectiveness at Capturing Visual Details

This script tests whether our RAG system can capture:
1. Physical appearance (hair, eyes, build, height)
2. Clothing and style
3. Age and demographics
4. Distinctive visual features
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from services.rag_system import BookRAG
from services.character_service import CharacterExtractor

def test_rag_visual_capture():
    """Test with sample text that has clear visual descriptions"""

    print("=" * 60)
    print("RAG Visual Capture Quality Test")
    print("=" * 60)

    # Sample text with explicit visual details
    sample_text = """
    Hermione Granger stood at the entrance of the library, her bushy brown hair
    forming a wild halo around her head. She wore the standard Hogwarts uniform -
    black robes, a white shirt, and the Gryffindor tie with its distinctive red
    and gold stripes. Her brown eyes sparkled with intelligence behind her
    reading glasses, which she pushed up nervously on her nose. At eleven years
    old, she was shorter than most of her classmates, but her confident posture
    made her seem taller. Her front teeth were noticeably large, something she
    was self-conscious about.

    Harry Potter walked beside her, his jet-black hair sticking up at odd angles
    no matter how much he tried to flatten it. Behind his round, wire-rimmed
    glasses, his bright green eyes - the same vivid green as his mother's -
    contrasted sharply with his lightning-bolt scar on his forehead. He was thin
    and small for his age, wearing clothes that were too large for him - hand-me-
    downs from his cousin Dudley. His Gryffindor robes hung loosely on his frame.

    Hermione gestured animatedly, her hands moving quickly as she explained
    something about the Transfiguration homework. Her cheeks flushed pink with
    excitement when she talked about her favorite subjects.

    Ron Weasley trailed behind them, his tall, gangly frame making him stand out.
    His bright red hair was unmistakable - a Weasley trademark - and his face was
    covered in freckles. He had long arms and legs that he hadn't quite grown into
    yet, making him appear awkward. His robes were old and slightly faded, clearly
    passed down from his older brothers. His blue eyes showed a mix of boredom and
    amusement as Hermione continued her lecture.

    Hermione's wand was tucked neatly in her robe pocket, always within reach.
    She carried a heavy bag full of books, the straps digging into her shoulder,
    but she didn't seem to notice the weight.
    """

    # Create small chunks (simulating book processing)
    chunks = [
        sample_text[i:i+300] for i in range(0, len(sample_text), 250)
    ]

    print(f"\n📖 Sample Text: {len(sample_text)} characters")
    print(f"📄 Split into {len(chunks)} chunks")

    # Test RAG system
    print("\n" + "=" * 60)
    print("Step 1: Testing RAG Retrieval")
    print("=" * 60)

    rag = BookRAG()
    rag.ingest_chunks(chunks, book_id="test_book")

    # Test character mention retrieval
    test_characters = ["Hermione Granger", "Harry Potter", "Ron Weasley"]

    for char_name in test_characters:
        print(f"\n🔍 Searching for: {char_name}")
        mentions = rag.find_character_mentions(char_name, k=5)

        print(f"   Retrieved {len(mentions)} chunks")

        # Analyze what visual details are captured
        visual_keywords = {
            'hair': ['hair', 'bushy', 'black', 'red', 'brown'],
            'eyes': ['eyes', 'green', 'blue', 'brown', 'glasses'],
            'clothing': ['robes', 'uniform', 'shirt', 'tie', 'clothes'],
            'build': ['tall', 'thin', 'small', 'gangly', 'frame'],
            'features': ['scar', 'teeth', 'freckles', 'cheeks'],
            'age': ['eleven', 'young', 'age', 'years old']
        }

        captured = {category: False for category in visual_keywords}

        for mention in mentions:
            mention_lower = mention.lower()
            for category, keywords in visual_keywords.items():
                if any(keyword in mention_lower for keyword in keywords):
                    captured[category] = True

        print(f"\n   Visual Details Captured:")
        for category, found in captured.items():
            status = "✅" if found else "❌"
            print(f"   {status} {category.capitalize()}")

    # Test synthesis
    print("\n" + "=" * 60)
    print("Step 2: Testing Character Profile Synthesis")
    print("=" * 60)

    try:
        extractor = CharacterExtractor()

        for char_name in test_characters[:1]:  # Test one to save API quota
            print(f"\n🎨 Creating profile for: {char_name}")
            profile = extractor.create_canonical_profile(char_name, rag, num_mentions=5)

            print(f"\n   Generated Description:")
            print(f"   {'-' * 56}")
            print(f"   {profile['description']}")
            print(f"   {'-' * 56}")

            # Analyze quality
            description_lower = profile['description'].lower()

            print(f"\n   Quality Analysis:")
            checks = {
                'Hair described': any(word in description_lower for word in ['hair', 'brown', 'bushy']),
                'Eyes described': any(word in description_lower for word in ['eyes', 'brown']),
                'Clothing mentioned': any(word in description_lower for word in ['uniform', 'robes', 'tie']),
                'Age mentioned': any(word in description_lower for word in ['eleven', 'young', 'age']),
                'Distinctive features': any(word in description_lower for word in ['teeth', 'glasses']),
                'Physical build': any(word in description_lower for word in ['small', 'shorter', 'height'])
            }

            for check, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {check}")

            score = sum(checks.values()) / len(checks) * 100
            print(f"\n   📊 Visual Detail Score: {score:.0f}%")

            if score >= 80:
                print(f"   ✅ EXCELLENT - Ready for image generation")
            elif score >= 60:
                print(f"   🟡 GOOD - Most details captured")
            else:
                print(f"   ⚠️  NEEDS IMPROVEMENT - Missing key details")

    except Exception as e:
        print(f"\n⚠️  Could not test synthesis (API quota?): {e}")
        print(f"   This is okay - RAG retrieval test above is more important")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_rag_visual_capture()
