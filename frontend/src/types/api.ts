export type VerdictType = 'likely_safe' | 'suspicious' | 'likely_scam' | 'insufficient_evidence';

export type RiskLevel = 'low' | 'medium' | 'high' | 'unknown';

export interface URLFinding {
  url: string;
  is_https: boolean;
  is_ip_address: boolean;
  is_shortener: boolean;
  is_risky_tld: boolean;
  is_brand_spoof: boolean;
  has_risky_extension: boolean;
  has_redirect_param: boolean;
  risk_summary: string[];
}

export interface AnalyzedFeatures {
  message_length: number;
  urls_found: string[];
  url_details: URLFinding[];
  has_urgency: boolean;
  requests_otp_or_pin: boolean;
  requests_payment_or_money: boolean;
  claims_lottery_or_prize: boolean;
  threatens_service_cutoff: boolean;
  mentions_kyc_or_pan: boolean;
  offers_remote_job: boolean;
  ml_scam_probability: number | null;
}

export interface AnalyzeResponse {
  verdict: VerdictType;
  verdict_label: string;
  confidence: number | null;
  risk_level: RiskLevel;
  reasons: string[];
  recommended_action: string;
  analyzed_features: AnalyzedFeatures;
  model_version: string;
  disclaimer: string;
}

export interface AnalyzeRequest {
  message: string;
}

export interface ServiceInfo {
  name: string;
  version: string;
  description: string;
  documentation_url: string;
  privacy_policy_summary: string;
}

export interface ApiError {
  message: string;
  status?: number;
  isRateLimit?: boolean;
}
