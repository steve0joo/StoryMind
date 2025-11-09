"""
Character Deduplication Utility

Identifies and merges duplicate characters that are referred to by different names:
- "Mrs Dursley" and "Petunia" → Same person
- "Harry" and "Harry Potter" → Same person
- "Hermione" and "Hermione Granger" → Same person

Uses fuzzy matching and LLM-based semantic similarity.
"""

import os
from typing import List, Dict, Tuple, Set
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()


class CharacterDeduplicator:
    """
    Identifies duplicate characters using multiple strategies:
    1. Exact substring matching (Harry Potter contains Harry)
    2. Fuzzy string matching (Hermione ~ Hermoine)
    3. LLM-based semantic matching (Mrs Dursley ~ Petunia)
    """

    def __init__(self, use_llm: bool = True):
        """
        Initialize deduplicator

        Args:
            use_llm: Whether to use Gemini for semantic matching
        """
        self.use_llm = use_llm

        if use_llm:
            try:
                import google.generativeai as genai
                api_key = os.getenv('GOOGLE_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    print("✓ Gemini configured for character deduplication")
                else:
                    self.use_llm = False
                    print("⚠️  GOOGLE_API_KEY not found, using fuzzy matching only")
            except Exception as e:
                self.use_llm = False
                print(f"⚠️  Gemini not available: {e}")

    def find_duplicates(self, character_names: List[str]) -> List[Set[str]]:
        """
        Find groups of duplicate character names

        Args:
            character_names: List of character names

        Returns:
            List of sets, where each set contains duplicate names
            Example: [{'Harry Potter', 'Harry'}, {'Mrs Dursley', 'Petunia'}]
        """
        print(f"\nFinding duplicates among {len(character_names)} characters...")

        duplicates = []
        processed = set()

        for i, name1 in enumerate(character_names):
            if name1 in processed:
                continue

            group = {name1}

            for j, name2 in enumerate(character_names[i+1:], start=i+1):
                if name2 in processed:
                    continue

                if self._are_duplicates(name1, name2):
                    group.add(name2)
                    processed.add(name2)

            if len(group) > 1:
                duplicates.append(group)
                print(f"  Found duplicate group: {group}")

            processed.add(name1)

        return duplicates

    def _are_duplicates(self, name1: str, name2: str) -> bool:
        """
        Check if two names refer to the same character

        Strategies:
        1. Substring matching (Harry Potter contains Harry)
        2. Fuzzy matching (similarity > 0.8)
        3. LLM semantic matching (Mrs Dursley ~ Petunia)
        """
        # Strategy 1: Exact substring match
        if self._is_substring_match(name1, name2):
            return True

        # Strategy 2: High fuzzy similarity
        if self._fuzzy_similarity(name1, name2) > 0.85:
            return True

        # Strategy 3: LLM semantic match
        if self.use_llm and self._llm_semantic_match(name1, name2):
            return True

        return False

    def _is_substring_match(self, name1: str, name2: str) -> bool:
        """
        Check if one name is a substring of another

        Examples:
        - "Harry" in "Harry Potter" → True
        - "Hermione" in "Hermione Granger" → True
        """
        lower1, lower2 = name1.lower(), name2.lower()

        # Remove common prefixes/suffixes
        prefixes = ['mr ', 'mrs ', 'miss ', 'ms ', 'dr ', 'professor ']
        for prefix in prefixes:
            if lower1.startswith(prefix):
                lower1 = lower1[len(prefix):]
            if lower2.startswith(prefix):
                lower2 = lower2[len(prefix):]

        # Check if one is substring of other
        return lower1 in lower2 or lower2 in lower1

    def _fuzzy_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate fuzzy string similarity (0.0 to 1.0)

        Uses SequenceMatcher for Levenshtein-like distance
        """
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

    def _llm_semantic_match(self, name1: str, name2: str) -> bool:
        """
        Use Gemini to determine if names refer to same character

        Examples that should match:
        - "Mrs Dursley" and "Petunia" (married name vs first name)
        - "The Boy Who Lived" and "Harry Potter" (title vs name)
        """
        if not self.use_llm:
            return False

        try:
            prompt = f"""Are these two names referring to the same character in a book?

Name 1: {name1}
Name 2: {name2}

Answer with ONLY "YES" or "NO". No explanation.

Consider:
- Married names vs maiden names (Mrs Smith vs Mary)
- First names vs full names (Harry vs Harry Potter)
- Titles vs names (Professor McGonagall vs McGonagall)
- Nicknames vs real names (Ron vs Ronald)

Answer:"""

            response = self.model.generate_content(
                prompt,
                generation_config={'temperature': 0.0}
            )

            answer = response.text.strip().upper()
            return answer == "YES"

        except Exception as e:
            print(f"  ⚠️  LLM check failed for {name1} vs {name2}: {e}")
            return False

    def get_canonical_name(self, duplicate_group: Set[str]) -> str:
        """
        Choose the best canonical name from a duplicate group

        Priority:
        1. Longest name (most complete)
        2. Contains both first and last name
        3. No title prefixes

        Example: {'Harry', 'Harry Potter'} → 'Harry Potter'
        """
        names = list(duplicate_group)

        # Remove title prefixes for comparison
        prefixes = ['mr ', 'mrs ', 'miss ', 'ms ', 'dr ', 'professor ']

        def clean_name(name):
            lower = name.lower()
            for prefix in prefixes:
                if lower.startswith(prefix):
                    return name[len(prefix):]
            return name

        # Prefer names without titles
        untitled = [n for n in names if clean_name(n) == n]
        if untitled:
            names = untitled

        # Prefer longer names (more complete)
        names.sort(key=lambda n: (len(n.split()), len(n)), reverse=True)

        return names[0]

    def deduplicate_characters(
        self,
        character_names: List[str]
    ) -> Tuple[List[str], Dict[str, str]]:
        """
        Remove duplicate characters and return canonical names

        Args:
            character_names: Original list of character names

        Returns:
            Tuple of (unique_names, alias_map)
            - unique_names: Deduplicated list
            - alias_map: Mapping of duplicate names to canonical names
              Example: {'Harry': 'Harry Potter', 'Petunia': 'Mrs Dursley'}
        """
        # Find duplicate groups
        duplicate_groups = self.find_duplicates(character_names)

        # Build alias map
        alias_map = {}
        unique_names = set(character_names)

        for group in duplicate_groups:
            canonical = self.get_canonical_name(group)

            for name in group:
                if name != canonical:
                    alias_map[name] = canonical
                    unique_names.discard(name)

        result = sorted(list(unique_names))

        print(f"\nDeduplication Results:")
        print(f"  Original: {len(character_names)} characters")
        print(f"  Deduplicated: {len(result)} characters")
        print(f"  Removed: {len(character_names) - len(result)} duplicates")

        if alias_map:
            print(f"\nAliases found:")
            for alias, canonical in alias_map.items():
                print(f"  '{alias}' → '{canonical}'")

        return result, alias_map


# Standalone test function
if __name__ == "__main__":
    print("Character Deduplication - Test Mode")
    print("=" * 60)

    # Test with Harry Potter characters
    test_names = [
        "Harry Potter",
        "Harry",
        "Hermione Granger",
        "Hermione",
        "Ron Weasley",
        "Ron",
        "Mrs Dursley",
        "Petunia",
        "Petunia Dursley",
        "Mr Dursley",
        "Vernon",
        "Vernon Dursley",
        "Dumbledore",
        "Albus Dumbledore",
        "Professor Dumbledore",
        "Hagrid",
        "Rubeus Hagrid"
    ]

    dedup = CharacterDeduplicator(use_llm=True)
    unique, aliases = dedup.deduplicate_characters(test_names)

    print("\n" + "=" * 60)
    print("Final unique characters:")
    for i, name in enumerate(unique, 1):
        print(f"  {i}. {name}")
