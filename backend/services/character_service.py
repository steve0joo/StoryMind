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

        # Create prompt template
        prompt_template = PromptTemplate(
            input_variables=["text", "max_chars"],
            template="""You are a literary analysis expert. Extract the main character names from this book text.

IMPORTANT:
- Extract FULL NAMES (first and last name) when available
- Include ONLY main characters (not minor/background characters)
- Maximum {max_chars} characters
- Return as a JSON array of strings
- Use the exact names as they appear in the text

Text:
{text}

Return ONLY a valid JSON array, nothing else. Example format:
["Character One", "Character Two", "Character Three"]

JSON array of character names:"""
        )

        # Format the prompt
        prompt = prompt_template.format(text=book_text[:15000], max_chars=max_characters)  # Use first 15k chars

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
            template="""You are a literary analyst. Create a comprehensive character description.

Character: {character_name}

Text mentions:
{context}

Create a canonical description that:
- Summarize physical appearance (if mentioned)
- Describe personality traits and motivations
- Note key relationships and roles
- Use present tense ("is", not "was")
- Is 3-5 sentences long
- Is accurate to the text (no speculation)

Canonical description:"""
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
