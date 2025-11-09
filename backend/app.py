"""
StoryMind Backend - Flask Application
Main entry point for the Flask REST API server
"""

import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///data/storymind.db')

#makes it so that the front end can communicate and access the backend
# without this, the browser would block cross-origin requests
# Configure CORS
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, origins=allowed_origins, supports_credentials=True)

# Configure logging
# Enhanced logging with file output and detailed formatting
log_level = logging.INFO if os.getenv('FLASK_DEBUG') == 'True' else logging.WARNING
log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[
        # Console handler - output to terminal
        logging.StreamHandler(),
        # File handler - save logs to file
        logging.FileHandler(os.path.join(log_dir, 'storymind.log'))
    ]
)

logger = logging.getLogger(__name__)

# Ensure upload directories exist
# Ensures that the backend has all the folders it needs 
    # static/uploads/books/
        # whenever users create book files (PDF, TXT) it goes here
    # static/uploads/images/
        # character images are saved here 
    # data/
        # database and other data files are stored here

os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'books'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)


# Request logging middleware
@app.before_request
def log_request_info():
    """Log information about each incoming request"""
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    if request.method in ['POST', 'PUT', 'PATCH']:
        # Log request body for debugging (excluding file uploads)
        if request.content_type and 'multipart/form-data' not in request.content_type:
            logger.debug(f"Request body: {request.get_data(as_text=True)[:200]}")


@app.after_request
def log_response_info(response):
    """Log information about each response"""
    logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running"""
    return jsonify({
        'status': 'healthy',
        'message': 'StoryMind API is running',
        'version': '1.0.0'
    }), 200


# Error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


@app.errorhandler(413)
def file_too_large(error):
    """Handle file upload size errors"""
    return jsonify({
        'error': 'File Too Large',
        'message': 'File size exceeds 50MB limit'
    }), 413


# Import and register API routes
try:
    from routes.books_routes import books_bp
    app.register_blueprint(books_bp, url_prefix='/api/books')
    logger.info("Books routes registered successfully")
except ImportError as e:
    logger.warning(f"Books routes not available: {e}")

# Character routes (will be implemented in Task #8)
try:
    from routes.characters_routes import characters_bp
    app.register_blueprint(characters_bp, url_prefix='/api/characters')
    logger.info("Characters routes registered successfully")
except ImportError as e:
    logger.warning(f"Characters routes not yet implemented: {e}")


if __name__ == '__main__':
    # Development server
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'

    logger.info(f"Starting StoryMind Backend on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Allowed CORS origins: {allowed_origins}")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
