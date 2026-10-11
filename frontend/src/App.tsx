import React from 'react';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { SafetyChecker } from './components/SafetyChecker';
import { HowItWorks } from './components/HowItWorks';
import { SafetyTips } from './components/SafetyTips';
import { Footer } from './components/Footer';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans selection:bg-brand-100 selection:text-brand-900">
      <Header />
      <main className="flex-1 w-full" id="main-content">
        <Hero />
        <SafetyChecker />
        <HowItWorks />
        <SafetyTips />
      </main>
      <Footer />
    </div>
  );
};

export default App;
