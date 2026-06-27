# AI-Powered Job Hunter Platform

A modern, full-stack web application that automatically finds and tracks job openings from LinkedIn and other job portals based on user-defined filters with AI-powered matching.

## 🌟 Features

### Core Features
- ✅ **AI Job Matching** - Match jobs against your resume with intelligent scoring
- ✅ **Multi-Source Scraping** - LinkedIn, Indeed, Naukri, and more
- ✅ **Smart Filtering** - Configure detailed job preferences
- ✅ **Application Tracking** - Track your job applications with Kanban board
- ✅ **Job Recommendations** - Get personalized job alerts
- ✅ **Dashboard Analytics** - Visualize your job search metrics
- ✅ **Resume Management** - Upload and manage your resume
- ✅ **Notification System** - Email and Telegram alerts

### Technical Features
- 🔐 JWT Authentication with refresh tokens
- 📊 Advanced analytics and reporting
- 🔄 Async job processing with Celery
- 💾 PostgreSQL with proper indexing
- 🚀 Docker containerization
- 📱 Fully responsive design
- 🎨 Modern UI with Tailwind CSS & Shadcn/UI

## 🛠️ Tech Stack

### Frontend
- Next.js 15 with React 19
- TypeScript
- Tailwind CSS
- Shadcn/UI components
- Framer Motion
- React Query (TanStack)
- Axios

### Backend
- FastAPI (Python 3.12)
- SQLAlchemy ORM
- PostgreSQL
- Redis
- Celery for task queue
- JWT authentication

### DevOps
- Docker & Docker Compose
- GitHub Actions CI/CD
- PostgreSQL database
- Redis cache

## 📋 Project Structure

```
linkedIn_scrapper/
├── frontend/
│   ├── app/
│   │   ├── page.tsx (Landing page)
│   │   ├── layout.tsx
│   │   ├── jobs/
│   │   ├── dashboard/
│   │   ├── applications/
│   │   ├── login/
│   │   └── signup/
│   ├── components/
│   │   ├── Header.tsx
│   │   └── JobCard.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   └── useApi.ts
│   ├── lib/
│   │   ├── api.ts
│   │   └── store.ts
│   ├── services/
│   │   └── api.ts
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── jobs.py
│   │   │   ├── filters.py
│   │   │   ├── applications.py
│   │   │   └── dashboard.py
│   │   ├── models/
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   ├── dependencies.py
│   │   │   ├── matching_engine.py
│   │   │   └── scraping_service.py
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   └── tasks.py
│   │   ├── database/
│   │   │   └── core.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── docker-compose.yml
├── Dockerfile.backend
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 18+
- PostgreSQL (or use Docker)
- Redis (or use Docker)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/linkedIn_scrapper.git
cd linkedIn_scrapper
```

2. **Create environment files**
```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run migrations (if using Alembic)
# alembic upgrade head

# Start the server
uvicorn app.main:app --reload

# In another terminal, start Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

## 📚 API Documentation

FastAPI automatically generates Swagger documentation available at:
```
http://localhost:8000/docs
```

### Key Endpoints

**Authentication**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh-token` - Refresh access token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password

**Jobs**
- `GET /jobs/` - List jobs with filters
- `GET /jobs/{id}` - Get job details
- `POST /jobs/{id}/save` - Save job
- `DELETE /jobs/{id}/save` - Unsave job

**Applications**
- `POST /applications/` - Create application
- `GET /applications/` - List applications
- `PUT /applications/{id}` - Update application status

**Filters**
- `POST /filters/` - Create job filter
- `GET /filters/` - List filters
- `PUT /filters/{id}` - Update filter

**Dashboard**
- `GET /dashboard/stats` - Get dashboard statistics

## 🔐 Authentication

The application uses JWT tokens:
- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Tokens stored in localStorage on frontend

## 📊 Database Schema

### Key Tables
- `users` - User accounts and profiles
- `jobs` - Job listings from various sources
- `job_filters` - User's saved search filters
- `applications` - User's job applications
- `saved_jobs` - User's saved jobs
- `match_scores` - AI matching results
- `notifications` - User notifications
- `scraping_logs` - Job scraping history

## 🤖 AI Matching Engine

The matching engine calculates job fit based on:
- Text similarity between resume and job description
- Skills match percentage
- Experience level alignment
- Overall match score (0-100%)

**Match Score Calculation:**
- Text similarity: 40%
- Skills match: 60%

## 🔄 Background Tasks with Celery

### Tasks
- `scrape_jobs_task` - Scrape jobs from multiple sources
- `calculate_match_scores_task` - Calculate match scores
- `send_match_notification_task` - Send notifications
- `scheduled_scraping_task` - Periodic scraping

### Running Celery
```bash
# Worker
celery -A app.workers.celery_app worker --loglevel=info

# Beat (Scheduler)
celery -A app.workers.celery_app beat --loglevel=info
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 📦 Deployment

### Vercel (Frontend)
```bash
# Connect your GitHub repository to Vercel
# Set environment variables
# Auto-deploy on push to main
```

### Railway/Render (Backend)
```bash
# Connect your GitHub repository
# Set environment variables:
# - DATABASE_URL
# - REDIS_URL
# - SECRET_KEY
# - CORS_ORIGINS
# Deploy
```

## 🐳 Docker Deployment

```bash
# Build images
docker build -f Dockerfile.backend -t job-hunter-backend .

# Push to registry
docker push job-hunter-backend

# Deploy
docker-compose up -d
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```
DATABASE_URL=postgresql://user:password@localhost:5432/job_hunter
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000
ENV=development
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📈 Performance Optimization

- Database indexing on frequently queried fields
- Redis caching for frequently accessed data
- Query pagination
- Gzip compression
- Lazy loading of components
- Image optimization

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose logs db

# Verify connection string in .env
```

### Celery Not Working
```bash
# Check Redis is running
docker-compose logs redis

# Restart Celery worker
docker-compose restart celery_worker
```

### API CORS Errors
```bash
# Update CORS_ORIGINS in backend .env
# Restart backend
docker-compose restart backend
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Built with FastAPI, Next.js, and modern web technologies
- Inspired by best practices in job hunting and recruitment

---

**Made with ❤️ by the JobHunter Team**
