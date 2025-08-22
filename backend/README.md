
# ImpactView Backend

FastAPI backend for ImpactView - AI-Powered Impact Reporting Platform

## Setup Instructions

### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
### 1.1. Backend Build - Must do this to connect to the database

```bash
cd ./backend
docker-compose up --build
```
### 2. Database Setup

```bash
# Start PostgreSQL using Docker
docker-compose up db -d

# Create database tables
## From Docker
docker compose exec backend alembic upgrade head
## From host
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
- `AUTH0_DOMAIN` & `AUTH0_AUDIENCE`: Auth0 settings for JWT verification (optional)
- `FIREBASE_PROJECT_ID`: Firebase project ID for token verification (optional)

### Authentication Setup

The backend verifies incoming JWTs using either Auth0 or Firebase public keys.
Provide the corresponding environment variables above and ensure tokens include a
`roles` claim. Role-based access control is enforced on sensitive routes such as
`POST /api/v1/integrations/sync`, which requires an `admin` role.

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

## Debug Notes
- Fixed a critical error where the User model referenced a non-existent backref (data_uploads)
- Resolved metadata name conflict in SQLAlchemy (metadata is a reserved keyword)
- Discovered an orphaned alembic.ini with no alembic/ folder
- Initialized Alembic and fixed env.py to point to your actual SQLAlchemy Base and models
- Ran alembic upgrade head successfully to create database tables
- Verified in PostgreSQL that all required tables, including `users`, now exist in the `mega_x` database
docker-compose exec db psql -U postgres -d mega_x
\dt
- Radix UI throws Uncaught Error: A <Select.Item /> must have a value prop that is not an empty string, which leads to a blank Investors page. The empty string is reserved for clearing the selection. Replaced empty string with "all."
- Added a top padding class to ensure content appears below the fixed navbar in the authenticated layout