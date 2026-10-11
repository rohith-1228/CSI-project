import React from 'react';
import { ShieldCheck, Lock } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-slate-200">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2.5 group text-decoration-none">
          <div className="w-9 h-9 rounded-lg bg-brand-900 flex items-center justify-center text-white shadow-sm">
            <ShieldCheck className="w-5 h-5 text-teal-300" aria-hidden="true" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-lg text-slate-900 tracking-tight">CyberSaathi</span>
              <span className="text-xs font-medium px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                Community Service
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">Think before you click.</p>
          </div>
        </a>

        <nav aria-label="Main Navigation" className="flex items-center gap-4 sm:gap-6 text-sm">
          <a
            href="#how-it-works"
            className="text-slate-600 hover:text-slate-900 font-medium transition-colors"
          >
            How It Works
          </a>
          <a
            href="#safety-tips"
            className="text-slate-600 hover:text-slate-900 font-medium transition-colors"
          >
            Safety Tips
          </a>
          <a
            href="#privacy"
            className="text-slate-600 hover:text-slate-900 font-medium hidden sm:inline-block transition-colors"
          >
            Privacy
          </a>
          <div className="flex items-center gap-1 text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full font-medium">
            <Lock className="w-3 h-3 text-emerald-600" aria-hidden="true" />
            <span>Zero-Retention</span>
          </div>
        </nav>
      </div>
    </header>
  );
};
