'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BookOpen, FileText, MessageSquare, TrendingUp, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/mcq', label: 'MCQ Practice', icon: BookOpen },
  { href: '/essays', label: 'Essays', icon: FileText },
  { href: '/community', label: 'Community', icon: MessageSquare },
  { href: '/progress', label: 'Progress', icon: TrendingUp },
];

export function Navigation() {
  const pathname = usePathname();
  
  return (
    <nav className="sticky top-0 z-50 bg-white border-b-2 border-navy-700 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-12 h-12 bg-gradient-to-br from-navy-700 to-navy-900 rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform">
              <span className="text-2xl font-serif font-bold text-amber-400">PR</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-serif font-bold text-navy-900 leading-none">
                Bar Exam Prep
              </span>
              <span className="text-xs text-slate-600 font-sans">
                Puerto Rico
              </span>
            </div>
          </Link>
          
          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200',
                    isActive
                      ? 'bg-navy-700 text-white shadow-md'
                      : 'text-navy-700 hover:bg-navy-50'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
          
          {/* Mobile Menu Button */}
          <button className="md:hidden p-2 rounded-lg hover:bg-navy-50">
            <svg className="w-6 h-6 text-navy-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </nav>
  );
}
