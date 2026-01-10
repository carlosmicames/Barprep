# 🚀 Complete Deployment Guide
## Puerto Rico Bar Exam Prep Platform

This guide will walk you through setting up and deploying the complete PR Bar Exam platform.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Database Setup (Supabase)](#database-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Docker Deployment](#docker-deployment)
6. [Initial Data Population](#initial-data-population)
7. [Testing the Platform](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **PostgreSQL 14+** (or Supabase account)
- **Docker & Docker Compose** (for containerized deployment)
- **Git** for version control

### Required API Keys
- **OpenAI API Key** (for GPT-3.5 and embeddings)
- **Supabase Project** (free tier works for MVP)

---

## Database Setup (Supabase)

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Note your project URL and anon key

### 2. Enable pgvector Extension
```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Setup Database Schema
The backend initialization script will create all tables automatically, but you can also run the schema manually if needed.

### 4. Enable Realtime for Chat
1. Go to Database > Replication in Supabase
2. Enable replication for `chat_messages` table
3. Set up realtime subscriptions

---

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Database
DATABASE_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres

# Security
SECRET_KEY=generate-a-strong-secret-key-here
```

### 5. Initialize Database
```bash
python scripts/init_db.py
```

### 6. Start Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

---

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment Variables
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### 4. Start Development Server
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

---

## Docker Deployment (Production)

### 1. Create Docker Compose File
Create `docker-compose.yml` in project root (already provided).

### 2. Build and Start Containers
```bash
docker-compose up -d
```

### 3. View Logs
```bash
docker-compose logs -f
```

### 4. Stop Containers
```bash
docker-compose down
```

---

## Initial Data Population

### 1. Upload Official Study Materials

#### Via API (Recommended)
```bash
curl -X POST "http://localhost:8000/materials/upload/1" \
  -F "file=@/path/to/civil-code-2020.pdf" \
  -F "subject=obligaciones" \
  -F "title=Código Civil de Puerto Rico 2020" \
  -F "is_official=true"
```

#### Via Web Interface
1. Go to Dashboard
2. Click "Upload Material"
3. Select subject, upload PDF
4. Mark as "Official Material"

### 2. Generate Initial MCQs

```bash
curl -X POST "http://localhost:8000/mcq/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "familia",
    "num_questions": 20,
    "difficulty": "medium"
  }'
```

### 3. Create Test User

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test Student"
  }'
```

---

## Testing the Platform

### Test MCQ Generation
1. Go to `/mcq`
2. Select subject: "Familia"
3. Generate 10 questions
4. Answer questions and verify feedback

### Test Essay Grading
1. Go to `/essays`
2. Select subject
3. Write essay response
4. Submit and verify AI grading with citations

### Test Community Chat
1. Go to `/community`
2. Select a subject room
3. Send messages
4. Verify real-time updates

### Test Progress Tracking
1. Complete several MCQs and essays
2. Go to `/progress`
3. Verify statistics are accurate

---

## Troubleshooting

### Backend Issues

#### Database Connection Fails
```bash
# Check DATABASE_URL format
postgresql://user:password@host:port/database

# Test connection
psql $DATABASE_URL
```

#### OpenAI API Errors
- Verify API key is valid
- Check API quota/billing
- Review error messages in logs

#### PDF Processing Fails
- Ensure PDF is not encrypted
- Check file size (< 10MB)
- Verify pypdf2/pdfplumber installation

### Frontend Issues

#### API Connection Fails
- Verify NEXT_PUBLIC_API_URL is correct
- Check CORS settings in backend
- Ensure backend is running

#### Supabase Realtime Not Working
- Verify Supabase project URL and key
- Check realtime is enabled for chat_messages
- Review browser console for errors

---

## Production Deployment Checklist

- [ ] Change all default secrets and keys
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure production database (not SQLite)
- [ ] Set up backup strategy
- [ ] Configure monitoring and logging
- [ ] Set DEBUG=False in environment
- [ ] Configure rate limiting
- [ ] Set up CDN for static files
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Enable database connection pooling
- [ ] Set up scheduled tasks (backups, cleanup)
- [ ] Configure firewall rules
- [ ] Set up load balancing (if needed)

---

## Maintenance

### Regular Tasks
- **Daily**: Monitor error logs
- **Weekly**: Review user feedback
- **Monthly**: Update dependencies
- **Quarterly**: Review and update study materials

### Updating Study Materials
1. Upload new PDFs via API or UI
2. System automatically processes and creates embeddings
3. Generate new MCQs from updated materials

### Database Backups
```bash
# Backup database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore database
psql $DATABASE_URL < backup_20240115.sql
```

---

## Support & Documentation

- **API Documentation**: http://localhost:8000/docs
- **Frontend Pages**:
  - Home: `/`
  - MCQ Practice: `/mcq`
  - Essays: `/essays`
  - Community: `/community`
  - Progress: `/progress`

## Performance Optimization

### Backend
- Enable Redis caching for embeddings
- Use Celery for async PDF processing
- Implement request rate limiting
- Add database indexing

### Frontend
- Enable Next.js image optimization
- Implement code splitting
- Add service worker for offline support
- Use React.memo for expensive components

---

**Happy Studying! 📚⚖️**
