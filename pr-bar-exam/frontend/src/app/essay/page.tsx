'use client';

import { useState, useEffect } from 'react';
import { Send, BookOpen, TrendingUp, Clock, FileText, CheckCircle } from 'lucide-react';
import { api, SUBJECT_NAMES, formatDate, getScoreColor } from '@/lib/utils';

interface Essay {
  id: number;
  user_id: number;
  subject: string;
  prompt: string;
  content: string;
  submitted_at: string;
  grade?: EssayGrade;
}

interface EssayGrade {
  overall_score: number;
  legal_analysis_score?: number;
  writing_quality_score?: number;
  citation_accuracy_score?: number;
  feedback: string;
  point_breakdown?: Record<string, any>;
  citations?: any[];
}

const ESSAY_PROMPTS: Record<string, string[]> = {
  familia: [
    'Discuta los requisitos legales para establecer la custodia compartida en Puerto Rico y los factores que el tribunal considera para determinar el mejor interés del menor.',
    'Analice las causales de divorcio en Puerto Rico y explique el procedimiento legal para obtener un divorcio por mutuo consentimiento.',
  ],
  sucesiones: [
    'Explique la diferencia entre sucesión testamentaria e intestada en Puerto Rico, y los requisitos formales para la validez de un testamento.',
    'Discuta los derechos hereditarios de los legitimarios en Puerto Rico y las limitaciones a la libertad de testar.',
  ],
  reales: [
    'Analice los requisitos para adquirir propiedad por prescripción adquisitiva en Puerto Rico y las diferencias entre prescripción ordinaria y extraordinaria.',
    'Explique el concepto de servidumbre en el derecho puertorriqueño y los diferentes tipos de servidumbres que existen.',
  ],
  hipoteca: [
    'Discuta los elementos esenciales de un contrato de hipoteca en Puerto Rico y el procedimiento de ejecución hipotecaria.',
    'Explique el concepto de hipoteca legal en Puerto Rico y los casos en que se aplica.',
  ],
  obligaciones: [
    'Analice los elementos esenciales de un contrato válido en Puerto Rico y las consecuencias de la nulidad contractual.',
    'Explique el concepto de incumplimiento de contrato y los remedios disponibles para el acreedor en Puerto Rico.',
  ],
  etica: [
    'Discuta las normas éticas que rigen el conflicto de intereses en la práctica legal en Puerto Rico.',
    'Analice las obligaciones éticas del abogado respecto a la confidencialidad del cliente y las excepciones a esta regla.',
  ],
  constitucional: [
    'Analice el derecho fundamental a la libertad de expresión en Puerto Rico y sus limitaciones constitucionales.',
    'Explique el concepto de igual protección bajo la Constitución de Puerto Rico y su aplicación en casos de discriminación.',
  ],
  administrativo: [
    'Discuta los principios que rigen el procedimiento administrativo en Puerto Rico y los derechos de las partes en un proceso administrativo.',
    'Explique el concepto de revisión judicial de decisiones administrativas y los estándares de revisión aplicables.',
  ],
  danos: [
    'Analice los elementos de la responsabilidad extracontractual bajo el Código Civil de Puerto Rico.',
    'Explique los diferentes tipos de daños resarcibles en Puerto Rico y cómo se determina la cuantía de la compensación.',
  ],
  penal: [
    'Discuta los elementos del delito de asesinato en Puerto Rico y las diferencias entre asesinato en primer grado y segundo grado.',
    'Analice las defensas disponibles en casos criminales en Puerto Rico, incluyendo legítima defensa y estado de necesidad.',
  ],
  proc_penal: [
    'Explique los derechos constitucionales del acusado durante el proceso criminal en Puerto Rico.',
    'Discuta el procedimiento de arresto, registro e incautación bajo la Constitución de Puerto Rico.',
  ],
  evidencia: [
    'Analice las reglas sobre admisibilidad de evidencia de referencia en Puerto Rico y sus excepciones.',
    'Explique el concepto de privilegio abogado-cliente y su aplicación en procedimientos judiciales en Puerto Rico.',
  ],
  proc_civil: [
    'Discuta los requisitos de jurisdicción y competencia en procedimientos civiles en Puerto Rico.',
    'Analice el procedimiento de descubrimiento de prueba bajo las Reglas de Procedimiento Civil de Puerto Rico.',
  ],
};

