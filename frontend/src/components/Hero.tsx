import { Sparkles, CheckCircle2 } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <section className="pt-6 sm:pt-8 pb-3 sm:pb-4 text-center max-w-2xl mx-auto px-4 sm:px-6" aria-labelledby="hero-title">
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-50 border border-brand-200 text-brand-900 text-xs font-semibold mb-3 sm:mb-4">
        <Sparkles className="w-3.5 h-3.5 text-brand-700 shrink-0" aria-hidden="true" />
        <span className="text-center">Free Community Cyber Safety Tool</span>
      </div>

      <h1 id="hero-title" className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-snug sm:leading-tight">
        Not sure if a message is safe?
      </h1>

      <p className="mt-2.5 sm:mt-3 text-sm sm:text-base md:text-lg text-slate-600 leading-relaxed max-w-xl mx-auto">
        Paste the SMS, WhatsApp forward, email, or link here. We'll help you spot possible scams and tell you what to do next.
      </p>

      <div className="mt-3.5 sm:mt-4 flex flex-wrap items-center justify-center gap-x-3 sm:gap-x-5 gap-y-1.5 sm:gap-y-2 text-xs text-slate-500">
        <span className="inline-flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" aria-hidden="true" />
          <span>No signup or login required</span>
        </span>
        <span className="inline-flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" aria-hidden="true" />
          <span>Zero data stored</span>
        </span>
        <span className="inline-flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" aria-hidden="true" />
          <span>Plain-English results</span>
        </span>
      </div>
    </section>
  );
};
