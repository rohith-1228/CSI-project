"""
CyberSaathi Unified Safety Assessment Engine.
Integrates ML probability predictions, static URL analysis, and deterministic heuristic rules
into a calibrated, transparent, and grounded safety verdict.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from backend.app.schemas.analysis import (
    VerdictType, RiskLevel, AnalyzeResponse, AnalyzedFeatures, URLFinding
)
from backend.app.services.url_analyzer import analyze_all_urls
from backend.app.ml.classifier import classifier

# Heuristic pattern definitions for scam indicators
PATTERNS = {
    "otp_theft": re.compile(
        r'\b(?:share|send|forward|tell|enter|provide|reply with)\b.*?\b(?:otp|one[- ]time[- ]password|pin|upi[- ]pin|password|cvv|secret code)\b|\b(?:cancellation|verification|authorization)\s+otp\b',
        re.IGNORECASE
    ),
    "urgency": re.compile(
        r'\b(?:immediately|urgent|within\s+\d+\s*(?:hours?|hrs?|mins?|minutes?)|tonight|by\s+evening|today|suspended\s+today|blocked\s+today|permanently\s+(?:closed|blocked)|immediate\s+action)\b',
        re.IGNORECASE
    ),
    "service_cutoff": re.compile(
        r'\b(?:electricity|power|bijli|gas|water|sim|connection)\b.*?\b(?:disconnected|cut\s*off|suspended|severed|blocked)\b|\b(?:power|supply)\s+will\s+be\s+disconnected\b',
        re.IGNORECASE
    ),
    "kyc_pan": re.compile(
        r'\b(?:kyc|pan\s*card|aadhaar|netbanking|debit\s*card|credit\s*card)\b.*?\b(?:update|expire|expired|pending|suspended|blocked|verify|unblock|hold)\b|\b(?:update|submit)\s+(?:your\s+)?(?:pan|kyc|aadhaar)\b',
        re.IGNORECASE
    ),
    "lottery_prize": re.compile(
        r'\b(?:congratulations|winner|won|lucky\s*draw|lottery|kbc|kaun\s*banega\s*crorepati|prize\s*money|jackpot|reward\s*points)\b.*?(?:\d+[\d,]*\s*(?:lakhs?|crores?|rs\.?|inr|\$)|mercedes|cash)',
        re.IGNORECASE
    ),
    "upi_reward": re.compile(
        r'\b(?:cashback|scratch\s*card|reward|festive\s*bonus)\b.*?\b(?:phonepe|gpay|googlepay|paytm)\b|\b(?:claim|accept)\s+(?:cashback|reward)\b',
        re.IGNORECASE
    ),
    "remote_job": re.compile(
        r'\b(?:part[- ]time\s*job|work\s*from\s*home|daily\s*income|earn\s*(?:rs|inr|\$)?\s*\d+).*?\b(?:telegram|whatsapp|liking\s*youtube|rating\s*hotels|reviews)\b',
        re.IGNORECASE
    ),
    "fake_loan": re.compile(
        r'\b(?:instant\s*loan|personal\s*loan|pre[- ]approved\s*loan)\b.*?\b(?:zero|0%|no\s*cibil|no\s*documents?|without\s*cibil)\b',
        re.IGNORECASE
    ),
    "delivery_failure": re.compile(
        r'\b(?:package|parcel|shipment|delivery)\b.*?\b(?:cannot\s*be\s*delivered|failed|wrong\s*address|incomplete\s*address|redelivery)\b',
        re.IGNORECASE
    )
}

DISCLAIMER_TEXT = (
    "CyberSaathi provides automated safety analysis based on machine learning and known threat patterns. "
    "Automated detection cannot provide a 100% guarantee of safety. When in doubt, always verify directly "
    "with the official organization using contact information from their genuine website or official app."
)

def is_insufficient_evidence(text: str) -> bool:
    """Detects if message is too short or lacks substantive content for a reliable verdict."""
    cleaned = text.strip()
    words = cleaned.split()
    if len(words) < 3 and len(cleaned) < 15:
        return True
    # Common conversational greetings without context
    trivial_phrases = {"hi", "hello", "hey", "ok", "okay", "yes", "no", "good morning", "good night", "thanks", "thank you"}
    if cleaned.lower() in trivial_phrases:
        return True
    return False

def assess_safety(message: str) -> AnalyzeResponse:
    """
    Evaluates message safety across ML, URL features, and heuristic scam indicators.
    Follows a documented, non-overriding safety policy.
    """
    clean_msg = message.strip()
    urls_data = analyze_all_urls(clean_msg)
    url_strings = [u["url"] for u in urls_data]
    url_findings = [URLFinding(**u) for u in urls_data]

    # Rule detections
    has_otp = bool(PATTERNS["otp_theft"].search(clean_msg))
    has_urgency = bool(PATTERNS["urgency"].search(clean_msg))
    has_cutoff = bool(PATTERNS["service_cutoff"].search(clean_msg))
    has_kyc = bool(PATTERNS["kyc_pan"].search(clean_msg))
    has_lottery = bool(PATTERNS["lottery_prize"].search(clean_msg))
    has_upi = bool(PATTERNS["upi_reward"].search(clean_msg))
    has_job = bool(PATTERNS["remote_job"].search(clean_msg))
    has_loan = bool(PATTERNS["fake_loan"].search(clean_msg))
    has_delivery = bool(PATTERNS["delivery_failure"].search(clean_msg))

    # URL danger flags
    has_apk_url = any(u["has_risky_extension"] for u in urls_data)
    has_ip_url = any(u["is_ip_address"] for u in urls_data)
    has_brand_spoof_url = any(u["is_brand_spoof"] for u in urls_data)
    has_shortener_url = any(u["is_shortener"] for u in urls_data)
    has_risky_tld = any(u["is_risky_tld"] for u in urls_data)
    has_redirect = any(u["has_redirect_param"] for u in urls_data)

    # ML Inference
    ml_prob = classifier.predict_probability(clean_msg)

    # Check for insufficient context first
    if is_insufficient_evidence(clean_msg):
        features = AnalyzedFeatures(
            message_length=len(clean_msg),
            urls_found=url_strings,
            url_details=url_findings,
            has_urgency=has_urgency,
            requests_otp_or_pin=has_otp,
            requests_payment_or_money=False,
            claims_lottery_or_prize=has_lottery,
            threatens_service_cutoff=has_cutoff,
            mentions_kyc_or_pan=has_kyc,
            offers_remote_job=has_job,
            ml_scam_probability=ml_prob
        )
        return AnalyzeResponse(
            verdict=VerdictType.INSUFFICIENT_EVIDENCE,
            verdict_label="Insufficient Information",
            confidence=None,
            risk_level=RiskLevel.UNKNOWN,
            reasons=[
                "The message is too short or vague to evaluate reliably.",
                "Scammers often provide partial instructions or follow up in subsequent messages."
            ],
            recommended_action="Paste the full message or conversation, including any sender details, links, or instructions.",
            analyzed_features=features,
            model_version=classifier.version,
            disclaimer=DISCLAIMER_TEXT
        )

    # Compile Grounded Reasons
    scam_reasons = []
    suspicious_reasons = []

    if has_otp:
        scam_reasons.append("The message attempts to solicit a one-time password (OTP), PIN, or security code. Legitimate institutions never ask you to share your OTP.")
    if has_apk_url:
        scam_reasons.append("Contains a direct link to download an Android APK application. Installing unverified APKs commonly infects phones with banking trojans.")
    if has_ip_url:
        scam_reasons.append("The link directs to a raw numerical IP address rather than a verified registered domain.")
    if has_brand_spoof_url:
        scam_reasons.append("The web link impersonates a trusted financial institution or organization using an unofficial domain name.")
    if has_cutoff and (has_urgency or url_strings or bool(re.search(r'\d{10}', clean_msg))):
        scam_reasons.append("Threatens immediate utility disconnection (electricity, power, or SIM) to force an urgent, panicky call or payment.")
    if has_lottery:
        scam_reasons.append("Claims you won a massive lottery or prize for a competition you never entered, a classic advance-fee fraud vector.")
    if has_kyc and (url_strings or has_urgency):
        scam_reasons.append("Claims your bank account or card is suspended and instructs you to submit PAN, Aadhaar, or KYC details on an external link.")
    if has_upi:
        scam_reasons.append("Promises cash rewards or cashback that requires opening a link or entering your UPI PIN (which actually debits money).")
    if has_job:
        scam_reasons.append("Promises high daily income for trivial online tasks (liking videos, giving reviews), typical of Telegram task-investment scams.")
    if has_loan:
        scam_reasons.append("Offers instant paperless loans without credit checks, a hallmark of predatory or illegal lending scams.")
    if has_delivery and (url_strings or has_urgency):
        scam_reasons.append("Claims a delivery has failed due to address issues and prompts clicking a link to pay redelivery fees.")

    # URL Heuristic Reasons
    if has_shortener_url:
        suspicious_reasons.append("Uses a link shortener (such as bit.ly or tinyurl) that conceals the true destination website.")
    if has_risky_tld:
        suspicious_reasons.append("Uses a high-risk or unusual domain extension (.xyz, .top, .buzz) frequently registered for short-lived scam campaigns.")
    if has_redirect:
        suspicious_reasons.append("Contains an open-redirect parameter that can bounce your browser to an unverified third-party webpage.")
    if has_urgency and not has_cutoff and not has_kyc:
        suspicious_reasons.append("Uses high-pressure psychological language demanding immediate action to prevent calm verification.")

    # High ML Probability reason
    if ml_prob is not None and ml_prob >= 0.70 and not scam_reasons:
        scam_reasons.append("Text patterns and phrasing closely match known fraudulent and spam messages analyzed by our AI model.")

    # Moderate ML Probability reason
    if ml_prob is not None and 0.35 <= ml_prob < 0.70 and not scam_reasons and not suspicious_reasons:
        suspicious_reasons.append("The wording displays characteristics commonly associated with promotional spam or unverified offers.")

    # Decision Matrix
    # Policy 1: Hard Scam Indicators -> LIKELY_SCAM
    if scam_reasons or (ml_prob is not None and ml_prob >= 0.75):
        verdict = VerdictType.LIKELY_SCAM
        verdict_label = "Likely Scam"
        risk_level = RiskLevel.HIGH
        # Ensure confidence represents scam probability
        confidence = ml_prob if ml_prob is not None else 0.90
        # If rules caught it but ML was lower, calibrate confidence upward to reflect rule certainty
        if scam_reasons and confidence < 0.80:
            confidence = 0.88

        reasons = scam_reasons[:3]
        if not reasons and suspicious_reasons:
            reasons = suspicious_reasons[:2]

        recommended_action = (
            "Do NOT click any links, do NOT dial any phone numbers listed in the message, and never share OTPs, "
            "passwords, or banking details. Delete the message and report the sender."
        )

    # Policy 2: Suspicious Indicators -> SUSPICIOUS
    elif suspicious_reasons or (ml_prob is not None and ml_prob >= 0.35):
        verdict = VerdictType.SUSPICIOUS
        verdict_label = "Suspicious"
        risk_level = RiskLevel.MEDIUM
        confidence = ml_prob if ml_prob is not None else 0.55

        reasons = (suspicious_reasons if suspicious_reasons else [
            "The message exhibits subtle warning signs or unsolicited promotional patterns.",
            "The sender identity cannot be verified from the message contents."
        ])[:3]

        recommended_action = (
            "Proceed with caution. Do not click links until you independently verify the sender through "
            "an official phone number or website you already trust."
        )

    # Policy 3: No scam or suspicious indicators -> LIKELY_SAFE
    else:
        verdict = VerdictType.LIKELY_SAFE
        verdict_label = "Likely Safe"
        risk_level = RiskLevel.LOW
        # Calibrated safe confidence: (1.0 - ml_prob)
        confidence = round(1.0 - (ml_prob if ml_prob is not None else 0.05), 4)

        reasons = [
            "No known scam patterns, malicious links, or credential-theft indicators were detected in this message.",
            "The language appears consistent with standard communication or legitimate transactional updates."
        ]

        recommended_action = (
            "The message appears normal. However, always exercise regular caution: never share OTPs or passwords "
            "if anyone subsequently asks for them."
        )

    features = AnalyzedFeatures(
        message_length=len(clean_msg),
        urls_found=url_strings,
        url_details=url_findings,
        has_urgency=has_urgency,
        requests_otp_or_pin=has_otp,
        requests_payment_or_money=bool(PATTERNS["upi_reward"].search(clean_msg) or PATTERNS["fake_loan"].search(clean_msg)),
        claims_lottery_or_prize=has_lottery,
        threatens_service_cutoff=has_cutoff,
        mentions_kyc_or_pan=has_kyc,
        offers_remote_job=has_job,
        ml_scam_probability=ml_prob
    )

    return AnalyzeResponse(
        verdict=verdict,
        verdict_label=verdict_label,
        confidence=confidence,
        risk_level=risk_level,
        reasons=reasons,
        recommended_action=recommended_action,
        analyzed_features=features,
        model_version=classifier.version,
        disclaimer=DISCLAIMER_TEXT
    )
