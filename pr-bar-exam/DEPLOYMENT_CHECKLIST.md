# ✅ Vercel Deployment Checklist

Use this checklist to ensure your PR Bar Exam Prep Platform is deployed correctly and ready for next week's launch.

## 📋 Pre-Deployment Checklist

### Prerequisites
- [ ] GitHub account created
- [ ] Code pushed to GitHub repository
- [ ] Vercel account created (free tier OK)
- [ ] OpenAI API key obtained
- [ ] Supabase project created
- [ ] Study material PDFs ready (all 13 subjects)

## 🗄️ Database Setup

### Vercel Postgres
- [ ] Created Vercel Postgres database
- [ ] Named: `pr-bar-exam-db`
- [ ] Enabled `pgvector` extension
- [ ] Copied `DATABASE_URL` connection string
- [ ] Ran database schema SQL
- [ ] Verified tables created (users, study_materials, document_chunks, etc.)
- [ ] Inserted default chat rooms
- [ ] Created test user

### Verify Database
Run these queries in Vercel Postgres Query tab:
```sql
-- Should show 13 tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Should show pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Should show 13 chat rooms
SELECT COUNT(*) FROM chat_rooms;

-- Should show at least 1 user
SELECT COUNT(*) FROM users;
```

## 📦 Storage Setup

### Vercel Blob Storage
- [ ] Created Vercel Blob Storage
- [ ] Named: `pr-bar-exam-files`
- [ ] Copied `BLOB_READ_WRITE_TOKEN`
- [ ] Token added to backend environment variables

## 🔧 Backend Deployment

### Deploy Backend
- [ ] Created new Vercel project
- [ ] Imported from GitHub
- [ ] Set Root Directory: `backend`
- [ ] Selected Framework: Other
- [ ] Deployment successful
- [ ] Copied backend URL: `https://_________.vercel.app`

### Backend Environment Variables
Verify all are set in Vercel project settings:
- [ ] `DATABASE_URL` (from Vercel Postgres)
- [ ] `BLOB_READ_WRITE_TOKEN` (from Vercel Blob)
- [ ] `OPENAI_API_KEY`
- [ ] `OPENAI_MODEL=gpt-3.5-turbo`
- [ ] `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`
- [ ] `SUPABASE_SERVICE_KEY`
- [ ] `SECRET_KEY` (32+ random characters)
- [ ] `ALLOWED_ORIGINS` (your frontend URL or *)
- [ ] `VERCEL=1`
- [ ] `APP_NAME=PR Bar Exam Prep`
- [ ] `APP_VERSION=1.0.0`
- [ ] `DEBUG=False`
- [ ] `ENVIRONMENT=production`
- [ ] `CHUNK_SIZE=1000`
- [ ] `CHUNK_OVERLAP=200`
- [ ] `TOP_K_RESULTS=5`
- [ ] `SIMILARITY_THRESHOLD=0.7`
- [ ] `MAX_UPLOAD_SIZE=10485760`
- [ ] `ALLOWED_EXTENSIONS=.pdf,.docx`

### Test Backend
- [ ] Visit `https://your-backend.vercel.app/docs`
- [ ] Swagger docs load correctly
- [ ] Test `/health` endpoint (should return `{"status": "healthy"}`)
- [ ] Test `/subjects` endpoint (should return 13 subjects)
- [ ] No errors in Vercel function logs

## 🎨 Frontend Deployment

### Deploy Frontend
- [ ] Created new Vercel project (or second project)
- [ ] Imported from GitHub
- [ ] Set Root Directory: `frontend`
- [ ] Selected Framework: Next.js
- [ ] Deployment successful
- [ ] Copied frontend URL: `https://_________.vercel.app`

### Frontend Environment Variables
Verify all are set:
- [ ] `NEXT_PUBLIC_API_URL` (backend URL from above)
- [ ] `NEXT_PUBLIC_SUPABASE_URL`
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### Test Frontend
- [ ] Visit your frontend URL
- [ ] Homepage loads without errors
- [ ] Navigation bar displays correctly
- [ ] All navigation links work:
  - [ ] Home (/)
  - [ ] MCQ Practice (/mcq)
  - [ ] Essays (/essay)
  - [ ] Community (/community)
  - [ ] Progress (/progress)

## 🧪 Integration Testing

### MCQ Practice
- [ ] Navigate to MCQ Practice page
- [ ] Select a subject (e.g., "Familia")
- [ ] Click "Generate Questions" button
- [ ] Questions generate successfully (or shows "No questions available")
- [ ] Can select an answer
- [ ] Can submit answer
- [ ] Receives feedback (correct/incorrect)
- [ ] Stats update (attempted, correct, accuracy)

### Essay Practice
- [ ] Navigate to Essay Practice page
- [ ] Subject selector displays 13 subjects
- [ ] Select a subject
- [ ] Essay prompts load (2 per subject)
- [ ] Select a prompt
- [ ] Prompt displays in highlighted box
- [ ] Can type in essay textarea
- [ ] Word count updates
- [ ] Submit button works
- [ ] Receives grade with:
  - [ ] Overall score
  - [ ] Detailed feedback
  - [ ] Citations (if materials uploaded)
