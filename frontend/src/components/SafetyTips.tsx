import React from 'react';
import { 
  KeyRound, 
  ClockAlert, 
  Globe2, 
  Building2, 
  DownloadCloud 
} from 'lucide-react';

export const SafetyTips: React.FC = () => {
  const tips = [
    {
      title: 'Never share OTPs or PINs',
      detail: 'Banks, government bodies, and courier delivery personnel will NEVER ask you to read out your OTP or enter your UPI PIN to receive money.',
      Icon: KeyRound
    },
    {
      title: 'Resist artificial urgency',
      detail: 'Scammers use threats like "power cutoff in 2 hours" or "account blocked today" to provoke panic. Take a breath and verify before reacting.',
      Icon: ClockAlert
    },
    {
      title: 'Examine web domain addresses',
      detail: 'Look closely at website URLs. A bank will never ask you to log in on addresses ending in .xyz, .top, or raw numbers like 192.168.x.x.',
      Icon: Globe2
    },
    {
      title: 'Verify via official helplines',
      detail: 'Never call phone numbers printed inside suspicious messages. Search for the company’s official helpline on their verified app or website.',
      Icon: Building2
    },
    {
      title: 'Never install unverified APK files',
      detail: 'Do not tap on attachments or links offering to install APK files sent on WhatsApp or SMS. They often contain malware that steals your SMS OTPs.',
      Icon: DownloadCloud
    }
  ];

  return (
    <section id="safety-tips" className="max-w-3xl mx-auto px-3.5 sm:px-6 py-8 sm:py-12 border-t border-slate-200" aria-labelledby="safety-tips-title">
      <div className="text-center mb-6 sm:mb-8">
        <h2 id="safety-tips-title" className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
          Practical Cyber Safety Tips
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 mt-1">
          Simple golden rules to protect you and your family from modern online fraud.
        </p>
      </div>

      <div className="space-y-3 sm:space-y-3.5">
        {tips.map((tip, idx) => {
          const { Icon } = tip;
          return (
            <div 
              key={idx}
              className="bg-white rounded-xl p-3.5 sm:p-5 border border-slate-200 shadow-sm flex items-start gap-3 sm:gap-4 transition-all hover:border-slate-300"
            >
              <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                <Icon className="w-4 h-4 sm:w-5 sm:h-5 text-brand-800" aria-hidden="true" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm sm:text-base font-bold text-slate-900">
                  {tip.title}
                </h3>
                <p className="mt-0.5 sm:mt-1 text-xs sm:text-sm text-slate-600 leading-relaxed">
                  {tip.detail}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
