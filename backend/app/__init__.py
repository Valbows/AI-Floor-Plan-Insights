"""
AI Floor Plan and Market Insights - Flask Application Factory
Main application initialization and configuration
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Celery
celery = Celery(
    __name__,
    broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
)


def create_app(config_name='development'):
    """
    Flask application factory
    
    Args:
        config_name: Configuration environment (development, testing, production)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # ================================
    # Configuration
    # ================================
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE_MB', 10)) * 1024 * 1024
    
    # Celery configuration
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')
    
    # ================================
    # Extensions
    # ================================
    
    # CORS - Allow frontend origins
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # JWT Authentication
    jwt = JWTManager(app)
    
    # Update Celery config
    celery.conf.update(app.config)
    
    # ================================
    # Error Handlers (OWASP Compliant)
    # ================================
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be understood or was missing required parameters.'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource.'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource could not be found.'
        }), 404
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle 413 File Too Large errors"""
        max_size = app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
        return jsonify({
            'error': 'File Too Large',
            'message': f'File size exceeds the maximum allowed size of {max_size}MB.'
        }), 413
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        app.logger.error(f'Internal Server Error: {error}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500
    
    # ================================
    # Health Check Endpoint
    # ================================
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for Docker and monitoring"""
        return jsonify({
            'status': 'healthy',
            'service': 'AI Floor Plan Insights API',
            'version': '1.0.0'
        }), 200
    
    # ================================
    # Register Blueprints (Routes)
    # ================================
    
    # Import blueprints here to avoid circular imports
    # from app.routes.auth import auth_bp
    # from app.routes.properties import properties_bp
    # from app.routes.public import public_bp
    
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(properties_bp, url_prefix='/api/properties')
    # app.register_blueprint(public_bp, url_prefix='/api/public')
    
    # ================================
    # Logging Configuration
    # ================================
    
    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('AI Floor Plan Insights startup')
    
    return app


# ================================
# Celery Task Context
# ================================

class ContextTask(celery.Task):
    """Custom Celery task that runs within Flask application context"""
    
    def __call__(self, *args, **kwargs):
        with create_app().app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask
