# ⚡ Quick Start - Vercel Deployment (10 Minutes)

Get your PR Bar Exam Prep Platform live on Vercel in 10 minutes!

## Prerequisites Checklist

- [ ] GitHub account with your code pushed
- [ ] Vercel account (free tier works)
- [ ] OpenAI API key
- [ ] Supabase project created

## 🚀 5-Step Deployment

### Step 1: Vercel Postgres (2 min)

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **Storage** → **Create Database** → **Postgres**
3. Name: `pr-bar-exam-db`, click **Create**
4. In **Query** tab, run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
5. Copy the **DATABASE_URL** from **.env.local** tab

### Step 2: Vercel Blob Storage (1 min)

1. In same project, **Storage** → **Create** → **Blob**
2. Name: `pr-bar-exam-files`, click **Create**
3. Copy the **BLOB_READ_WRITE_TOKEN**

### Step 3: Deploy Backend (3 min)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repo
3. **Root Directory**: `backend`
4. **Framework**: Other
5. Add Environment Variables:
   ```bash
   DATABASE_URL=<from Step 1>
   BLOB_READ_WRITE_TOKEN=<from Step 2>
   OPENAI_API_KEY=<your key>
   SUPABASE_URL=<your supabase url>
   SUPABASE_KEY=<your supabase anon key>
   SUPABASE_SERVICE_KEY=<your supabase service key>
   SECRET_KEY=<generate random 32+ char string>
   ALLOWED_ORIGINS=*
   VERCEL=1
   ```
6. Click **Deploy**
7. Copy your backend URL: `https://your-backend.vercel.app`

### Step 4: Initialize Database (2 min)

1. Go to your backend URL: `https://your-backend.vercel.app/docs`
2. Test `/health` endpoint - should return "healthy"
3. In Vercel Postgres **Query** tab, run the SQL from `docs/VERCEL_DEPLOYMENT.md` Step 1.3

### Step 5: Deploy Frontend (2 min)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import same GitHub repo (or add another project)
3. **Root Directory**: `frontend`
4. **Framework**: Next.js
5. Add Environment Variables:
   ```bash
   NEXT_PUBLIC_API_URL=<your backend URL from Step 3>
   NEXT_PUBLIC_SUPABASE_URL=<your supabase url>
   NEXT_PUBLIC_SUPABASE_ANON_KEY=<your supabase anon key>
   ```
6. Click **Deploy**
7. Visit your app: `https://your-app.vercel.app`

## ✅ Verify It Works

1. Visit your frontend URL
2. Navigate to **MCQ Practice**
3. Select a subject (e.g., "Familia")
4. Click **Generate Questions** (should work even without PDFs uploaded yet)
5. Navigate to **Essay Practice**
6. Select a subject and prompt
7. Write a test essay and submit

## 📤 Upload Study Materials

1. Have your PDF materials ready
2. Create an upload interface or use API directly
3. Upload PDFs for each of the 13 subjects
4. Materials will be processed automatically

## 🎯 You're Live!

Your platform is now accessible at:
- **Frontend**: `https://your-app.vercel.app`
- **API**: `https://your-backend.vercel.app`
- **Docs**: `https://your-backend.vercel.app/docs`

## 📖 Next Steps

- Upload study materials (PDFs)
- Test MCQ generation with real materials
- Test essay grading functionality
- Invite test users to try it out
- Monitor usage in Vercel dashboard

## 🆘 Issues?

See full deployment guide: `docs/VERCEL_DEPLOYMENT.md`

Common fixes:
- **CORS errors**: Add your frontend URL to `ALLOWED_ORIGINS`
- **Database errors**: Verify `DATABASE_URL` and pgvector extension
- **OpenAI errors**: Check API key and credits
- **Upload errors**: Verify `BLOB_READ_WRITE_TOKEN`

## 💰 Costs

**Free Tier Covers**:
- Vercel: 100GB bandwidth, 100GB-hrs compute
- Vercel Postgres: 256MB storage, 60 compute hours
- Vercel Blob: 1GB storage
- Supabase: 500MB database, 1GB file storage

**Expected Monthly Costs** (with moderate usage):
- OpenAI API: $10-50 (depends on usage)
- Vercel Pro (if needed): $20/month
- Total: ~$30-70/month

## 🎉 Success!

You now have a fully functional bar exam prep platform with:
- ✅ MCQ practice with AI-generated questions
- ✅ Essay grading with AI feedback
- ✅ Study material management
- ✅ Progress tracking
- ✅ Real-time community chat

Happy studying! 📚⚖️
