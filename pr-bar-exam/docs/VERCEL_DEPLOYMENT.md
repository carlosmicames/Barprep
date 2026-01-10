# 🚀 Vercel Deployment Guide - PR Bar Exam Prep Platform

This guide provides step-by-step instructions to deploy your Puerto Rico Bar Exam Prep Platform to Vercel with 95% accuracy.

## 📋 Prerequisites

Before you begin, ensure you have:

- [ ] Vercel account (sign up at [vercel.com](https://vercel.com))
- [ ] OpenAI API key (from [platform.openai.com](https://platform.openai.com))
- [ ] Supabase account and project (from [supabase.com](https://supabase.com))
- [ ] GitHub repository with your code
- [ ] Your study material PDFs ready to upload

## 🗄️ Step 1: Set Up Vercel Postgres Database

### 1.1 Create Vercel Postgres Database

1. Go to your Vercel dashboard
2. Navigate to **Storage** tab
3. Click **Create Database**
4. Select **Postgres**
5. Choose a name: `pr-bar-exam-db`
6. Select your region (closest to your users)
7. Click **Create**

### 1.2 Enable pgvector Extension

Vercel Postgres supports pgvector, but you need to enable it:

1. In your database dashboard, go to the **Query** tab
2. Run this SQL command:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Verify it's installed:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 1.3 Initialize Database Schema

1. Go to the **Query** tab in your Vercel Postgres dashboard
2. Copy and run the SQL from `backend/scripts/init_db.py` or create tables manually:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Study Materials table
CREATE TABLE study_materials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    subject VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(20),
    is_official BOOLEAN DEFAULT FALSE,
    processed BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document Chunks table (for RAG)
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES study_materials(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector index for similarity search
CREATE INDEX document_chunks_embedding_idx ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- MCQ Questions table
CREATE TABLE mcq_questions (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    explanation TEXT,
    difficulty VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MCQ Responses table
CREATE TABLE mcq_responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    question_id INTEGER REFERENCES mcq_questions(id),
    selected_answer CHAR(1) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_spent_seconds INTEGER,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Essays table
CREATE TABLE essays (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    subject VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,
    content TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Essay Grades table
CREATE TABLE essay_grades (
    id SERIAL PRIMARY KEY,
    essay_id INTEGER REFERENCES essays(id) ON DELETE CASCADE,
    overall_score FLOAT NOT NULL,
    legal_analysis_score FLOAT,
    writing_quality_score FLOAT,
    citation_accuracy_score FLOAT,
    feedback TEXT NOT NULL,
    point_breakdown JSONB,
    citations JSONB,
    graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Progress table
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    subject VARCHAR(50) NOT NULL,
    total_mcqs_attempted INTEGER DEFAULT 0,
    total_mcqs_correct INTEGER DEFAULT 0,
    total_essays_submitted INTEGER DEFAULT 0,
    average_essay_score FLOAT,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, subject)
);

-- Chat Rooms table
CREATE TABLE chat_rooms (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat Messages table
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES chat_rooms(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default chat rooms for all subjects
INSERT INTO chat_rooms (subject, name, description) VALUES
('familia', 'Derecho de Familia', 'Discuss family law topics'),
('sucesiones', 'Sucesiones', 'Discuss succession law'),
('reales', 'Derechos Reales', 'Discuss property rights'),
('hipoteca', 'Hipoteca', 'Discuss mortgage law'),
('obligaciones', 'Obligaciones & Contratos', 'Discuss obligations and contracts'),
('etica', 'Ética', 'Discuss legal ethics'),
('constitucional', 'Derecho Constitucional', 'Discuss constitutional law'),
('administrativo', 'Derecho Administrativo', 'Discuss administrative law'),
('danos', 'Daños y Perjuicios', 'Discuss damages and torts'),
('penal', 'Derecho Penal', 'Discuss criminal law'),
('proc_penal', 'Procedimiento Penal', 'Discuss criminal procedure'),
('evidencia', 'Evidencia', 'Discuss evidence law'),
('proc_civil', 'Procedimiento Civil', 'Discuss civil procedure');

-- Create a default test user
INSERT INTO users (email, username, full_name) VALUES
('test@example.com', 'testuser', 'Test User');
```

## 🔑 Step 2: Set Up Vercel Blob Storage

1. In your Vercel project dashboard, go to **Storage**
2. Click **Create Database**
3. Select **Blob**
4. Name it `pr-bar-exam-files`
5. Click **Create**
6. Copy the `BLOB_READ_WRITE_TOKEN` - you'll need this later

## 🚀 Step 3: Deploy Backend to Vercel

### 3.1 Create Backend Project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Output Directory**: Leave empty
   - **Install Command**: Leave default

### 3.2 Configure Backend Environment Variables

In your Vercel project settings, go to **Settings** → **Environment Variables** and add:

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...

# Database (from Vercel Postgres connection string)
DATABASE_URL=postgres://default:xxx@xxx.postgres.vercel-storage.com:5432/verceldb

# Security
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (your frontend URL)
ALLOWED_ORIGINS=https://your-frontend.vercel.app

# App Config
APP_NAME=PR Bar Exam Prep
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# RAG Config
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7

# File Upload
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=.pdf,.docx

# Vercel Blob Storage
BLOB_READ_WRITE_TOKEN=vercel_blob_...

# Vercel Detection
VERCEL=1
```

### 3.3 Deploy Backend

1. Click **Deploy**
2. Wait for deployment to complete
3. Copy your backend URL (e.g., `https://your-backend.vercel.app`)
4. Test the API: Visit `https://your-backend.vercel.app/docs`

## 🎨 Step 4: Deploy Frontend to Vercel

### 4.1 Create Frontend Project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository (or create a new project)
3. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

### 4.2 Configure Frontend Environment Variables

In your Vercel project settings, add:

```bash
# Backend API URL (from Step 3.3)
NEXT_PUBLIC_API_URL=https://your-backend.vercel.app

# Supabase (for real-time chat)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

### 4.3 Deploy Frontend

1. Click **Deploy**
2. Wait for deployment to complete
3. Visit your frontend URL (e.g., `https://your-app.vercel.app`)

## ✅ Step 5: Verify Deployment

### 5.1 Test Backend API

Visit `https://your-backend.vercel.app/docs` and verify:
- [ ] Swagger docs load correctly
- [ ] `/health` endpoint returns healthy status
- [ ] `/subjects` endpoint returns all 13 subjects

### 5.2 Test Frontend

Visit your frontend URL and verify:
- [ ] Homepage loads correctly
- [ ] Navigation works
- [ ] MCQ page loads
- [ ] Essay page loads

### 5.3 Test Full Integration

1. **Create a test user** (if not already created in database)
2. **Upload a PDF**:
   - Go to Materials section
   - Upload a test PDF
   - Verify it uploads to Vercel Blob Storage
3. **Generate MCQ Questions**:
   - Go to MCQ Practice
   - Select a subject
   - Click "Generate Questions"
   - Verify questions appear
4. **Submit an Essay**:
   - Go to Essay Practice
   - Select a subject and prompt
   - Write a test essay
   - Submit and verify you receive a grade

## 📤 Step 6: Upload Study Materials

Now that everything is working, upload your Puerto Rico bar exam PDFs:

1. Log into your application
2. Navigate to the Materials/Upload section
3. For each of the 13 subjects, upload official materials:
   - Familia (Family Law)
   - Sucesiones (Succession)
   - Reales (Property Rights)
   - Hipoteca (Mortgage)
   - Obligaciones (Obligations & Contracts)
   - Ética (Ethics)
   - Constitucional (Constitutional Law)
   - Administrativo (Administrative Law)
   - Daños (Damages)
   - Penal (Criminal Law)
   - Proc_Penal (Criminal Procedure)
   - Evidencia (Evidence)
   - Proc_Civil (Civil Procedure)

## 🔧 Troubleshooting

### Issue: Backend API not accessible

**Solution**:
- Check that CORS is configured correctly with your frontend URL
- Verify all environment variables are set
- Check Vercel function logs for errors

### Issue: Database connection fails

**Solution**:
- Verify DATABASE_URL is correct
- Check that pgvector extension is installed
- Ensure database tables are created

### Issue: PDF upload fails

**Solution**:
- Verify BLOB_READ_WRITE_TOKEN is set correctly
- Check that VERCEL=1 environment variable is set
- Verify file size is under MAX_UPLOAD_SIZE

### Issue: MCQ generation fails

**Solution**:
- Verify OPENAI_API_KEY is correct and has credits
- Check that PDF was processed and chunks were created
- Look at backend logs for specific errors

### Issue: Essay grading not working

**Solution**:
- Verify study materials are uploaded and processed
- Check that embeddings were created successfully
- Ensure RAG service can access document chunks

## 📊 Monitoring & Maintenance

### Monitor Usage

1. **Vercel Dashboard**:
   - Check function execution times
   - Monitor bandwidth usage
   - Review error logs

2. **OpenAI Dashboard**:
   - Monitor API usage and costs
   - Set spending limits if needed

3. **Vercel Postgres**:
   - Monitor database size
   - Check query performance
   - Review connection usage

### Regular Maintenance

- **Weekly**: Review error logs and fix issues
- **Monthly**: Update study materials as laws change
- **Quarterly**: Review and optimize database queries
- **As Needed**: Scale up Vercel plan if traffic increases

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ Frontend loads without errors
- ✅ Backend API is accessible at `/docs`
- ✅ Database queries work correctly
- ✅ PDF uploads work via Vercel Blob Storage
- ✅ MCQ generation produces valid questions
- ✅ Essay grading returns detailed feedback
- ✅ Chat functionality works in real-time
- ✅ All 13 subjects have study materials
- ✅ Progress tracking updates correctly

## 🚀 Next Steps

After successful deployment:

1. **Test with real users**: Have 2-3 law students test the platform
2. **Gather feedback**: Collect user experience feedback
3. **Optimize**: Based on usage patterns, optimize slow queries
4. **Scale**: Increase Vercel plan if needed for more traffic
5. **Monitor**: Set up alerts for errors and downtime

## 📞 Support

If you encounter issues:

1. Check Vercel function logs: **Project** → **Deployments** → **Functions**
2. Review this guide's troubleshooting section
3. Check backend logs for specific error messages
4. Test API endpoints directly using `/docs` interface

## 🎉 Congratulations!

Your PR Bar Exam Prep Platform is now live on Vercel! Students can now access MCQ practice and essay grading powered by AI with study materials from official Puerto Rico legal sources.

**Your deployment URLs**:
- Backend API: `https://your-backend.vercel.app`
- Frontend App: `https://your-app.vercel.app`
- API Documentation: `https://your-backend.vercel.app/docs`

Good luck with your bar exam preparation platform! 📚⚖️
