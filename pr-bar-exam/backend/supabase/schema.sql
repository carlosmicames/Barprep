-- ==============================================
-- PR Bar Exam - Supabase Database Schema
-- Run this in Supabase SQL Editor
-- ==============================================

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- ==============================================
-- TABLES
-- ==============================================

-- BLL Rules (Black Letter Law from Shorter PDFs)
CREATE TABLE IF NOT EXISTS bll_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    article_number TEXT,
    description TEXT NOT NULL,
    source_pdf TEXT,
    page_number INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document Chunks (for RAG embeddings)
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    page_number INTEGER,
    source_file TEXT,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Study Materials (PDFs)
CREATE TABLE IF NOT EXISTS study_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject TEXT NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    is_shorter BOOLEAN DEFAULT FALSE,
    is_processed BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quiz Sessions
CREATE TABLE IF NOT EXISTS quiz_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_count INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Quiz Questions (generated per session)
CREATE TABLE IF NOT EXISTS quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    explanation TEXT,
    bll_rule_id UUID REFERENCES bll_rules(id),
    difficulty TEXT DEFAULT 'medium',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quiz Responses
CREATE TABLE IF NOT EXISTS quiz_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    question_id UUID REFERENCES quiz_questions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    selected_answer CHAR(1) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    answered_at TIMESTAMPTZ DEFAULT NOW()
);

-- Weekly Progress
CREATE TABLE IF NOT EXISTS weekly_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    subject TEXT,
    mcqs_attempted INTEGER DEFAULT 0,
    mcqs_correct INTEGER DEFAULT 0,
    accuracy_percentage NUMERIC(5,2) DEFAULT 0,
    UNIQUE(user_id, week_start, subject)
);

-- Essays
CREATE TABLE IF NOT EXISTS essays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    prompt TEXT NOT NULL,
    content TEXT NOT NULL,
    submitted_at TIMESTAMPTZ DEFAULT NOW()
);

-- Essay Grades
CREATE TABLE IF NOT EXISTS essay_grades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    essay_id UUID UNIQUE REFERENCES essays(id) ON DELETE CASCADE,
    overall_score NUMERIC(5,2) NOT NULL,
    legal_analysis_score NUMERIC(5,2),
    writing_quality_score NUMERIC(5,2),
    citation_accuracy_score NUMERIC(5,2),
    feedback TEXT NOT NULL,
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    suggestions JSONB DEFAULT '[]',
    citations JSONB DEFAULT '[]',
    graded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Rooms (one per subject)
CREATE TABLE IF NOT EXISTS chat_rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES chat_rooms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================
-- INDEXES
-- ==============================================

