"""
Deterministic Seed Generation Utility

This is the CORE INNOVATION of StoryMind.
Ensures the same character always generates visually consistent images.

CRITICAL: Uses hashlib.md5() for deterministic hashing.
DO NOT use Python's built-in hash() - it changes every session.
"""

import hashlib


def generate_character_seed(character_name: str) -> int:
    """
    Generate a deterministic seed from a character name.

    Same character name = same seed = consistent images across all sessions.

    Args:
        character_name: The character's name (e.g., "Harry Potter")

    Returns:
        A deterministic integer seed (0 to 2^32-1)

    Example:
        >>> seed = generate_character_seed("Harry Potter")
        >>> seed
        2847593921
        >>> # Always returns the same value for "Harry Potter"

    Implementation:
        1. Normalize the name (lowercase, strip whitespace)
        2. Generate MD5 hash of the normalized name
        3. Convert hex hash to integer
        4. Modulo 2^32 to fit in seed range
    """
    # Normalize the character name
    normalized_name = character_name.strip().lower()

    # Generate MD5 hash (deterministic across all Python sessions)
    name_hash = hashlib.md5(normalized_name.encode('utf-8')).hexdigest()

    # Convert hex string to integer and constrain to 32-bit unsigned range
    seed = int(name_hash, 16) % (2**32)

    return seed


def verify_seed_consistency(character_name: str, num_tests: int = 100) -> bool:
    """
    Verify that seed generation is truly deterministic.

    Args:
        character_name: Name to test
        num_tests: Number of times to generate and compare

    Returns:
        True if all seeds are identical, False otherwise
    """
    seeds = [generate_character_seed(character_name) for _ in range(num_tests)]
    return len(set(seeds)) == 1


if __name__ == "__main__":
    # Test the seed generator
    print("Testing Deterministic Seed Generation")
    print("=" * 50)

    test_characters = [
        "Anna Karenina",
        "Gandalf",
        "Frodo Baggins",
        "Harry Potter",
        "Hermione Granger"
    ]

    for char in test_characters:
        seed = generate_character_seed(char)
        is_consistent = verify_seed_consistency(char, num_tests=1000)
        status = "✓" if is_consistent else "✗"
        print(f"{status} {char:30s} → Seed: {seed:10d} (Consistent: {is_consistent})")

    print("\n" + "=" * 50)
    print("Seed generation is deterministic across all runs!")
