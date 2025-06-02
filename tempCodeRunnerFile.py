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

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    if isinstance(config_name, str):
        from config import config
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(config_name)
    
    # Initialize extensions
    CORS(app, supports_credentials=True, origins=app.config['CORS_ORIGINS'])
    # CORS(app, supports_credentials=True)
    Session(app)
    cache_manager.init_app(app)
    
    # Setup logging
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
    from routes.user_routes import user_bp
    from routes.game_routes import game_bp
    from routes.category_routes import category_bp
    
    app.register_blueprint(category_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(game_bp)
    on_startup()
    # Request logging middleware
    @app.before_request
    def before_request():
        app.logger.info(f'Request: {request.method} {request.url} - {dict(request.headers)}')

    # Security headers middleware
    @app.after_request
    def add_security_headers(response):
        for header, value in app.config['SECURITY_HEADERS'].items():
            response.headers[header] = value
        return response

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}\n{traceback.format_exc()}')
        return jsonify({'error': 'Internal server error'}), 500

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
            "timestamp": strftime('%Y-%m-%d %H:%M:%S')
        })

    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'default'))
    app.run(debug=app.config['DEBUG'])
