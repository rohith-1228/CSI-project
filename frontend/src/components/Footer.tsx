import React from 'react';
import { ShieldCheck, Lock, AlertTriangle, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer id="privacy" className="bg-slate-900 text-slate-300 mt-16 border-t border-slate-800">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 pb-8 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-teal-500/20 text-teal-400 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4" aria-hidden="true" />
              </div>
              <span className="font-bold text-white text-base">CyberSaathi</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed max-w-sm">
              An open community cyber-safety initiative built to protect ordinary citizens, elderly family members, and first-time digital users from financial scams and phishing deception.
            </p>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-3">
              <Lock className="w-4 h-4 text-emerald-400" aria-hidden="true" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Privacy Guarantee</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              We operate on a strict <strong className="text-emerald-400">zero-retention architecture</strong>. Messages pasted into CyberSaathi are evaluated transiently in server memory and discarded immediately. We do not store, log, catalog, or share your submitted messages, phone numbers, or links.
            </p>
          </div>
        </div>

        {/* Disclaimer Notice */}
        <div className="bg-slate-800/80 rounded-xl p-4 border border-slate-700/80 mb-6 flex items-start gap-3 text-xs text-slate-400">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
          <p className="leading-relaxed">
            <strong className="text-slate-200">Public Service Disclaimer:</strong> CyberSaathi provides automated threat signals using machine learning models and known scam rules. Automated classification can make mistakes or miss novel attack techniques. It does not replace official advice or human diligence. When in doubt, always contact your bank or provider through official helplines.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3">
          <p>© {new Date().getFullYear()} CyberSaathi Community Project. Think before you click.</p>
          <p className="flex items-center gap-1">
            Built with care for public digital safety <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" aria-hidden="true" />
          </p>
        </div>
      </div>
    </footer>
  );
};