export default function EssayPage() {
  const [selectedSubject, setSelectedSubject] = useState<string>('familia');
  const [selectedPrompt, setSelectedPrompt] = useState<string>('');
  const [essayContent, setEssayContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [submittedEssay, setSubmittedEssay] = useState<Essay | null>(null);
  const [previousEssays, setPreviousEssays] = useState<Essay[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const userId = 1; // In production, get from auth context

  useEffect(() => {
    // Set default prompt when subject changes
    const prompts = ESSAY_PROMPTS[selectedSubject] || [];
    if (prompts.length > 0 && !selectedPrompt) {
      setSelectedPrompt(prompts[0]);
    }
    loadPreviousEssays();
  }, [selectedSubject]);

  const loadPreviousEssays = async () => {
    try {
      const response = await api.essays.getUserEssays(userId, selectedSubject);
      setPreviousEssays(response.data);
    } catch (error) {
      console.error('Error loading previous essays:', error);
    }
  };

  const handleSubmit = async () => {
    if (!essayContent.trim() || !selectedPrompt) return;

    setLoading(true);
    try {
      const response = await api.essays.submit(userId, {
        subject: selectedSubject,
        prompt: selectedPrompt,
        content: essayContent,
      });
      setSubmittedEssay(response.data);
      setEssayContent('');
      loadPreviousEssays();
    } catch (error) {
      console.error('Error submitting essay:', error);
      alert('Error submitting essay. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const wordCount = essayContent.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 animate-slide-up">
          <h1 className="text-4xl font-serif font-bold text-navy-900 mb-4">
            Essay Practice
          </h1>
          <p className="text-lg text-slate-600">
            Write essays and receive AI-powered feedback based on official legal materials
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Essay Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Subject & Prompt Selection */}
            <div className="card animate-slide-up">
              <label className="block text-sm font-medium text-navy-900 mb-3">
                Select Subject
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
                {Object.entries(SUBJECT_NAMES).slice(0, 6).map(([code, name]) => (
                  <button
                    key={code}
                    onClick={() => {
                      setSelectedSubject(code);
                      setSelectedPrompt('');
                      setSubmittedEssay(null);
                    }}
                    className={`p-3 rounded-lg font-medium transition-all text-sm ${
                      selectedSubject === code
                        ? 'bg-navy-700 text-white shadow-md'
                        : 'bg-slate-100 text-navy-700 hover:bg-slate-200'
                    }`}
                  >
                    {name}
                  </button>
                ))}
              </div>

              <label className="block text-sm font-medium text-navy-900 mb-3">
                Essay Prompt
              </label>
              <select
                value={selectedPrompt}
                onChange={(e) => setSelectedPrompt(e.target.value)}
                className="w-full p-3 border-2 border-slate-300 rounded-lg focus:border-navy-700 focus:outline-none"
              >
                <option value="">Select a prompt...</option>
                {(ESSAY_PROMPTS[selectedSubject] || []).map((prompt, idx) => (
                  <option key={idx} value={prompt}>
                    Prompt {idx + 1}
                  </option>
                ))}
              </select>

              {selectedPrompt && (
                <div className="mt-4 p-4 bg-amber-50 border-l-4 border-amber-500 rounded">
                  <p className="text-navy-900">{selectedPrompt}</p>
                </div>
              )}
            </div>

            {/* Essay Input */}
            {!submittedEssay ? (
              <div className="card animate-slide-up animation-delay-200">
                <label className="block text-sm font-medium text-navy-900 mb-3">
                  Your Essay
                </label>
                <textarea
                  value={essayContent}
                  onChange={(e) => setEssayContent(e.target.value)}
                  placeholder="Write your essay here... Analyze the legal issues, apply relevant law, and provide citations to support your arguments."
                  className="w-full h-96 p-4 border-2 border-slate-300 rounded-lg focus:border-navy-700 focus:outline-none resize-none"
                  disabled={loading || !selectedPrompt}
                />
                <div className="flex justify-between items-center mt-4">
                  <span className="text-sm text-slate-600">
                    <Clock className="w-4 h-4 inline mr-1" />
                    {wordCount} words
                  </span>
                  <button
                    onClick={handleSubmit}
                    disabled={!essayContent.trim() || !selectedPrompt || loading}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2 inline-block"></div>
                        Grading...
                      </>
                    ) : (
                      <>
                        <Send className="w-5 h-5 mr-2 inline" />
                        Submit Essay
                      </>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              /* Grade Display */
              <div className="card animate-slide-up animation-delay-200">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-serif font-bold text-navy-900">
                    Your Grade
                  </h3>
                  <button
                    onClick={() => setSubmittedEssay(null)}
                    className="btn-secondary text-sm"
                  >
                    Write Another
                  </button>
                </div>

                {/* Overall Score */}
                {submittedEssay.grade && (
                  <>
                    <div className="text-center mb-6 p-6 bg-gradient-to-br from-navy-50 to-slate-50 rounded-lg">
                      <div className={`text-6xl font-bold ${getScoreColor(submittedEssay.grade.overall_score)}`}>
                        {submittedEssay.grade.overall_score.toFixed(1)}
                      </div>
                      <div className="text-sm text-slate-600 mt-2">Overall Score</div>
                    </div>

                    {/* Score Breakdown */}
                    {(submittedEssay.grade.legal_analysis_score ||
                      submittedEssay.grade.writing_quality_score ||
                      submittedEssay.grade.citation_accuracy_score) && (
                      <div className="grid grid-cols-3 gap-4 mb-6">
                        {submittedEssay.grade.legal_analysis_score && (
                          <div className="text-center p-4 bg-slate-50 rounded-lg">
                            <div className="text-2xl font-bold text-navy-700">
                              {submittedEssay.grade.legal_analysis_score.toFixed(1)}
                            </div>
                            <div className="text-xs text-slate-600 mt-1">Legal Analysis</div>
                          </div>
                        )}
                        {submittedEssay.grade.writing_quality_score && (
                          <div className="text-center p-4 bg-slate-50 rounded-lg">
                            <div className="text-2xl font-bold text-navy-700">
                              {submittedEssay.grade.writing_quality_score.toFixed(1)}
                            </div>
                            <div className="text-xs text-slate-600 mt-1">Writing Quality</div>
                          </div>
                        )}
                        {submittedEssay.grade.citation_accuracy_score && (
                          <div className="text-center p-4 bg-slate-50 rounded-lg">
                            <div className="text-2xl font-bold text-navy-700">
                              {submittedEssay.grade.citation_accuracy_score.toFixed(1)}
                            </div>
                            <div className="text-xs text-slate-600 mt-1">Citations</div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Feedback */}
                    <div className="bg-amber-50 border-l-4 border-amber-500 p-6 rounded">
                      <h4 className="font-semibold text-amber-900 mb-3 flex items-center">
                        <FileText className="w-5 h-5 mr-2" />
                        Detailed Feedback
                      </h4>
                      <div className="text-amber-800 whitespace-pre-wrap">
                        {submittedEssay.grade.feedback}
                      </div>
                    </div>

                    {/* Citations */}
                    {submittedEssay.grade.citations && submittedEssay.grade.citations.length > 0 && (
                      <div className="mt-6 bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
                        <h4 className="font-semibold text-blue-900 mb-3">
                          Referenced Sources
                        </h4>
                        <ul className="space-y-2">
                          {submittedEssay.grade.citations.map((citation, idx) => (
                            <li key={idx} className="text-sm text-blue-800">
                              <CheckCircle className="w-4 h-4 inline mr-2 text-blue-600" />
                              {typeof citation === 'string' ? citation : JSON.stringify(citation)}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Tips */}
            <div className="card animate-slide-up animation-delay-400">
              <h3 className="text-lg font-serif font-bold text-navy-900 mb-4 flex items-center">
                <BookOpen className="w-5 h-5 mr-2" />
                Writing Tips
              </h3>
              <ul className="space-y-3 text-sm text-slate-700">
                <li className="flex items-start">
                  <span className="text-amber-600 mr-2">•</span>
                  <span>Identify all legal issues clearly</span>
                </li>
                <li className="flex items-start">
                  <span className="text-amber-600 mr-2">•</span>
                  <span>State the applicable law and rules</span>
                </li>
                <li className="flex items-start">
                  <span className="text-amber-600 mr-2">•</span>
                  <span>Apply the law to the facts systematically</span>
                </li>
                <li className="flex items-start">
                  <span className="text-amber-600 mr-2">•</span>
                  <span>Provide citations to support your analysis</span>
                </li>
                <li className="flex items-start">
                  <span className="text-amber-600 mr-2">•</span>
                  <span>Reach a clear conclusion</span>
                </li>
                <li className="flex items-start">
                  <span className="text-amber-600 mr-2">•</span>
                  <span>Use proper legal terminology</span>
                </li>
              </ul>
            </div>

            {/* Previous Essays */}
            <div className="card animate-slide-up animation-delay-600">
              <h3 className="text-lg font-serif font-bold text-navy-900 mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                Your Progress
              </h3>
              {previousEssays.length > 0 ? (
                <div className="space-y-3">
                  <div className="text-center p-4 bg-gradient-to-br from-navy-50 to-slate-50 rounded-lg">
                    <div className="text-3xl font-bold text-navy-700">
                      {previousEssays.length}
                    </div>
                    <div className="text-sm text-slate-600">Essays Submitted</div>
                  </div>
                  {previousEssays.filter(e => e.grade).length > 0 && (
                    <div className="text-center p-4 bg-gradient-to-br from-amber-50 to-slate-50 rounded-lg">
                      <div className="text-3xl font-bold text-amber-600">
                        {(
                          previousEssays
                            .filter(e => e.grade)
                            .reduce((sum, e) => sum + (e.grade?.overall_score || 0), 0) /
                          previousEssays.filter(e => e.grade).length
                        ).toFixed(1)}
                      </div>
                      <div className="text-sm text-slate-600">Average Score</div>
                    </div>
                  )}
                  <button
                    onClick={() => setShowHistory(!showHistory)}
                    className="btn-secondary w-full text-sm"
                  >
                    {showHistory ? 'Hide' : 'Show'} History
                  </button>
                  {showHistory && (
                    <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
                      {previousEssays.map((essay) => (
                        <div
                          key={essay.id}
                          className="p-3 bg-slate-50 rounded border border-slate-200 hover:border-navy-300 transition-colors cursor-pointer"
                          onClick={() => setSubmittedEssay(essay)}
                        >
                          <div className="flex justify-between items-start">
                            <div className="text-xs text-slate-600">
                              {formatDate(essay.submitted_at)}
                            </div>
                            {essay.grade && (
                              <div className={`text-sm font-bold ${getScoreColor(essay.grade.overall_score)}`}>
                                {essay.grade.overall_score.toFixed(1)}
                              </div>
                            )}
                          </div>
                          <div className="text-xs text-slate-500 mt-1 line-clamp-2">
                            {essay.prompt}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-slate-600 text-center py-4">
                  No essays submitted yet. Start writing to track your progress!
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
