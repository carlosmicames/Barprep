'use client';

import Link from 'next/link';
import { BookOpen, FileText, MessageSquare, TrendingUp, Sparkles, Target, Users } from 'lucide-react';

export default function HomePage() {
  const subjects = [
    'Derecho de Familia',
    'Sucesiones',
    'Derechos Reales',
    'Hipoteca',
    'Obligaciones & Contratos',
    'Ética',
    'Derecho Constitucional',
    'Derecho Administrativo',
    'Daños y Perjuicios',
    'Derecho Penal',
    'Procedimiento Penal',
    'Evidencia',
    'Procedimiento Civil',
  ];

  const features = [
    {
      icon: BookOpen,
      title: 'MCQ Practice',
      description: 'AI-generated multiple-choice questions from official legal materials',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      icon: FileText,
      title: 'Essay Grading',
      description: 'Get instant, citation-backed feedback on your essay responses',
      color: 'text-amber-600',
      bgColor: 'bg-amber-50',
    },
    {
      icon: MessageSquare,
      title: 'Community Chat',
      description: 'Discuss topics with fellow students in real-time chat rooms',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      icon: TrendingUp,
      title: 'Progress Tracking',
      description: 'Monitor your performance across all 13 bar exam subjects',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-navy-900 via-navy-800 to-navy-900 text-white overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 right-10 w-96 h-96 bg-amber-400 rounded-full blur-3xl"></div>
          <div className="absolute bottom-10 left-10 w-80 h-80 bg-blue-400 rounded-full blur-3xl"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
          <div className="text-center space-y-8 animate-fade-in">
            <div className="inline-flex items-center space-x-2 bg-amber-500/20 px-4 py-2 rounded-full border border-amber-400/30">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <span className="text-sm font-medium text-amber-200">AI-Powered Bar Exam Preparation</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-serif font-bold text-balance leading-tight">
              Ace the Puerto Rico<br />
              <span className="text-amber-400">Bar Exam</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto text-balance">
              Comprehensive AI-powered study platform with MCQ practice, essay grading, and community support for all 13 subjects.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link href="/mcq" className="btn-amber text-lg px-8 py-4 w-full sm:w-auto">
                Start Practicing
              </Link>
              <Link href="/progress" className="btn-secondary bg-white/10 border-white/30 text-white hover:bg-white/20 text-lg px-8 py-4 w-full sm:w-auto">
                View Progress
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="section-title">Everything You Need to Succeed</h2>
            <p className="section-subtitle">
              Powered by AI and designed for Puerto Rico bar exam candidates
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="card-hover text-center space-y-4 animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className={`inline-flex p-4 rounded-2xl ${feature.bgColor}`}>
                    <Icon className={`w-8 h-8 ${feature.color}`} />
                  </div>
                  <h3 className="text-xl font-serif font-semibold text-navy-900">
                    {feature.title}
                  </h3>
                  <p className="text-slate-600">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Subjects Section */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="section-title">13 Complete Subjects</h2>
            <p className="section-subtitle">
              Comprehensive coverage of all Puerto Rico bar exam topics
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {subjects.map((subject, index) => (
              <div
                key={index}
                className="card-hover text-center py-6 animate-fade-in"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <p className="font-medium text-navy-900">{subject}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-navy-700 to-navy-900 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          <h2 className="text-4xl md:text-5xl font-serif font-bold">
            Ready to Begin Your Journey?
          </h2>
          <p className="text-xl text-slate-300">
            Join fellow law students preparing for the Puerto Rico bar exam
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/mcq" className="btn-amber text-lg px-8 py-4 w-full sm:w-auto">
              Start with MCQs
            </Link>
            <Link href="/community" className="btn-secondary bg-white/10 border-white/30 text-white hover:bg-white/20 text-lg px-8 py-4 w-full sm:w-auto">
              Join Community
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
