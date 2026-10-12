import React, { useState, useRef } from 'react';
import { 
  ShieldCheck, 
  Trash2, 
  Loader2, 
  AlertCircle, 
  Sparkles,
  ClipboardPaste
} from 'lucide-react';
import { analyzeMessage } from '../services/api';
import type { AnalyzeResponse, ApiError } from '../types/api';
import { ResultPanel } from './ResultPanel';

const MAX_CHARS = 5000;

// Curated realistic sample prompts for easy 1-click testing
const SAMPLES = [
  {
    label: 'Bank KYC Scam',
    text: 'Dear customer, your SBI account has been suspended today due to pending KYC verification. Click http://sbi-kyc-verify.xyz to update PAN immediately or your account will be blocked.'
  },
  {
    label: 'Electricity Cutoff',
    text: 'URGENT: Your electricity connection will be disconnected tonight at 9:30 PM due to unpaid previous month bill. Please call electricity officer Rahul Sharma on 9876543210 immediately.'
  },
  {
    label: 'UPI Cash Reward',
    text: 'Congratulations! You won Rs 2,999 cashback in PhonePe festive scratch card. Click http://cashback-phonepe.xyz/claim and enter your UPI PIN to receive money in your bank.'
  },
  {
    label: 'Safe Message',
    text: 'Your A/C ending XX4921 has been debited with INR 350.00 on 10-Oct-2024 via UPI. Ref No: 42918491829. Available balance is INR 14,210.00. - HDFC Bank'
  }
];

export const SafetyChecker: React.FC = () => {
  const [message, setMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleClear = () => {
    setMessage('');
    setError(null);
    setResult(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleSelectSample = (sampleText: string) => {
    setMessage(sampleText);
    setError(null);
    setResult(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = message.trim();

    if (!trimmed) {
      setError({ message: 'Please paste an SMS, WhatsApp message, email, or link to check.' });
      return;
    }

    if (trimmed.length > MAX_CHARS) {
      setError({ message: `Message exceeds maximum allowed length of ${MAX_CHARS} characters.` });
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await analyzeMessage(trimmed);
      setResult(response);
      // Smoothly scroll to result if supported
      setTimeout(() => {
        const el = document.getElementById('safety-assessment-result');
        if (el && typeof el.scrollIntoView === 'function') {
          el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    } catch (err: any) {
      setError(err as ApiError);
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-3.5 sm:px-6 py-2 sm:py-4">
      {/* Main Input Form Card */}
      <div className="bg-white rounded-xl sm:rounded-2xl border border-slate-200 shadow-sm p-4 sm:p-6 md:p-7">
        <form onSubmit={handleSubmit} noValidate>
          <div className="flex items-center justify-between gap-2 mb-2">
            <label 
              htmlFor="message-input" 
              className="text-xs sm:text-sm font-bold text-slate-900 flex items-center gap-1.5"
            >
              <ClipboardPaste className="w-4 h-4 text-brand-700 shrink-0" aria-hidden="true" />
              <span>Paste Suspicious Message or Web Link</span>
            </label>

            <span 
              className={`text-xs font-mono shrink-0 ${
                message.length > MAX_CHARS ? 'text-rose-600 font-bold' : 'text-slate-600'
              }`}
              aria-live="polite"
            >
              {message.length} / {MAX_CHARS}
            </span>
          </div>

          <div className="relative">
            <textarea
              id="message-input"
              ref={textareaRef}
              rows={5}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Paste the SMS, WhatsApp message, email, or link here..."
              className="w-full rounded-xl border border-slate-300 p-3.5 sm:p-4 text-slate-900 text-base placeholder:text-slate-600 focus:border-brand-700 focus:ring-1 focus:ring-brand-700 transition-all resize-y min-h-[130px] sm:min-h-[140px] leading-relaxed"
              disabled={isLoading}
              aria-invalid={!!error}
              aria-describedby={error ? 'checker-error' : undefined}
            />

            {message.length > 0 && !isLoading && (
              <button
                type="button"
                onClick={handleClear}
                className="absolute top-2 right-2 sm:top-3 sm:right-3 text-slate-600 hover:text-slate-800 p-1.5 sm:p-2 rounded-lg bg-slate-100/80 hover:bg-slate-200 transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center"
                title="Clear input"
                aria-label="Clear input message"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Quick Sample Selector */}
          <div className="mt-3.5">
            <div className="flex items-center gap-1.5 text-xs font-medium text-slate-500 mb-2">
              <Sparkles className="w-3.5 h-3.5 text-brand-600 shrink-0" aria-hidden="true" />
              <span>Try sample:</span>
            </div>
            <div className="flex flex-wrap gap-1.5 sm:gap-2">
              {SAMPLES.map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectSample(s.text)}
                  disabled={isLoading}
                  className="text-xs font-medium px-2.5 sm:px-3 py-1.5 sm:py-1 rounded-lg bg-slate-100 hover:bg-slate-200 active:bg-slate-300 text-slate-700 border border-slate-200 transition-colors touch-manipulation min-h-[36px] sm:min-h-0 flex items-center justify-center text-center"
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Validation & API Error Banner */}
          {error && (
            <div 
              id="checker-error" 
              role="alert" 
              className="mt-4 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-sm flex items-start gap-2.5"
            >
              <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" aria-hidden="true" />
              <div className="flex-1">
                <span className="font-semibold block">{error.message}</span>
                {error.status === 503 && (
                  <p className="mt-1 text-xs text-rose-700">
                    Make sure the Python backend server is running with <code className="bg-rose-100 px-1 py-0.5 rounded">python -m uvicorn backend.app.main:app --port 8000</code>.
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Submit Action Button */}
          <div className="mt-5 flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4">
            <p className="text-xs text-slate-500 text-center sm:text-left">
              Analyzed in real time using Machine Learning and cyber-threat rules.
            </p>

            <button
              type="submit"
              disabled={isLoading || message.trim().length === 0}
              className={`w-full sm:w-auto min-w-[180px] h-12 px-6 rounded-xl font-bold text-base flex items-center justify-center gap-2 transition-all shadow-sm active:scale-[0.99] touch-manipulation shrink-0 ${
                isLoading || message.trim().length === 0
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300'
                  : 'bg-brand-900 hover:bg-brand-950 text-white shadow-brand-900/10 hover:shadow-md cursor-pointer'
              }`}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin text-teal-300" aria-hidden="true" />
                  <span>Checking this message...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-5 h-5 text-teal-300" aria-hidden="true" />
                  <span>Check Safety</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Result Panel Rendered Immediately Below */}
      {result && (
        <ResultPanel 
          result={result} 
          onReset={handleClear} 
        />
      )}
    </div>
  );
};