-- Vector similarity search index
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
ON document_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_bll_rules_subject ON bll_rules(subject);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_user ON quiz_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_subject ON quiz_sessions(subject);
CREATE INDEX IF NOT EXISTS idx_quiz_responses_user ON quiz_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_weekly_progress_user ON weekly_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_essays_user ON essays(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_room ON chat_messages(room_id);

-- ==============================================
-- FUNCTIONS
-- ==============================================

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding vector(1536),
    match_subject TEXT,
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id UUID,
    chunk_text TEXT,
    page_number INTEGER,
    source_file TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.chunk_text,
        dc.page_number,
        dc.source_file,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM document_chunks dc
    WHERE dc.subject = match_subject
    AND 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Increment correct count function
CREATE OR REPLACE FUNCTION increment_correct_count(session_id_input UUID)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE quiz_sessions
    SET correct_count = correct_count + 1
    WHERE id = session_id_input;
END;
$$;

-- ==============================================
-- ROW LEVEL SECURITY (RLS)
-- ==============================================

-- Enable RLS on user-specific tables
ALTER TABLE quiz_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE essays ENABLE ROW LEVEL SECURITY;
ALTER TABLE essay_grades ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Quiz Sessions: Users can only see their own
CREATE POLICY "Users can view own quiz sessions"
ON quiz_sessions FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own quiz sessions"
ON quiz_sessions FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own quiz sessions"
ON quiz_sessions FOR UPDATE
TO authenticated
USING (auth.uid() = user_id);

-- Quiz Responses: Users can only see their own
CREATE POLICY "Users can view own quiz responses"
ON quiz_responses FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own quiz responses"
ON quiz_responses FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Weekly Progress: Users can only see their own
CREATE POLICY "Users can view own progress"
ON weekly_progress FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own progress"
ON weekly_progress FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own progress"
ON weekly_progress FOR UPDATE
TO authenticated
USING (auth.uid() = user_id);

-- Essays: Users can only see their own
CREATE POLICY "Users can view own essays"
ON essays FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own essays"
ON essays FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Essay Grades: Users can view grades for their essays
CREATE POLICY "Users can view own essay grades"
ON essay_grades FOR SELECT
TO authenticated
USING (
    essay_id IN (
        SELECT id FROM essays WHERE user_id = auth.uid()
    )
);

-- Chat Messages: All authenticated users can view and post
CREATE POLICY "Authenticated users can view chat messages"
ON chat_messages FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Authenticated users can insert chat messages"
ON chat_messages FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- ==============================================
-- PUBLIC ACCESS (for service role operations)
-- ==============================================

-- BLL Rules: Read-only for authenticated, full access for service role
CREATE POLICY "Authenticated users can read BLL rules"
ON bll_rules FOR SELECT
TO authenticated
USING (true);

-- Document Chunks: Read access for authenticated
CREATE POLICY "Authenticated users can read document chunks"
ON document_chunks FOR SELECT
TO authenticated
USING (true);

-- Study Materials: Read access for authenticated
CREATE POLICY "Authenticated users can read study materials"
ON study_materials FOR SELECT
TO authenticated
USING (true);

-- Chat Rooms: Read access for all authenticated
CREATE POLICY "Authenticated users can read chat rooms"
ON chat_rooms FOR SELECT
TO authenticated
USING (true);

-- Quiz Questions: Read access for authenticated (needed for quiz flow)
ALTER TABLE quiz_questions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can read quiz questions"
ON quiz_questions FOR SELECT
TO authenticated
USING (true);

-- ==============================================
-- STORAGE BUCKET
-- ==============================================

-- Create storage bucket for study materials
INSERT INTO storage.buckets (id, name, public)
VALUES ('study-materials', 'study-materials', false)
ON CONFLICT (id) DO NOTHING;

-- Storage policies
CREATE POLICY "Authenticated users can read study materials"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'study-materials');

-- ==============================================
-- SEED DATA: Create chat rooms for all subjects
-- ==============================================

INSERT INTO chat_rooms (subject, name, description) VALUES
    ('familia', 'Derecho de Familia', 'Discuss family law topics'),
    ('sucesiones', 'Sucesiones', 'Discuss succession and inheritance law'),
    ('reales', 'Derechos Reales', 'Discuss property rights'),
    ('hipoteca', 'Hipoteca', 'Discuss mortgage law'),
    ('obligaciones', 'Obligaciones y Contratos', 'Discuss contracts and obligations'),
    ('etica', 'Ética Profesional', 'Discuss legal ethics'),
    ('constitucional', 'Derecho Constitucional', 'Discuss constitutional law'),
    ('administrativo', 'Derecho Administrativo', 'Discuss administrative law'),
    ('danos', 'Daños y Perjuicios', 'Discuss torts and damages'),
    ('penal', 'Derecho Penal', 'Discuss criminal law'),
    ('proc_penal', 'Procedimiento Penal', 'Discuss criminal procedure'),
    ('evidencia', 'Evidencia', 'Discuss evidence law'),
    ('proc_civil', 'Procedimiento Civil', 'Discuss civil procedure')
ON CONFLICT (subject) DO NOTHING;