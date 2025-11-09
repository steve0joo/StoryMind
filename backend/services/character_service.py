"""
Character Extraction and Profile Synthesis Service

Two-step process:
1. Extract character names using Gemini 2.5 Flash (LangChain wrapper)
2. Create canonical profiles using RAG + Gemini synthesis

This is where the magic happens - combining RAG retrieval with LLM synthesis.
"""

import os
import json
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Handle imports for both module use and standalone testing
try:
    from .rag_system import BookRAG
    from ..utils.seed_generator import generate_character_seed
except ImportError:
    # Standalone testing mode
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from services.rag_system import BookRAG
    from utils.seed_generator import generate_character_seed

# Load environment variables
load_dotenv()


class CharacterExtractor:
    """
    Character extraction and profile synthesis using Gemini 2.5 Flash.
    """

    def __init__(self, model: str = "gemini-2.0-flash-exp", temperature: float = 0.0):
        """
        Initialize the character extractor.

        Args:
            model: Gemini model to use (default: gemini-2.0-flash-exp)
            temperature: LLM temperature (0 for deterministic)
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        print(f"Initializing CharacterExtractor with model: {model}")

        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature
        )

        print("✓ Gemini 2.5 Flash connected")

    def extract_character_names(self, book_text: str, max_characters: int = 20) -> List[str]:
        """
        Extract main character names from book text (PRD Example 3).

        Uses LangChain's PromptTemplate + Gemini for structured extraction.

        Args:
            book_text: Full or sample text from the book
            max_characters: Maximum number of characters to extract

        Return:
            List of character names (e.g., ["Celia Bowen", "Marco Alisdair"])

        Example:
            >>> extractor = CharacterExtractor()
            >>> names = extractor.extract_character_names(book_text)
            >>> print(names)
            ['Celia Bowen', 'Marco Alisdair', 'Prospero the Enchanter']
        """
        print(f"\nExtracting character names from text ({len(book_text):,} characters)...")

        # Create prompt template with improved instructions
        prompt_template = PromptTemplate(
            input_variables=["text", "max_chars"],
            template="""You are an expert literary analyst specializing in character identification. Your task is to extract the main character names from this book text.

EXTRACTION RULES:
1. Extract FULL NAMES (e.g., "Harry Potter" not just "Harry")
2. Include titles/honorifics if they're part of the character's identity (e.g., "Professor Dumbledore", "Lady Macbeth")
3. Include MAIN characters and ALL SIGNIFICANT SECONDARY characters with names
4. Characters mentioned by name multiple times should be included
5. Exclude generic references (e.g., "the man", "a woman", "the child")
6. Exclude very minor characters mentioned only once in passing
7. Maximum {max_chars} characters total
8. Use exact names as they appear in the text (preserve spelling and capitalization)

Text excerpt:
{text}

OUTPUT FORMAT:
Return ONLY a valid JSON array of character name strings. No explanations, no markdown, just the JSON array.

Example of correct output format:
["Elizabeth Bennet", "Mr. Darcy", "Jane Bennet"]

JSON array of main character names:"""
        )

        # Format the prompt - use more text for comprehensive character extraction
        # Sample text throughout the book (beginning, middle, end) to catch all characters
        text_len = len(book_text)
        if text_len <= 30000:
            # Short book - use entire text
            sample_text = book_text
        else:
            # Long book - sample from beginning, middle, and end (10k chars each)
            beginning = book_text[:10000]
            middle_start = text_len // 2 - 5000
            middle = book_text[middle_start:middle_start + 10000]
            end = book_text[-10000:]
            sample_text = f"{beginning}\n\n[... middle section ...]\n\n{middle}\n\n[... later section ...]\n\n{end}"

        prompt = prompt_template.format(text=sample_text, max_chars=max_characters)

        # Call Gemini
        response = self.llm.invoke(prompt)
        response_text = response.content.strip()

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            character_names = json.loads(response_text)

            if not isinstance(character_names, list):
                raise ValueError("Response is not a list")

            print(f"✓ Extracted {len(character_names)} characters")
            return character_names

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to parse JSON response: {e}")
            print(f"Raw response: {response_text[:200]}...")
            return []

    def create_canonical_profile(
        self,
        character_name: str,
        rag_system: BookRAG,
        num_mentions: int = 10
    ) -> Dict:
        """
        Create a canonical character profile.

        Combine RAG retrieval with LLM synthesis.

        Process:
            1. Use RAG to find all mentions of the character
            2. Use Gemini to synthesize mentions into canonical description
            3. Generate deterministic seed for image consistency

        Args:
            character_name: Name of the character
            rag_system: BookRAG instance (must be indexed)
            num_mentions: Number of text chunks to retrieve

        Return:
            Dictionary containing:
                - 'name': Character name
                - 'description': Canonical description (synthesized)
                - 'seed': Deterministic seed for image generation
                - 'mention_count': Number of chunks found
                - 'raw_mentions': List of text chunks (for debugging)

        Example:
            >>> profile = extractor.create_canonical_profile("Celia Bowen", rag)
            >>> print(profile['description'])
            'Celia Bowen is a young illusionist with innate magical abilities...'
            >>> print(profile['seed'])
            682447847
        """
        print(f"\nCreating canonical profile for: {character_name}")

        # Step 1: Retrieve character mentions using RAG
        print(f"  1. Retrieving {num_mentions} mentions from RAG...")
        mentions = rag_system.find_character_mentions(character_name, k=num_mentions)

        if not mentions:
            print(f"  ⚠ No mentions found for {character_name}")
            return {
                'name': character_name,
                'description': f"{character_name} (no description available)",
                'seed': generate_character_seed(character_name),
                'mention_count': 0,
                'raw_mentions': []
            }

        # Combine mentions into context
        context = "\n\n".join([f"[Mention {i+1}]\n{m}" for i, m in enumerate(mentions)])

        # Step 2: Synthesize canonical description using Gemini
        print(f"  2. Synthesizing canonical description with Gemini...")

        synthesis_prompt = PromptTemplate(
            input_variables=["character_name", "context"],
            template="""You are an expert literary analyst. Create a canonical character description for image generation.

