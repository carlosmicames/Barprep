'use client';

import { useState, useEffect } from 'react';
import { ChevronRight, CheckCircle, XCircle, BookOpen, RefreshCw } from 'lucide-react';
import { api, SUBJECT_NAMES } from '@/lib/utils';

interface MCQOption {
  label: string;
  text: string;
}

interface MCQuestion {
  id: number;
  subject: string;
  question_text: string;
  options: MCQOption[];
  difficulty: string;
}

interface MCQResult {
  is_correct: boolean;
  correct_answer: string;
  explanation: string | null;
  selected_answer: string;
}

export default function MCQPage() {
  const [selectedSubject, setSelectedSubject] = useState<string>('familia');
  const [questions, setQuestions] = useState<MCQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [result, setResult] = useState<MCQResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ attempted: 0, correct: 0, accuracy: 0 });
  const [showResults, setShowResults] = useState(false);
  const userId = 1; // In production, get from auth context

  useEffect(() => {
    loadQuestions();
    loadStats();
  }, [selectedSubject]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const response = await api.mcq.getBySubject(selectedSubject, 20);
      setQuestions(response.data);
      setCurrentIndex(0);
      setSelectedAnswer(null);
      setResult(null);
      setShowResults(false);
    } catch (error) {
      console.error('Error loading questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.mcq.getStats(userId, selectedSubject);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleSubmit = async () => {
    if (!selectedAnswer || !questions[currentIndex]) return;

    setLoading(true);
    try {
      const response = await api.mcq.submit(userId, {
        question_id: questions[currentIndex].id,
        selected_answer: selectedAnswer,
      });
      setResult(response.data);
      setShowResults(true);
      loadStats();
    } catch (error) {
      console.error('Error submitting answer:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedAnswer(null);
      setResult(null);
      setShowResults(false);
    } else {
      loadQuestions();
    }
  };

  const generateNewQuestions = async () => {
    setLoading(true);
    try {
      await api.mcq.generate({
        subject: selectedSubject,
        num_questions: 10,
        difficulty: 'medium',
      });
      await loadQuestions();
    } catch (error) {
      console.error('Error generating questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentQuestion = questions[currentIndex];

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 animate-slide-up">
          <h1 className="text-4xl font-serif font-bold text-navy-900 mb-4">
            MCQ Practice
          </h1>
          <p className="text-lg text-slate-600">
            Test your knowledge with AI-generated questions from official materials
          </p>
        </div>

        {/* Subject Selector */}
        <div className="card mb-8 animate-slide-up animation-delay-200">
          <label className="block text-sm font-medium text-navy-900 mb-3">
            Select Subject
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(SUBJECT_NAMES).slice(0, 6).map(([code, name]) => (
              <button
                key={code}
                onClick={() => setSelectedSubject(code)}
                className={`p-3 rounded-lg font-medium transition-all ${
                  selectedSubject === code
                    ? 'bg-navy-700 text-white shadow-md'
                    : 'bg-slate-100 text-navy-700 hover:bg-slate-200'
                }`}
              >
                {name}
              </button>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8 animate-slide-up animation-delay-400">
          <div className="card text-center">
            <div className="text-3xl font-bold text-navy-700">{stats.attempted}</div>
            <div className="text-sm text-slate-600">Attempted</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-green-600">{stats.correct}</div>
            <div className="text-sm text-slate-600">Correct</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-amber-600">{stats.accuracy}%</div>
            <div className="text-sm text-slate-600">Accuracy</div>
          </div>
        </div>

        {/* Question Card */}
        {loading ? (
          <div className="card text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-navy-700 mx-auto mb-4"></div>
            <p className="text-slate-600">Loading questions...</p>
          </div>
        ) : questions.length === 0 ? (
          <div className="card text-center py-12 space-y-4">
            <BookOpen className="w-16 h-16 text-slate-400 mx-auto" />
            <h3 className="text-xl font-semibold text-navy-900">No Questions Available</h3>
            <p className="text-slate-600">Generate new questions to get started!</p>
            <button onClick={generateNewQuestions} className="btn-amber mx-auto">
              <RefreshCw className="w-5 h-5 mr-2 inline" />
              Generate Questions
            </button>
          </div>
        ) : currentQuestion ? (
          <div className="card animate-slide-up">
            {/* Progress */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-slate-600 mb-2">
                <span>Question {currentIndex + 1} of {questions.length}</span>
                <span className="badge-primary">{currentQuestion.difficulty}</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div
                  className="bg-navy-700 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Question */}
            <h3 className="text-xl font-serif font-semibold text-navy-900 mb-6">
              {currentQuestion.question_text}
            </h3>

            {/* Options */}
            <div className="space-y-3 mb-6">
              {currentQuestion.options.map((option) => (
                <button
                  key={option.label}
                  onClick={() => !showResults && setSelectedAnswer(option.label)}
                  disabled={showResults}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    selectedAnswer === option.label
                      ? 'border-navy-700 bg-navy-50'
                      : 'border-slate-300 hover:border-navy-300'
                  } ${
                    showResults && result
                      ? option.label === result.correct_answer
                        ? 'border-green-500 bg-green-50'
                        : option.label === selectedAnswer
                        ? 'border-red-500 bg-red-50'
                        : 'opacity-50'
                      : ''
                  } disabled:cursor-not-allowed`}
                >
                  <div className="flex items-start">
                    <span className="font-bold text-navy-700 mr-3">{option.label}.</span>
                    <span className="flex-1">{option.text}</span>
                    {showResults && result && (
                      <>
                        {option.label === result.correct_answer && (
                          <CheckCircle className="w-6 h-6 text-green-600 ml-2" />
                        )}
                        {option.label === selectedAnswer && option.label !== result.correct_answer && (
                          <XCircle className="w-6 h-6 text-red-600 ml-2" />
                        )}
                      </>
                    )}
                  </div>
                </button>
              ))}
            </div>

            {/* Explanation */}
            {showResults && result && result.explanation && (
              <div className="bg-amber-50 border-l-4 border-amber-500 p-4 mb-6">
                <h4 className="font-semibold text-amber-900 mb-2">Explanation</h4>
                <p className="text-amber-800">{result.explanation}</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
              {!showResults ? (
                <button
                  onClick={handleSubmit}
                  disabled={!selectedAnswer || loading}
                  className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Submit Answer
                </button>
              ) : (
                <button onClick={handleNext} className="btn-primary flex-1">
                  {currentIndex < questions.length - 1 ? 'Next Question' : 'Start Over'}
                  <ChevronRight className="w-5 h-5 ml-2 inline" />
                </button>
              )}
              <button onClick={generateNewQuestions} className="btn-secondary">
                <RefreshCw className="w-5 h-5" />
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
