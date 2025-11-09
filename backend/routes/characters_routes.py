"""
Characters API Routes
Handles character retrieval and image generation

TODO: Complete implementation for ML/AI Lead
"""

import os
import sys
from flask import Blueprint, request, jsonify

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import Character, GeneratedImage, Book, get_db

# Create Blueprint
characters_bp = Blueprint('characters', __name__)


@characters_bp.route('/', methods=['GET'])
def list_characters():
    """
    Get all characters, optionally filtered by book_id

    GET /api/characters?book_id=<id>

    Response:
    {
        "characters": [
            {
                "id": "char-123",
                "book_id": "book-456",
                "name": "Harry Potter",
                "canonical_description": "A young wizard with...",
                "seed": 1085936863,
                "mention_count": 45,
                "created_at": "2025-11-08T..."
            }
        ],
        "count": 1
    }
    """
    db = get_db()

    try:
        # Get optional book_id filter
        book_id = request.args.get('book_id')

        # Query characters
        query = db.query(Character)
        if book_id:
            query = query.filter(Character.book_id == book_id)

        characters = query.all()

        # Convert to dict
        characters_data = [char.to_dict() for char in characters]

        return jsonify({
            'characters': characters_data,
            'count': len(characters_data)
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve characters',
            'message': str(e)
        }), 500

    finally:
        db.close()


@characters_bp.route('/<character_id>', methods=['GET'])
def get_character(character_id):
    """
    Get a specific character by ID with all details

    GET /api/characters/<character_id>

    Response:
    {
        "character": {
            "id": "char-123",
            "name": "Harry Potter",
            "canonical_description": "...",
            "seed": 1085936863,
            "mention_count": 45,
            "book": {
                "id": "book-456",
                "title": "Harry Potter and the Sorcerer's Stone"
            },
            "images": [
                {
                    "id": "img-789",
                    "image_url": "/static/uploads/images/harry_potter_1085936863.png",
                    "prompt": "...",
                    "generation_time_ms": 15000
                }
            ]
        }
    }
    """
    db = get_db()

    try:
        # Get character
        character = db.query(Character).filter(Character.id == character_id).first()

        if not character:
            return jsonify({
                'error': 'Character not found',
                'character_id': character_id
            }), 404

        # Get character data
        char_data = character.to_dict()

        # Add book info
        book = db.query(Book).filter(Book.id == character.book_id).first()
        if book:
            char_data['book'] = {
                'id': book.id,
                'title': book.title,
                'author': book.author
            }

        # Add images
        images = db.query(GeneratedImage).filter(
            GeneratedImage.character_id == character_id
        ).all()
        char_data['images'] = [img.to_dict() for img in images]

        return jsonify({
            'character': char_data
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve character',
            'message': str(e)
        }), 500

    finally:
        db.close()


@characters_bp.route('/<character_id>/generate-image', methods=['POST'])
def generate_character_image(character_id):
    """
    Generate an image for a character

    POST /api/characters/<character_id>/generate-image

    Request body (optional):
    {
        "style": "photorealistic portrait",
        "aspect_ratio": "1:1"
    }

    Response:
    {
        "image": {
            "id": "img-789",
            "character_id": "char-123",
            "image_url": "/static/uploads/images/harry_potter_1085936863.png",
            "prompt": "A young wizard with black hair and green eyes...",
            "generation_time_ms": 15000,
            "seed": 1085936863
        }
    }

    TODO: Implement image generation
    """
    db = get_db()

    try:
        # Get character
        character = db.query(Character).filter(Character.id == character_id).first()

        if not character:
            return jsonify({
                'error': 'Character not found',
                'character_id': character_id
            }), 404

        # Get style from request (optional)
        data = request.get_json() or {}
        style = data.get('style', 'photorealistic portrait, detailed, high quality')
        aspect_ratio = data.get('aspect_ratio', '1:1')

        # TODO: Generate image using Imagen 3
        # from services.image_service import ImageGenerator
        #
        # generator = ImageGenerator()
        # profile = {
        #     'name': character.name,
        #     'description': character.canonical_description,
        #     'seed': character.seed
        # }
        # result = generator.generate_character_image(
        #     character_profile=profile,
        #     style=style,
        #     aspect_ratio=aspect_ratio
        # )
        #
        # # Save image to database
        # image = GeneratedImage(
        #     character_id=character.id,
        #     prompt=result['prompt'],
        #     style=style,
        #     image_url=result['image_url'],
        #     generation_time_ms=result['generation_time_ms']
        # )
        # db.add(image)
        # db.commit()
        #
        # return jsonify({
        #     'image': image.to_dict(),
        #     'message': 'Image generated successfully'
        # }), 201

        # Temporary response until Imagen is set up
        return jsonify({
            'error': 'Image generation not yet implemented',
            'message': 'Install google-cloud-aiplatform and configure Vertex AI',
            'character': character.to_dict()
        }), 501  # Not Implemented

    except Exception as e:
        return jsonify({
            'error': 'Failed to generate image',
            'message': str(e)
        }), 500

    finally:
        db.close()


@characters_bp.route('/<character_id>', methods=['DELETE'])
def delete_character(character_id):
    """
    Delete a character and all associated images

    DELETE /api/characters/<character_id>

    Response:
    {
        "message": "Character deleted successfully",
        "character_id": "char-123"
    }
    """
    db = get_db()

    try:
        # Get character
        character = db.query(Character).filter(Character.id == character_id).first()

        if not character:
            return jsonify({
                'error': 'Character not found',
                'character_id': character_id
            }), 404

        # Delete character (cascade deletes images)
        db.delete(character)
        db.commit()

        return jsonify({
            'message': 'Character deleted successfully',
            'character_id': character_id
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({
            'error': 'Failed to delete character',
            'message': str(e)
        }), 500

    finally:
        db.close()


# Health check for characters service
@characters_bp.route('/health', methods=['GET'])
def characters_health():
    """
    Health check for characters service

    GET /api/characters/health
    """
    db = get_db()

    try:
        # Count characters
        count = db.query(Character).count()

        return jsonify({
            'status': 'healthy',
            'service': 'characters',
            'total_characters': count
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

    finally:
        db.close()
