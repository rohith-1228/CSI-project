import { 
  ShieldCheck, 
  AlertTriangle, 
  ShieldAlert, 
  HelpCircle, 
  ArrowRight, 
  RotateCcw, 
  Info,
  ExternalLink,
  CheckCircle
} from 'lucide-react';
import type { AnalyzeResponse } from '../types/api';

interface ResultPanelProps {
  result: AnalyzeResponse;
  onReset: () => void;
}

export const ResultPanel: React.FC<ResultPanelProps> = ({ result, onReset }) => {
  const { verdict, verdict_label, confidence, risk_level, reasons, recommended_action, analyzed_features, disclaimer } = result;

  // Visual configuration based on verdict
  const config = {
    likely_safe: {
      border: 'border-emerald-300',
      bg: 'bg-emerald-50/70',
      badgeBg: 'bg-emerald-100 text-emerald-900 border-emerald-300',
      iconBg: 'bg-emerald-600 text-white',
      accentColor: 'text-emerald-800',
      Icon: ShieldCheck,
      headline: 'No strong warning signs were detected',
      subline: 'The message language and links appear standard, but always stay cautious.'
    },
    suspicious: {
      border: 'border-amber-300',
      bg: 'bg-amber-50/70',
      badgeBg: 'bg-amber-100 text-amber-900 border-amber-300',
      iconBg: 'bg-amber-600 text-white',
      accentColor: 'text-amber-800',
      Icon: AlertTriangle,
      headline: 'One or more warning signs were detected',
      subline: 'This message uses techniques common in unsolicited marketing or deceptive outreach.'
    },
    likely_scam: {
      border: 'border-rose-300',
      bg: 'bg-rose-50/70',
      badgeBg: 'bg-rose-100 text-rose-900 border-rose-300',
      iconBg: 'bg-rose-600 text-white',
      accentColor: 'text-rose-900',
      Icon: ShieldAlert,
      headline: 'Strong indicators of fraud or phishing detected',
      subline: 'High probability of malicious intent. Do not interact with this message.'
    },
    insufficient_evidence: {
      border: 'border-slate-300',
      bg: 'bg-slate-50',
      badgeBg: 'bg-slate-200 text-slate-800 border-slate-300',
      iconBg: 'bg-slate-600 text-white',
      accentColor: 'text-slate-800',
      Icon: HelpCircle,
      headline: 'More context needed for a reliable safety assessment',
      subline: 'The submitted text was too brief or lacked verifiable details.'
    }
  }[verdict] || {
    border: 'border-slate-300',
    bg: 'bg-slate-50',
    badgeBg: 'bg-slate-200 text-slate-800 border-slate-300',
    iconBg: 'bg-slate-600 text-white',
    accentColor: 'text-slate-800',
    Icon: HelpCircle,
    headline: 'Assessment Complete',
    subline: ''
  };

  const { Icon } = config;

  // Format percentage display only if confidence exists and is grounded
  const confidencePercent = confidence !== null ? Math.round(confidence * 100) : null;

  return (
    <section 
      aria-live="polite"
      id="safety-assessment-result"
      className={`mt-5 sm:mt-6 rounded-xl sm:rounded-2xl border-2 ${config.border} ${config.bg} p-4 sm:p-6 md:p-7 shadow-sm transition-all`}
    >
      {/* Top Banner: Verdict & Badges */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4 pb-4 sm:pb-5 border-b border-slate-200/80">
        <div className="flex items-start sm:items-center gap-3 sm:gap-3.5">
          <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl ${config.iconBg} flex items-center justify-center shrink-0 shadow-sm mt-0.5 sm:mt-0`}>
            <Icon className="w-5 h-5 sm:w-6 sm:h-6" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
              <span className="text-[11px] sm:text-xs uppercase tracking-wider font-semibold text-slate-500">
                Safety Assessment
              </span>
              <span className={`inline-flex items-center px-2 sm:px-2.5 py-0.5 rounded-full text-xs font-bold border ${config.badgeBg}`}>
                {verdict_label}
              </span>
              <span className="text-[11px] sm:text-xs font-medium px-2 py-0.5 rounded bg-white text-slate-700 border border-slate-200">
                Risk: {risk_level.toUpperCase()}
              </span>
            </div>
            <h2 className={`text-lg sm:text-2xl font-bold mt-1 leading-snug sm:leading-tight ${config.accentColor}`}>
              {config.headline}
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 mt-0.5 leading-relaxed">
              {config.subline}
            </p>
          </div>
        </div>

        {/* Real Grounded Confidence Score Display */}
        {confidencePercent !== null && (
          <div className="flex items-center justify-between sm:block bg-white/90 sm:bg-transparent p-3 sm:p-0 rounded-xl border border-slate-200/80 sm:border-0 shadow-xs sm:shadow-none sm:text-right shrink-0">
            <div>
              <span className="block text-xs font-medium text-slate-500">
                {verdict === 'likely_safe' ? 'Safety Confidence' : 'Detection Probability'}
              </span>
              <span className="text-[11px] text-slate-500 hidden sm:block">
                {verdict === 'likely_safe' 
                  ? 'Based on evaluated threat absence' 
                  : 'Based on matched attack patterns'}
              </span>
            </div>
            <div className="flex items-baseline sm:justify-end gap-1 shrink-0">
              <span className="text-2xl sm:text-3xl font-black text-slate-900 leading-none">{confidencePercent}%</span>
              <span className="text-[11px] text-slate-500 font-medium">calibrated</span>
            </div>
          </div>
        )}
      </div>

      {/* Grounded Reasons List */}
      <div className="mt-4 sm:mt-5">
        <h3 className="text-xs sm:text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
          <Info className="w-4 h-4 text-slate-500 shrink-0" aria-hidden="true" />
          <span>Why did CyberSaathi give this verdict?</span>
        </h3>
        <ul className="mt-2.5 space-y-2">
          {reasons.map((reason, idx) => (
            <li key={idx} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-800 leading-relaxed bg-white/90 p-2.5 sm:p-3 rounded-lg sm:rounded-xl border border-slate-200/80">
              {verdict === 'likely_scam' ? (
                <ShieldAlert className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" aria-hidden="true" />
              ) : verdict === 'suspicious' ? (
                <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" aria-hidden="true" />
              ) : verdict === 'insufficient_evidence' ? (
                <HelpCircle className="w-4 h-4 text-slate-500 mt-0.5 shrink-0" aria-hidden="true" />
              ) : (
                <CheckCircle className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" aria-hidden="true" />
              )}
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* URL Findings summary if URLs were present */}
      {analyzed_features.urls_found.length > 0 && (
        <div className="mt-4 p-3 sm:p-3.5 bg-white/90 rounded-lg sm:rounded-xl border border-slate-200">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5 mb-2">
            <ExternalLink className="w-3.5 h-3.5 text-slate-500 shrink-0" aria-hidden="true" />
            <span>Analyzed Web Links ({analyzed_features.urls_found.length})</span>
          </h4>
          <div className="space-y-1.5">
            {analyzed_features.url_details.map((u, i) => (
              <div key={i} className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                <span className="font-mono text-slate-800 break-all select-all block">{u.url}</span>
                {u.risk_summary.length > 0 && (
                  <ul className="mt-1.5 list-disc list-inside text-rose-700 space-y-0.5">
                    {u.risk_summary.map((finding, fi) => (
                      <li key={fi}>{finding}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actionable Next Step Box */}
      <div className="mt-4 sm:mt-5 p-3.5 sm:p-4 rounded-xl bg-slate-900 text-white">
        <div className="flex items-start gap-3">
          <div className="p-1 rounded bg-slate-800 text-teal-400 shrink-0 mt-0.5">
            <ArrowRight className="w-4 h-4" aria-hidden="true" />
          </div>
          <div>
            <h4 className="text-xs sm:text-sm font-bold text-teal-300 uppercase tracking-wide">
              What Should You Do Next?
            </h4>
            <p className="mt-1 text-xs sm:text-sm text-slate-100 leading-relaxed font-medium">
              {recommended_action}
            </p>
          </div>
        </div>
      </div>

      {/* Reset & Check Another Message Button */}
      <div className="mt-5 sm:mt-6 flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4 pt-4 border-t border-slate-200">
        <p className="text-[11px] sm:text-xs text-slate-500 leading-normal max-w-lg text-center sm:text-left">
          {disclaimer}
        </p>

        <button
          type="button"
          onClick={onReset}
          className="w-full sm:w-auto min-h-[44px] inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-white hover:bg-slate-100 active:bg-slate-200 text-slate-800 text-sm font-semibold border border-slate-300 shadow-sm transition-all focus-visible:ring-2 focus-visible:ring-slate-800 touch-manipulation cursor-pointer shrink-0"
        >
          <RotateCcw className="w-4 h-4 text-slate-600" aria-hidden="true" />
          <span>Check Another Message</span>
        </button>
      </div>
    </section>
  );
};
