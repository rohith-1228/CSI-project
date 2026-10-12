import React, { useState, useEffect } from 'react';
import { ShieldCheck, Lock, Menu, X, ArrowRight } from 'lucide-react';

export const Header: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile navigation drawer on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Close mobile navigation drawer on resize to tablet/desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const closeMenu = () => setMobileMenuOpen(false);

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
        {/* Brand Logo and Title */}
        <a 
          href="/" 
          className="flex items-center gap-2 sm:gap-2.5 group text-decoration-none min-h-[44px] py-1"
          aria-label="CyberSaathi Home"
        >
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-brand-900 flex items-center justify-center text-white shadow-sm shrink-0">
            <ShieldCheck className="w-4 h-4 sm:w-5 sm:h-5 text-teal-300" aria-hidden="true" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="font-bold text-base sm:text-lg text-slate-900 tracking-tight leading-none">
                CyberSaathi
              </span>
              <span className="hidden sm:inline-block text-xs font-medium px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 whitespace-nowrap">
                Community Service
              </span>
            </div>
            <p className="text-[11px] sm:text-xs text-slate-500 hidden sm:block leading-tight mt-0.5">
              Think before you click.
            </p>
          </div>
        </a>

        {/* Desktop & Tablet Navigation (visible on md+) */}
        <nav aria-label="Main Navigation" className="hidden md:flex items-center gap-5 lg:gap-6 text-sm">
          <a
            href="#how-it-works"
            className="text-slate-600 hover:text-slate-900 font-medium transition-colors py-2"
          >
            How It Works
          </a>
          <a
            href="#safety-tips"
            className="text-slate-600 hover:text-slate-900 font-medium transition-colors py-2"
          >
            Safety Tips
          </a>
          <a
            href="#privacy"
            className="text-slate-600 hover:text-slate-900 font-medium transition-colors py-2"
          >
            Privacy
          </a>
          <div className="flex items-center gap-1 text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full font-medium shrink-0">
            <Lock className="w-3 h-3 text-emerald-600" aria-hidden="true" />
            <span>Zero-Retention</span>
          </div>
        </nav>

        {/* Mobile Action Controls (visible below md) */}
        <div className="flex md:hidden items-center gap-2">
          {/* Compact Zero-Retention Indicator */}
          <div 
            className="flex items-center gap-1 text-[11px] text-emerald-800 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full font-medium shrink-0"
            title="Zero-Retention Guarantee"
          >
            <Lock className="w-3 h-3 text-emerald-600 shrink-0" aria-hidden="true" />
            <span className="hidden min-[360px]:inline">Zero-Retention</span>
            <span className="min-[360px]:hidden">Safe</span>
          </div>

          {/* Accessible Hamburger Menu Toggle */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-nav-menu"
            aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            className="w-10 h-10 min-w-[44px] min-h-[44px] rounded-lg text-slate-700 hover:text-slate-900 hover:bg-slate-100 active:bg-slate-200 flex items-center justify-center transition-colors focus-visible:ring-2 focus-visible:ring-brand-700"
          >
            {mobileMenuOpen ? (
              <X className="w-5 h-5 text-slate-700" aria-hidden="true" />
            ) : (
              <Menu className="w-5 h-5 text-slate-700" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Dropdown Menu */}
      {mobileMenuOpen && (
        <div 
          id="mobile-nav-menu"
          className="md:hidden border-t border-slate-200 bg-white shadow-lg animate-in fade-in slide-in-from-top-2 duration-150"
        >
          <nav aria-label="Mobile Navigation" className="px-4 py-3 space-y-1">
            <a
              href="#how-it-works"
              onClick={closeMenu}
              className="flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-semibold text-slate-700 hover:text-brand-900 hover:bg-slate-50 active:bg-slate-100 transition-colors min-h-[44px]"
            >
              <span>How It Works</span>
              <ArrowRight className="w-4 h-4 text-slate-400" aria-hidden="true" />
            </a>
            <a
              href="#safety-tips"
              onClick={closeMenu}
              className="flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-semibold text-slate-700 hover:text-brand-900 hover:bg-slate-50 active:bg-slate-100 transition-colors min-h-[44px]"
            >
              <span>Safety Tips</span>
              <ArrowRight className="w-4 h-4 text-slate-400" aria-hidden="true" />
            </a>
            <a
              href="#privacy"
              onClick={closeMenu}
              className="flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-semibold text-slate-700 hover:text-brand-900 hover:bg-slate-50 active:bg-slate-100 transition-colors min-h-[44px]"
            >
              <span>Privacy Guarantee</span>
              <ArrowRight className="w-4 h-4 text-slate-400" aria-hidden="true" />
            </a>

            <div className="pt-2.5 mt-1 border-t border-slate-100 px-3.5 py-2 flex items-center gap-2 text-xs text-slate-600 bg-slate-50/70 rounded-lg">
              <Lock className="w-3.5 h-3.5 text-emerald-600 shrink-0" aria-hidden="true" />
              <span>Zero-retention architecture. We never save or share your messages.</span>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
};
