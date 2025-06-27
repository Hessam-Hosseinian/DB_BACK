from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_session import Session
import os
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback
from startup import on_startup
from routes import user_bp, game_bp, category_bp, leaderboard_bp

def create_app(config_name='default'):
    load_dotenv()
    app = Flask(__name__)

    # Load configuration
    from config import config
    app.config.from_object(config[config_name])

    # Enable CORS
    CORS(app, supports_credentials=True, origins=app.config.get('CORS_ORIGINS', '*'))

    # Enable server-side sessions
    Session(app)

    # Logging setup
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

    # Register blueprints
    app.register_blueprint(category_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(leaderboard_bp)

    # Any startup routines
    on_startup()

    # Request logging
    @app.before_request
    def before_request():
        app.logger.info(f'Request: {request.method} {request.url} - {dict(request.headers)}')

    # Security headers
    @app.after_request
    def add_security_headers(response):
        for header, value in app.config.get('SECURITY_HEADERS', {}).items():
            response.headers[header] = value
        response.headers['X-Request-ID'] = request.environ.get('REQUEST_ID', '')
        return response

    # Error handling
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'error': 'Bad request',
            'message': str(error)
        }), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error("Unhandled Exception", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

    # Utility routes
    @app.route("/routes")
    def list_routes():
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
            output.append({
                "endpoint": rule.endpoint,
                "methods": methods,
                "route": str(rule)
            })
        return {"routes": output}

    @app.route("/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": strftime('%Y-%m-%d %H:%M:%S'),
            "version": os.getenv('APP_VERSION', '1.0.0')
        })

    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'default'))
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
