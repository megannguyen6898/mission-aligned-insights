
# Mega X Backend

FastAPI backend for Mega X - AI-Powered Impact Reporting Platform

## Setup Instructions

### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Start PostgreSQL using Docker
docker-compose up db -d

# Create database tables
alembic upgrade head
```

### 3. Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT tokens
- `OPENAI_API_KEY`: OpenAI API key for LLM features
- `XERO_CLIENT_ID` & `XERO_CLIENT_SECRET`: Xero OAuth credentials
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: Google OAuth credentials

### 4. Run the Backend

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh JWT token

### Data Management
- `POST /api/v1/data/upload` - Upload CSV/Excel/JSON files
- `GET /api/v1/data/uploads` - List user uploads
- `DELETE /api/v1/data/uploads/{id}` - Delete upload

### Integrations
- `POST /api/v1/integrations/xero/connect` - Connect Xero
- `POST /api/v1/integrations/google-sheets/connect` - Connect Google Sheets
- `GET /api/v1/integrations/status` - Check integration status

### Dashboards
- `GET /api/v1/dashboards/topics` - Available dashboard topics
- `POST /api/v1/dashboards/generate` - Generate dashboard
- `GET /api/v1/dashboards/{id}` - Get dashboard

### Reports
- `GET /api/v1/reports/frameworks` - Available frameworks
- `POST /api/v1/reports/generate` - Generate impact report
- `GET /api/v1/reports/{id}/download` - Download report

### Investor Matching
- `GET /api/v1/investors/match` - Get matched investors
- `POST /api/v1/investors/pitch-summary` - Generate pitch
- `POST /api/v1/investors/intro-request` - Request introduction

## Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Production Deployment

1. Set production environment variables
2. Use a production WSGI server like Gunicorn
3. Set up proper database connection pooling
4. Configure logging and monitoring
5. Use environment-specific settings

```bash
# Production run example
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```