- [ ] "Write Another" button resets form
- [ ] Previous essays show in sidebar

### Study Materials Upload
- [ ] API endpoint `/materials/upload/{user_id}` accessible
- [ ] Can upload a test PDF
- [ ] File uploads to Vercel Blob Storage
- [ ] Database record created
- [ ] PDF processing starts (check logs)
- [ ] Document chunks created in database

## 📤 Study Materials Preparation

### Upload Materials for All Subjects

#### Subject 1: Familia (Family Law)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 2: Sucesiones (Succession)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 3: Reales (Property Rights)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 4: Hipoteca (Mortgage)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 5: Obligaciones (Obligations & Contracts)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 6: Ética (Ethics)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 7: Constitucional (Constitutional Law)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 8: Administrativo (Administrative Law)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 9: Daños (Damages)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 10: Penal (Criminal Law)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 11: Proc_Penal (Criminal Procedure)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 12: Evidencia (Evidence)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

#### Subject 13: Proc_Civil (Civil Procedure)
- [ ] PDF prepared
- [ ] Uploaded via API
- [ ] Processing completed
- [ ] Chunks created

## 🎯 Feature Verification (Post-Upload)

### MCQ with Real Materials
- [ ] Generate MCQs for a subject with uploaded materials
- [ ] Questions reference actual content from PDFs
- [ ] Explanations cite sources correctly
- [ ] Difficulty levels vary
- [ ] All 4 options are plausible

### Essay Grading with Real Materials
- [ ] Submit an essay for a subject with uploaded materials
- [ ] Grading completes within 30 seconds
- [ ] Feedback references specific legal concepts
- [ ] Citations point to actual PDF sources
- [ ] Score breakdown is detailed
- [ ] Legal analysis score provided
- [ ] Writing quality score provided
- [ ] Citation accuracy score provided

## 📊 Performance & Monitoring

### Vercel Dashboard
- [ ] Check function execution times (should be < 30s for most)
- [ ] Review error logs (should be minimal)
- [ ] Monitor bandwidth usage
- [ ] Check database query performance

### OpenAI Usage
- [ ] Verify API calls are working
- [ ] Monitor token usage
- [ ] Set spending limits if needed

### Database Health
- [ ] Check storage usage in Vercel Postgres
- [ ] Verify vector indexes are working
- [ ] Review connection pool usage

## 🚀 Launch Preparation

### Documentation
- [ ] `README.md` updated with Vercel deployment info
- [ ] User guide created (if needed)
- [ ] API documentation accessible at `/docs`

### Security
- [ ] CORS configured correctly
- [ ] API keys secured in environment variables
- [ ] No sensitive data in git repository
- [ ] Database access restricted

### User Experience
- [ ] Test on desktop browser
- [ ] Test on mobile browser
- [ ] Navigation is intuitive
- [ ] Load times are acceptable (< 3s)
- [ ] Error messages are user-friendly

### Final Tests
- [ ] Complete MCQ workflow (select → generate → answer → submit)
- [ ] Complete Essay workflow (select → write → submit → review)
- [ ] Complete Upload workflow (select file → upload → process)
- [ ] Check progress tracking updates correctly

## ✅ Pre-Launch Checklist

### 24 Hours Before Launch
- [ ] All study materials uploaded and processed
- [ ] Test with 2-3 beta users
- [ ] Collect feedback and fix critical issues
- [ ] Verify all 13 subjects work correctly
- [ ] Backup database
- [ ] Monitor Vercel function logs for errors

### Launch Day
- [ ] Announce to students
- [ ] Share frontend URL
- [ ] Provide user guide/instructions
- [ ] Monitor for issues in real-time
- [ ] Be ready to respond to user questions

### Post-Launch (First Week)
- [ ] Daily log review
- [ ] User feedback collection
- [ ] Performance optimization as needed
- [ ] Bug fixes for reported issues

## 🎉 Success Metrics

Your deployment is successful when:
- ✅ 95%+ uptime
- ✅ MCQ generation < 10 seconds
- ✅ Essay grading < 30 seconds
- ✅ All 13 subjects have study materials
- ✅ Users can complete full workflows
- ✅ No critical errors in logs
- ✅ OpenAI API costs within budget

## 📞 Support Contacts

- Vercel Support: [vercel.com/support](https://vercel.com/support)
- OpenAI Support: [help.openai.com](https://help.openai.com)
- Supabase Support: [supabase.com/support](https://supabase.com/support)

## 📊 Progress Tracking

**Overall Progress**: _____ / 100 items completed

**Deployment Phase**:
- Pre-Deployment: _____ / 6
- Database Setup: _____ / 8
- Storage Setup: _____ / 4
- Backend Deployment: _____ / 22
- Frontend Deployment: _____ / 12
- Integration Testing: _____ / 23
- Materials Upload: _____ / 52
- Feature Verification: _____ / 10
- Performance: _____ / 9
- Launch Prep: _____ / 16

---

**Target Completion Date**: [Next Week]
**Launch Date**: [Next Week + 1 day for testing]

Good luck with your deployment! 🚀📚⚖️