Character Name: {character_name}

Text Excerpts:
{context}

DESCRIPTION REQUIREMENTS:
1. Physical Appearance: Include ALL physical details mentioned (hair color, eye color, build, height, distinctive features, clothing style)
2. Age/Demographics: Include approximate age, gender, ethnicity if mentioned
3. Personality: Key personality traits evident from the text
4. Role: Their role/occupation in the story
5. Distinctive Features: Any unique characteristics that make them visually distinctive

STYLE GUIDELINES:
- Write in present tense ("is", "has", "wears" not "was", "had", "wore")
- Be specific and concrete (good: "has long black hair", bad: "is attractive")
- 4-6 sentences recommended
- Prioritize visual details that will help with image generation
- Base ONLY on evidence from the text excerpts (no speculation or assumptions)
- Avoid vague terms like "beautiful", "handsome" - describe specific features instead

IMPORTANT FOR IMAGE GENERATION:
Focus on physical, visual characteristics that an AI image generator can render. Psychological traits should be mentioned only if they manifest physically (e.g., "appears confident" is better than "is confident").

Canonical visual description:"""
        )

        prompt = synthesis_prompt.format(character_name=character_name, context=context[:10000])  # Limit context

        response = self.llm.invoke(prompt)
        canonical_description = response.content.strip()

        # Step 3: Generate deterministic seed
        print(f"  3. Generating deterministic seed...")
        seed = generate_character_seed(character_name)

        profile = {
            'name': character_name,
            'description': canonical_description,
            'seed': seed,
            'mention_count': len(mentions),
            'raw_mentions': mentions  # Keep for debugging
        }

        print(f"✓ Profile created")
        print(f"  - Description: {canonical_description[:100]}...")
        print(f"  - Seed: {seed}")
        print(f"  - Mentions: {len(mentions)}")

        return profile


# Convenience functions for direct use

def extract_characters(book_text: str, max_characters: int = 20) -> List[str]:
    """
    Convenience function: Extract character names from book text.

    Args:
        book_text: Text content of the book
        max_characters: Maximum number of characters to extract

    Return:
        List of character names
    """
    extractor = CharacterExtractor()
    return extractor.extract_character_names(book_text, max_characters)


def create_canonical_profile(
    character_name: str,
    rag_system: BookRAG,
    num_mentions: int = 10
) -> Dict:
    """
    Convenience function: Create canonical character profile.

    Args:
        character_name: Name of the character
        rag_system: BookRAG instance (must be indexed)
        num_mentions: Number of mentions to retrieve

    Return:
        Character profile dictionary
    """
    extractor = CharacterExtractor()
    return extractor.create_canonical_profile(character_name, rag_system, num_mentions)


if __name__ == "__main__":
    print("Character Service - Test Mode")
    print("=" * 60)

    # Test with sample text
    sample_text = """
    Celia Bowen was born with magic coursing through her veins. Her father, Prospero the Enchanter,
    recognized her talent immediately and began training her from a young age. She is dark-haired
    and graceful, with an innate ability to manipulate reality itself.

    Marco Alisdair, in contrast, learned his magic through rigorous study under the mysterious
    man in the grey suit. He is calculating and methodical, with blonde hair and sharp features.
    Marco works behind the scenes at the Night Circus.

    The rivalry between Celia and Marco forms the heart of the story, though neither understands
    the full stakes of their competition.
    """

    try:
        # Test character extraction
        extractor = CharacterExtractor()
        names = extractor.extract_character_names(sample_text, max_characters=5)
        print("\nExtracted characters:")
        for name in names:
            print(f"  - {name}")

    except Exception as e:
        print(f"\n⚠ Test requires GOOGLE_API_KEY to be set")
        print(f"Error: {e}")
