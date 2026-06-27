# Get started with Docker

## Quick Start

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clean database)
docker-compose down -v
```

## Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432
- **Redis**: localhost:6379

## Database Access

```bash
# PostgreSQL
docker-compose exec db psql -U user -d job_hunter

# Redis CLI
docker-compose exec redis redis-cli
```

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose logs db

# Restart database
docker-compose restart db
```

### Celery Not Working
```bash
# Check Redis
docker-compose logs redis

# Restart Celery
docker-compose restart celery_worker celery_beat
```

## Monitoring

```bash
# View all running containers
docker-compose ps

# View logs for specific service
docker-compose logs backend

# Real-time logs
docker-compose logs -f backend
```
