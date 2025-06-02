# Flask Game Application

A Flask-based game application with user management, categories, and game functionality.

## Features

- User authentication and authorization
- Game categories and management
- Rate limiting for API endpoints
- Redis caching for improved performance
- Comprehensive logging
- Security headers and best practices
- Health check endpoint
- API documentation

## Prerequisites

- Python 3.8+
- Redis (for caching)
- PostgreSQL (optional, for persistent storage)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

The application supports different configuration environments:

- Development
- Production
- Testing

Set the `FLASK_ENV` environment variable to choose the configuration:

```bash
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
```

## Running the Application

Development server:

```bash
python app.py
```

Production server:

```bash
gunicorn 'app:create_app()'
```

## Testing

Run tests with pytest:

```bash
pytest
```

## API Documentation

### Endpoints

- `GET /health` - Health check endpoint
- `GET /routes` - List all available routes
- See specific route files for detailed endpoint documentation

### Rate Limiting

- Default limits: 200 requests per day, 50 requests per hour
- Custom limits can be set per endpoint

### Caching

- Redis-based caching
- Default cache timeout: 300 seconds
- Custom cache decorators available

## Security

- CORS protection
- Security headers
- Rate limiting
- Session security
- HTTPS enforcement in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]
