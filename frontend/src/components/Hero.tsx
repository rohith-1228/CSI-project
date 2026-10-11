import { Sparkles, CheckCircle2 } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <section className="pt-8 pb-4 text-center max-w-2xl mx-auto px-4" aria-labelledby="hero-title">
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-50 border border-brand-200 text-brand-900 text-xs font-semibold mb-4">
        <Sparkles className="w-3.5 h-3.5 text-brand-700" aria-hidden="true" />
        <span>Free Community Cyber Safety Tool</span>
      </div>

      <h1 id="hero-title" className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
        Not sure if a message is safe?
      </h1>

      <p className="mt-3 text-base sm:text-lg text-slate-600 leading-relaxed">
        Paste the SMS, WhatsApp forward, email, or link here. We'll help you spot possible scams and tell you what to do next.
      </p>

      <div className="mt-4 flex flex-wrap items-center justify-center gap-y-2 gap-x-5 text-xs text-slate-500">
        <span className="flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" aria-hidden="true" />
          No signup or login required
        </span>
        <span className="flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" aria-hidden="true" />
          Zero data stored
        </span>
        <span className="flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" aria-hidden="true" />
          Plain-English results
        </span>
      </div>
    </section>
  );
};
