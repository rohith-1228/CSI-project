import React from 'react';
import { ClipboardPaste, Search, CheckCircle } from 'lucide-react';

export const HowItWorks: React.FC = () => {
  const steps = [
    {
      num: '1',
      title: 'Paste the message',
      description: 'Copy any suspicious SMS, WhatsApp forward, email alert, or web address and paste it into the checker.',
      Icon: ClipboardPaste
    },
    {
      num: '2',
      title: 'AI checks for warning signs',
      description: 'Our system analyzes wording, deceptive domains, urgency patterns, and credential-theft attempts.',
      Icon: Search
    },
    {
      num: '3',
      title: 'Follow the safety recommendation',
      description: 'Get an immediate, clear verdict and simple, actionable guidance on what steps you should take.',
      Icon: CheckCircle
    }
  ];

  return (
    <section id="how-it-works" className="max-w-3xl mx-auto px-3.5 sm:px-6 py-8 sm:py-12 border-t border-slate-200 mt-6 sm:mt-8" aria-labelledby="how-it-works-title">
      <div className="text-center mb-6 sm:mb-8">
        <h2 id="how-it-works-title" className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
          How It Works
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 mt-1">
          Simple three-step safety check designed for everyday citizens.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 sm:gap-5 md:gap-6">
        {steps.map((s, idx) => {
          const { Icon } = s;
          return (
            <div 
              key={idx}
              className="bg-white rounded-xl p-4 sm:p-5 border border-slate-200 shadow-sm relative flex flex-col items-center text-center transition-all hover:border-slate-300"
            >
              <div className="w-10 h-10 rounded-full bg-brand-50 border border-brand-200 text-brand-900 flex items-center justify-center font-bold text-base mb-2.5 sm:mb-3 shadow-xs shrink-0">
                <Icon className="w-5 h-5 text-brand-700" aria-hidden="true" />
              </div>
              <span className="text-[11px] sm:text-xs uppercase font-bold text-brand-800 tracking-wider mb-1">
                Step {s.num}
              </span>
              <h3 className="text-sm sm:text-base font-bold text-slate-900 mb-1 sm:mb-1.5">
                {s.title}
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                {s.description}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
};
