# Backend Setup

## Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and configure:
- DATABASE_URL
- REDIS_URL
- SECRET_KEY
- CORS_ORIGINS

## Running

### Development

```bash
# Terminal 1 - FastAPI server
uvicorn app.main:app --reload

# Terminal 2 - Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3 - Celery beat (scheduler)
celery -A app.workers.celery_app beat --loglevel=info
```

### Production

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## Database

### Create Tables

```bash
python -c "from app.database.core import engine, Base; from app.models.models import *; Base.metadata.create_all(bind=engine)"
```

### Migrations (using Alembic)

```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## API Documentation

Visit `http://localhost:8000/docs` for Swagger documentation.

## Testing

```bash
pytest
pytest --cov=app
```

## Deployment

### Docker

```bash
docker build -f Dockerfile.backend -t job-hunter-backend .
docker run -p 8000:8000 job-hunter-backend
```

### Railway/Render

1. Connect GitHub repository
2. Set environment variables
3. Deploy

## Troubleshooting

- Database connection issues: Check DATABASE_URL format
- Celery not working: Ensure Redis is running
- CORS errors: Update CORS_ORIGINS in .env
