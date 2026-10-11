import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../App';
import * as apiModule from '../services/api';
import type { AnalyzeResponse } from '../types/api';

describe('CyberSaathi Frontend Application', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders header, hero, checker input, and guidance sections', () => {
    render(<App />);

    // Brand and Tagline (present in header and footer)
    const brandElements = screen.getAllByText('CyberSaathi');
    expect(brandElements.length).toBeGreaterThanOrEqual(1);
    const taglines = screen.getAllByText(/Think before you click/i);
    expect(taglines.length).toBeGreaterThanOrEqual(1);

    // Hero title
    expect(screen.getByRole('heading', { name: /Not sure if a message is safe\?/i })).toBeInTheDocument();

    // Input textarea & Check button
    expect(screen.getByPlaceholderText(/Paste the SMS, WhatsApp message, email, or link here/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Check Safety/i })).toBeInTheDocument();

    // How it works and safety tips
    expect(screen.getByRole('heading', { name: /How It Works/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Practical Cyber Safety Tips/i })).toBeInTheDocument();
  });

  it('disables check button when empty and validates whitespace submissions', async () => {
    render(<App />);

    const textarea = screen.getByPlaceholderText(/Paste the SMS, WhatsApp message, email, or link here/i) as HTMLTextAreaElement;
    const checkBtn = screen.getByRole('button', { name: /Check Safety/i });

    // Initially empty -> button disabled
    expect(checkBtn).toBeDisabled();

    // If submitted via form with whitespace
    const form = textarea.closest('form')!;
    fireEvent.submit(form);

    expect(await screen.findByText(/Please paste an SMS, WhatsApp message, email, or link to check/i)).toBeInTheDocument();
  });

  it('populates message when clicking sample buttons', async () => {
    const user = userEvent.setup();
    render(<App />);

    const kycSampleBtn = screen.getByRole('button', { name: /Bank KYC Scam/i });
    await user.click(kycSampleBtn);

    const textarea = screen.getByPlaceholderText(/Paste the SMS, WhatsApp message, email, or link here/i) as HTMLTextAreaElement;
    expect(textarea.value).toContain('SBI account has been suspended');
  });

  it('renders LIKELY SCAM verdict panel with grounded reasons and recommended action', async () => {
    const user = userEvent.setup();

    const mockScamResponse: AnalyzeResponse = {
      verdict: 'likely_scam',
      verdict_label: 'Likely Scam',
      confidence: 0.94,
      risk_level: 'high',
      reasons: [
        'The message attempts to solicit a one-time password (OTP).',
        'Uses urgent deadline pressure claiming immediate suspension.'
      ],
      recommended_action: 'Do NOT click any links or share passwords. Delete this message immediately.',
      analyzed_features: {
        message_length: 120,
        urls_found: ['http://sbi-fake.xyz'],
        url_details: [
          {
            url: 'http://sbi-fake.xyz',
            is_https: false,
            is_ip_address: false,
            is_shortener: false,
            is_risky_tld: true,
            is_brand_spoof: true,
            has_risky_extension: false,
            has_redirect_param: false,
            risk_summary: ['Uses disposable .xyz domain']
          }
        ],
        has_urgency: true,
        requests_otp_or_pin: true,
        requests_payment_or_money: false,
        claims_lottery_or_prize: false,
        threatens_service_cutoff: false,
        mentions_kyc_or_pan: true,
        offers_remote_job: false,
        ml_scam_probability: 0.94
      },
      model_version: 'cybersaathi-v1.0.0',
      disclaimer: 'CyberSaathi provides automated safety analysis.'
    };

    vi.spyOn(apiModule, 'analyzeMessage').mockResolvedValue(mockScamResponse);

    render(<App />);

    const textarea = screen.getByPlaceholderText(/Paste the SMS, WhatsApp message, email, or link here/i);
    await user.type(textarea, 'Urgent: Call now to share your OTP or account blocked');

    const checkBtn = screen.getByRole('button', { name: /Check Safety/i });
    await user.click(checkBtn);

    // Verify verdict badge and reasons
    expect(await screen.findByText('Likely Scam')).toBeInTheDocument();
    expect(screen.getByText(/Strong indicators of fraud or phishing detected/i)).toBeInTheDocument();
    expect(screen.getByText(/The message attempts to solicit a one-time password \(OTP\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Do NOT click any links or share passwords/i)).toBeInTheDocument();
    expect(screen.getByText('94%')).toBeInTheDocument();

    // Verify Check Another Message button resets
    const resetBtn = screen.getByRole('button', { name: /Check Another Message/i });
    await user.click(resetBtn);
    expect(screen.queryByText(/Likely Scam/i)).not.toBeInTheDocument();
  });

  it('renders LIKELY SAFE verdict panel correctly', async () => {
    const user = userEvent.setup();

    const mockSafeResponse: AnalyzeResponse = {
      verdict: 'likely_safe',
      verdict_label: 'Likely Safe',
      confidence: 0.98,
      risk_level: 'low',
      reasons: [
        'No known scam patterns, malicious links, or credential-theft indicators were detected.'
      ],
      recommended_action: 'The message appears normal. Always maintain standard vigilance.',
      analyzed_features: {
        message_length: 50,
        urls_found: [],
        url_details: [],
        has_urgency: false,
        requests_otp_or_pin: false,
        requests_payment_or_money: false,
        claims_lottery_or_prize: false,
        threatens_service_cutoff: false,
        mentions_kyc_or_pan: false,
        offers_remote_job: false,
        ml_scam_probability: 0.02
      },
      model_version: 'cybersaathi-v1.0.0',
      disclaimer: 'Automated detection can make mistakes.'
    };

    vi.spyOn(apiModule, 'analyzeMessage').mockResolvedValue(mockSafeResponse);

    render(<App />);

    const textarea = screen.getByPlaceholderText(/Paste the SMS, WhatsApp message, email, or link here/i);
    await user.type(textarea, 'Hi, are we still meeting tomorrow for lunch at 1pm?');

    const checkBtn = screen.getByRole('button', { name: /Check Safety/i });
    await user.click(checkBtn);

    expect(await screen.findByText('Likely Safe')).toBeInTheDocument();
    expect(screen.getByText(/No strong warning signs were detected/i)).toBeInTheDocument();
    expect(screen.getByText('98%')).toBeInTheDocument();
  });

  it('handles backend error and shows retry instructions', async () => {
    const user = userEvent.setup();

    vi.spyOn(apiModule, 'analyzeMessage').mockRejectedValue({
      message: 'Unable to connect to the safety server. Please ensure the backend is running.',
      status: 503
    });

    render(<App />);

    const textarea = screen.getByPlaceholderText(/Paste the SMS, WhatsApp message, email, or link here/i);
    await user.type(textarea, 'Test message for failure');

    const checkBtn = screen.getByRole('button', { name: /Check Safety/i });
    await user.click(checkBtn);

    expect(await screen.findByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(/Unable to connect to the safety server/i)).toBeInTheDocument();
  });
});
