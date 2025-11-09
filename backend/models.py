"""
Database Models using SQLAlchemy ORM
Maps Python classes to SQLite tables
"""

from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import os

# Get database URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/storymind.db')

# Fix the database path to be absolute
if DATABASE_URL.startswith('sqlite:///') and not DATABASE_URL.startswith('sqlite:////'):
    # Convert relative path to absolute
    db_path = DATABASE_URL.replace('sqlite:///', '')
    abs_db_path = os.path.join(os.path.dirname(__file__), db_path)
    # Ensure the directory exists
    os.makedirs(os.path.dirname(abs_db_path), exist_ok=True)
    DATABASE_URL = f'sqlite:///{abs_db_path}'

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False},  # SQLite specific
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


class Book(Base):
    """
    Book model - represents uploaded books
    Corresponds to 'books' table in SQLite
    """
    __tablename__ = 'books'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    upload_date = Column(String, default=lambda: datetime.utcnow().isoformat())
    processing_status = Column(String, default='pending')  # pending, processing, completed, failed
    faiss_index_path = Column(String, nullable=True)  # Path to saved FAISS index
    character_count = Column(Integer, default=0)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relationship: One book has many characters
    characters = relationship('Character', back_populates='book', cascade='all, delete-orphan')

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'upload_date': self.upload_date,
            'processing_status': self.processing_status,
            'character_count': self.character_count,
            'created_at': self.created_at
        }


class Character(Base):
    """
    Character model - represents extracted characters from books
    Corresponds to 'characters' table in SQLite
    """
    __tablename__ = 'characters'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = Column(String, ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    canonical_description = Column(Text, nullable=True)  # Synthesized description from all mentions
    seed = Column(Integer, nullable=False)  # Deterministic seed for image generation consistency
    mention_count = Column(Integer, default=0)  # Number of times character is mentioned
    relationships = Column(Text, nullable=True)  # JSON string of character relationships
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    book = relationship('Book', back_populates='characters')
    images = relationship('GeneratedImage', back_populates='character', cascade='all, delete-orphan')

    def to_dict(self, include_images=True):
        """Convert model to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'book_id': self.book_id,
            'name': self.name,
            'canonical_description': self.canonical_description,
            'seed': self.seed,
            'mention_count': self.mention_count,
            'relationships': self.relationships,
            'created_at': self.created_at
        }

        # Include images relationship if requested
        if include_images and self.images:
            data['images'] = [img.to_dict() for img in self.images]

        return data


class GeneratedImage(Base):
    """
    GeneratedImage model - represents AI-generated character images
    Corresponds to 'images' table in SQLite
    """
    __tablename__ = 'images'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    character_id = Column(String, ForeignKey('characters.id', ondelete='CASCADE'), nullable=False)
    prompt = Column(Text, nullable=True)  # Full prompt sent to Imagen 3
    style = Column(String, nullable=True)  # Style modifier (e.g., 'realistic', 'anime')
    image_url = Column(String, nullable=True)  # Path or URL to generated image
    generation_time_ms = Column(Integer, nullable=True)  # Time taken to generate in milliseconds
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relationship
    character = relationship('Character', back_populates='images')

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'prompt': self.prompt,
            'style': self.style,
            'image_url': self.image_url,
            'generation_time_ms': self.generation_time_ms,
            'created_at': self.created_at
        }


def get_db():
    """
    Dependency function to get database session
    Usage in routes:
        db = get_db()
        try:
            # Use db session
            book = db.query(Book).filter(Book.id == book_id).first()
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def init_db():
    """
    Initialize database - create all tables
    This should be called when the application starts
    """
    Base.metadata.create_all(bind=engine)


# Create tables when module is imported (if they don't exist)
if __name__ == "__main__":
    print("Initializing database with SQLAlchemy...")
    init_db()
    print("✅ Database tables created successfully")
