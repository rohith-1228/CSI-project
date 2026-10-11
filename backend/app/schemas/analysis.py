"""Pydantic schemas for CyberSaathi request and response contracts."""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class VerdictType(str, Enum):
    LIKELY_SAFE = "likely_safe"
    SUSPICIOUS = "suspicious"
    LIKELY_SCAM = "likely_scam"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"

class AnalyzeRequest(BaseModel):
    message: str = Field(
        ...,
        description="The suspicious SMS, WhatsApp message, email, or URL to analyze.",
        json_schema_extra={"example": "Dear customer, your SBI account is suspended. Update KYC at http://sbi-kyc.xyz immediately."}
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or contain only whitespace.")
        v_clean = v.strip()
        if len(v_clean) > 5000:
            raise ValueError("Message exceeds the maximum permitted length of 5000 characters.")
        return v_clean

class URLFinding(BaseModel):
    url: str
    is_https: bool
    is_ip_address: bool
    is_shortener: bool
    is_risky_tld: bool
    is_brand_spoof: bool
    has_risky_extension: bool
    has_redirect_param: bool
    risk_summary: List[str]

class AnalyzedFeatures(BaseModel):
    message_length: int
    urls_found: List[str] = Field(default_factory=list)
    url_details: List[URLFinding] = Field(default_factory=list)
    has_urgency: bool = False
    requests_otp_or_pin: bool = False
    requests_payment_or_money: bool = False
    claims_lottery_or_prize: bool = False
    threatens_service_cutoff: bool = False
    mentions_kyc_or_pan: bool = False
    offers_remote_job: bool = False
    ml_scam_probability: Optional[float] = None

class AnalyzeResponse(BaseModel):
    verdict: VerdictType
    verdict_label: str
    confidence: Optional[float] = Field(
        None,
        description="Calibrated probability score between 0.0 and 1.0, or null if insufficient evidence."
    )
    risk_level: RiskLevel
    reasons: List[str] = Field(
        ...,
        description="Concise, factual explanations grounded directly in detected indicators."
    )
    recommended_action: str = Field(
        ...,
        description="Practical, clear instruction on what ordinary users should do next."
    )
    analyzed_features: AnalyzedFeatures
    model_version: str
    disclaimer: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    environment: str

class ReadyResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    classifier_ready: bool
    timestamp: str

class ServiceInfoResponse(BaseModel):
    name: str = "CyberSaathi API"
    version: str
    description: str
    documentation_url: str
    privacy_policy_summary: str
