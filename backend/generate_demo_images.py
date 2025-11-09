"""
Generate Demo Character Images with Imagen 3

This script generates character images for your Harry Potter characters
using the real Imagen 3 API.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services import generate_character_image

def main():
    """Generate demo images for Harry Potter characters"""

    print("="*70)
    print(" GENERATING DEMO CHARACTER IMAGES WITH IMAGEN 3")
    print("="*70)

    # Character profiles from our Harry Potter test
    characters = [
        {
            'name': 'Harry Potter',
            'description': 'A young boy, approximately ten years old. He has messy black hair and round glasses. He has a lightning bolt scar on his forehead. He appears brave and determined.',
            'seed': 1085936863
        },
        {
            'name': 'Hermione Granger',
            'description': 'A young girl with bushy brown hair and intelligent brown eyes. She appears studious and confident, often carrying books.',
            'seed': 1240141138
        },
        {
            'name': 'Ron Weasley',
            'description': 'A young boy with flaming red hair and freckles. He has a friendly, loyal expression and appears lanky.',
            'seed': 3456789012  # Example seed
        }
    ]

    print(f"\nGenerating images for {len(characters)} characters...\n")

    results = []
    for i, profile in enumerate(characters, 1):
        print(f"\n{'='*70}")
        print(f"CHARACTER {i}/{len(characters)}: {profile['name']}")
        print(f"{'='*70}")

        try:
            result = generate_character_image(
                profile,
                style="photorealistic portrait, detailed, high quality"
            )

            results.append(result)

            print(f"\n✅ Generated {profile['name']}")
            print(f"   Seed: {result['seed']}")
            print(f"   Image: {result['image_url']}")
            print(f"   Time: {result['generation_time_ms']}ms")

            if 'error' in result:
                print(f"   ⚠️  Note: {result['error'][:100]}")

        except Exception as e:
            print(f"\n❌ Failed to generate {profile['name']}: {e}")
            continue

    # Summary
    print("\n" + "="*70)
    print(" GENERATION COMPLETE")
    print("="*70)

    successful = sum(1 for r in results if 'error' not in r)
    print(f"✅ Successfully generated: {successful}/{len(characters)}")

    if successful > 0:
        print("\nGenerated images:")
        for r in results:
            if 'error' not in r:
                print(f"  - {r['character_name']}: {r['image_url']}")

    print("\nImages saved to: backend/static/uploads/images/")

if __name__ == "__main__":
    main()
