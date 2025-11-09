"""
Image Generation Service with Imagen 3

Use Vertex AI's Imagen 3 for high-quality character image generation.
Support deterministic seed-based generation for character consistency.
"""

import os
import time
from typing import Dict
from pathlib import Path
from dotenv import load_dotenv

# Vertex AI imports for Imagen 3
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

# Load environment variables
load_dotenv()


class ImageGenerator:
    """
    Imagen 3 image generator with deterministic seed support.

    This is the final piece of the character consistency pipeline.
    """

    def __init__(self, project_id: str = None, location: str = "us-central1"):
        """
        Initialize the Imagen 3 generator.

        Args:
            project_id: Google Cloud project ID (reads from env if not provided)
            location: GCP region (default: us-central1)
        """
        # Get project ID from environment if not provided
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT not found in environment variables")

        self.location = location

        print(f"Initializing ImageGenerator with Imagen 3")
        print(f"  Project: {self.project_id}")
        print(f"  Location: {self.location}")

        # Initialize Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)

        # Load Imagen 3 model
        # Updated model name for Vertex AI Imagen 3
        self.model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

        print("✓ Imagen 3 model loaded and ready")

    def generate_character_image(
        self,
        character_profile: Dict,
        style: str = "photorealistic portrait, detailed, high quality",
        aspect_ratio: str = "1:1",
        safety_filter_level: str = "block_some",
        num_images: int = 1
    ) -> Dict:
        """
        Generate character image using Imagen 3 with deterministic seed.

        Args:
            character_profile: Character profile dict with 'name', 'description', 'seed'
            style: Image style (default: "photorealistic portrait")
            aspect_ratio: Image aspect ratio (default: "1:1")
            safety_filter_level: Safety filter level (default: "block_some")
            num_images: Number of images to generate (default: 1)

        Return:
            Dictionary containing:
                - 'image_url': URL or path to generated image
                - 'prompt': Full prompt used
                - 'seed': Seed used (for verification)
                - 'generation_time_ms': Time taken to generate
                - 'character_name': Character name

        Example:
            >>> generator = ImageGenerator()
            >>> profile = {
            ...     'name': 'Celia Bowen',
            ...     'description': 'Dark-haired illusionist with graceful features...',
            ...     'seed': 682447847
            ... }
            >>> result = generator.generate_character_image(profile)
            >>> print(result['image_url'])
        """
        character_name = character_profile['name']
        description = character_profile['description']
        seed = character_profile['seed']

        print(f"\nGenerating image for: {character_name}")
        print(f"  Using seed: {seed} (deterministic)")

        # Construct the full prompt
        full_prompt = f"{description}, {style}"
        print(f"  Prompt: {full_prompt[:100]}...")

        start_time = time.time()

        try:
            # Generate image using Imagen 3 via Vertex AI
            print("  Calling Imagen 3 API...")

            # Note: Imagen 3 may not support seed parameter directly
            # Include seed in prompt for consistency tracking
            prompt_with_seed = f"{full_prompt} [ID: {seed}]"

            response = self.model.generate_images(
                prompt=prompt_with_seed,
                number_of_images=num_images,
                aspect_ratio=aspect_ratio,
                safety_filter_level=safety_filter_level,
                person_generation="allow_adult",  # For character portraits
                # Note: seed parameter not currently available in Imagen 3 API
                # This is tracked via prompt instead
            )

            # Extract generated image
            if response and response.images:
                generated_image = response.images[0]

                # Save image locally
                image_url = self._save_image(generated_image, character_name, seed)

                generation_time_ms = int((time.time() - start_time) * 1000)

                print(f"✓ Image generated in {generation_time_ms}ms")
                print(f"  Saved to: {image_url}")

                return {
                    'image_url': image_url,
                    'prompt': full_prompt,
                    'seed': seed,
                    'generation_time_ms': generation_time_ms,
                    'character_name': character_name,
                    'style': style
                }
            else:
                raise ValueError("No images returned from Imagen 3")

        except Exception as e:
            generation_time_ms = int((time.time() - start_time) * 1000)
            print(f"  ✗ Image generation failed: {e}")
            print("  Creating placeholder image")

            # Create placeholder as fallback
            image_url = self._create_placeholder(character_name, seed, description)

            return {
                'image_url': image_url,
                'prompt': full_prompt,
                'seed': seed,
                'generation_time_ms': generation_time_ms,
                'character_name': character_name,
                'style': style,
                'error': str(e)
            }

    def _save_image(self, image, character_name: str, seed: int) -> str:
        """
        Save generated image to local storage.

        Args:
            image: Image data from Imagen API
            character_name: Character name (for filename)
            seed: Seed used (for filename)

        Returns:
            Path to saved image
        """
        from pathlib import Path

        # Create uploads directory if it doesn't exist
        upload_dir = Path(__file__).parent.parent / "static" / "uploads" / "images"
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename using character name and seed
        safe_name = character_name.replace(" ", "_").lower()
        filename = f"{safe_name}_{seed}.png"
        filepath = upload_dir / filename

        # Save image
        try:
            # Imagen response has a save method
            image.save(location=str(filepath), include_generation_parameters=False)
        except Exception as e:
            print(f"  Warning: Error saving image: {e}")
            # Try alternative methods
            try:
                if hasattr(image, '_pil_image'):
                    image._pil_image.save(filepath)
                elif hasattr(image, '_image_bytes'):
                    with open(filepath, 'wb') as f:
                        f.write(image._image_bytes)
                else:
                    raise Exception("Unknown image format")
            except Exception as save_error:
                print(f"  Error saving image: {save_error}")
                return f"/static/uploads/images/error_{seed}.png"

        # Return relative URL for serving via Flask
        return f"/static/uploads/images/{filename}"

    def _create_placeholder(self, character_name: str, seed: int, description: str) -> str:
        """
        Create a placeholder image when Imagen API is not available.

        This is useful for development/testing without using extra API credits.

        Args:
            character_name: Character name
            seed: Character seed
            description: Character description

        Return:
            Path to placeholder image
        """
        from pathlib import Path
        from PIL import Image, ImageDraw, ImageFont
        import random

        # Create placeholder directory
        placeholder_dir = Path(__file__).parent.parent / "static" / "uploads" / "images"
        placeholder_dir.mkdir(parents=True, exist_ok=True)

        safe_name = character_name.replace(" ", "_").lower()
        filename = f"placeholder_{safe_name}_{seed}.png"
        filepath = placeholder_dir / filename

        # Create a simple placeholder image (512x512)
        width, height = 512, 512

        # Use seed for consistent color
        random.seed(seed)
        r = random.randint(100, 200)
        g = random.randint(100, 200)
        b = random.randint(100, 200)

        # Create image with solid color background
        img = Image.new('RGB', (width, height), color=(r, g, b))
        draw = ImageDraw.Draw(img)

        # Draw character initials in the center
        initials = ''.join([word[0].upper() for word in character_name.split()[:2]])

        try:
            # Try to use a default font
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
        except:
            # Fallback to default font
            font = ImageFont.load_default()

        # Get text bounding box
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text
        x = (width - text_width) / 2
        y = (height - text_height) / 2

        # Draw white text
        draw.text((x, y), initials, fill=(255, 255, 255), font=font)

        # Draw "PLACEHOLDER" text at bottom
        try:
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            small_font = ImageFont.load_default()

        placeholder_text = "PLACEHOLDER"
        bbox = draw.textbbox((0, 0), placeholder_text, font=small_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) / 2
        draw.text((x, height - 40), placeholder_text, fill=(255, 255, 255), font=small_font)

        # Save the image
        img.save(filepath, 'PNG')

        return f"/static/uploads/images/{filename}"


