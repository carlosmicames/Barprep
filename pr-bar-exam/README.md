# Puerto Rico Bar Exam Prep Platform

A comprehensive AI-powered study platform for Puerto Rico bar exam candidates, featuring MCQ practice, essay grading with RAG-based feedback, and real-time community chat.

## 🎯 Features

### Phase 1 (MVP)
- ✅ **MCQ Practice System**: Auto-generated multiple-choice questions from study materials
- ✅ **Essay Grading**: AI-powered essay evaluation with citation-backed feedback
- ✅ **Community Chat**: Real-time topic-based discussion rooms
- ✅ **Progress Tracking**: Comprehensive analytics and performance metrics

### Subjects Covered (13 Total)
1. Derecho de Familia (Family Law)
2. Sucesiones (Succession)
3. Derechos Reales (Property Rights)
4. Hipoteca (Mortgage)
5. Obligaciones & Contratos (Obligations & Contracts)
6. Ética (Ethics)
7. Constitucional (Constitutional Law)
8. Administrativo (Administrative Law)
9. Daños y Perjuicios (Damages)
10. Penal (Criminal Law)
11. Procedimiento Penal (Criminal Procedure)
12. Evidencia (Evidence)
13. Procedimiento Civil (Civil Procedure)

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Next.js 15     │◄────►│   FastAPI        │◄────►│   Supabase      │
│  Frontend       │      │   Backend        │      │   PostgreSQL    │
│  (Tailwind)     │      │   (OpenAI RAG)   │      │   + pgvector    │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.11+
- Docker & Docker Compose (for self-hosting)
- Supabase account
- OpenAI API key

### Installation

1. **Clone and setup**
```bash
git clone <repository-url>
cd pr-bar-exam
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

3. **Frontend Setup**
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your API URLs
```

4. **Database Setup**
```bash
# Run Supabase migrations
cd backend
python scripts/init_db.py
```

5. **Run Development Servers**

Terminal 1 (Backend):
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Access the application at `http://localhost:3000`

## 🐳 Docker Deployment (Self-Hosted)

```bash
docker-compose up -d
```

The application will be available at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 📚 Documentation

- [Backend API Documentation](./docs/api.md)
- [Frontend Components Guide](./docs/frontend.md)
- [RAG System Architecture](./docs/rag.md)
- [Database Schema](./docs/schema.md)
- [Deployment Guide](./docs/deployment.md)

## 🔑 Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://....supabase.co
SUPABASE_KEY=eyJ...
DATABASE_URL=postgresql://...
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://....supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📦 Project Structure

```
pr-bar-exam/
├── frontend/               # Next.js 15 application
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities and configs
│   │   └── styles/        # Global styles
│   └── public/            # Static assets
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core configs
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── main.py       # App entry point
│   └── scripts/          # Utility scripts
├── docs/                  # Documentation
└── docker-compose.yml     # Docker orchestration
```

## 🤝 Contributing

This is an MVP for Puerto Rico bar exam students. Contributions welcome!

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues or questions, please open a GitHub issue or contact support.

---

Built with ❤️ for Puerto Rico bar exam candidates
