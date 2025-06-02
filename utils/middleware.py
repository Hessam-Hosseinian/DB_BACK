from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def init_middleware(app):
    """Initialize middleware for the Flask application"""
    limiter.init_app(app)
    
    # Custom rate limit handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {
            "error": "Rate limit exceeded",
            "message": str(e.description)
        }, 429
    
    return app 