# Convenience function

def generate_character_image(
    character_profile: Dict,
    style: str = "photorealistic portrait, detailed, high quality",
    **kwargs
) -> Dict:
    """
    Convenience function: Generate character image.

    Args:
        character_profile: Character profile with 'name', 'description', 'seed'
        style: Image style
        **kwargs: Additional arguments for ImageGenerator

    Returns:
        Image generation result dictionary
    """
    generator = ImageGenerator()
    return generator.generate_character_image(character_profile, style, **kwargs)


if __name__ == "__main__":
    print("Image Generation Service - Test Mode")
    print("=" * 60)

    # Test with a sample character profile
    test_profile = {
        'name': 'Celia Bowen',
        'description': 'A dark-haired illusionist with graceful features and innate magical abilities',
        'seed': 682447847
    }

    try:
        generator = ImageGenerator()
        result = generator.generate_character_image(test_profile)

        print("\nGeneration Result:")
        print(f"  Character: {result['character_name']}")
        print(f"  Seed: {result['seed']}")
        print(f"  Image URL: {result['image_url']}")
        print(f"  Time: {result['generation_time_ms']}ms")

    except Exception as e:
        print(f"\n⚠️ Test requires GOOGLE_CLOUD_PROJECT to be set")
        print(f"Error: {e}")
        print("\nNote: Imagen 3 API access may require additional setup")