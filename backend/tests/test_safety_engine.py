"""Unit tests for safety assessment engine covering all scam categories and edge cases."""

import pytest
from backend.app.services.safety_engine import assess_safety, is_insufficient_evidence
from backend.app.schemas.analysis import VerdictType, RiskLevel

def test_otp_theft_scam():
    msg = "Bank Security: To stop fraudulent transfer of Rs 50,000, call immediately and share the OTP sent to your mobile."
    res = assess_safety(msg)
    assert res.verdict == VerdictType.LIKELY_SCAM
    assert res.risk_level == RiskLevel.HIGH
    assert any("one-time password" in r or "OTP" in r for r in res.reasons)
    assert res.analyzed_features.requests_otp_or_pin is True

def test_electricity_disconnection_scam():
    msg = "Dear consumer, your electricity will be disconnected tonight at 9:30 PM due to unpaid bill. Call officer Rahul Sharma on 9812304918 immediately."
    res = assess_safety(msg)
    assert res.verdict == VerdictType.LIKELY_SCAM
    assert res.risk_level == RiskLevel.HIGH
    assert any("disconnection" in r for r in res.reasons)
    assert res.analyzed_features.threatens_service_cutoff is True

def test_bank_kyc_suspension_scam():
    msg = "Dear customer, your SBI account is suspended today. Update your PAN card immediately at http://sbi-kyc-verify.xyz"
    res = assess_safety(msg)
    assert res.verdict == VerdictType.LIKELY_SCAM
    assert res.risk_level == RiskLevel.HIGH
    assert res.analyzed_features.mentions_kyc_or_pan is True

def test_lottery_prize_scam():
    msg = "Congratulations! You have won 25 Lakhs in KBC WhatsApp Lucky Draw. Contact KBC manager to claim your prize money."
    res = assess_safety(msg)
    assert res.verdict == VerdictType.LIKELY_SCAM
    assert res.risk_level == RiskLevel.HIGH
    assert res.analyzed_features.claims_lottery_or_prize is True

def test_apk_delivery_scam():
    msg = "Government scheme: Receive Rs 5000 in your bank. Download app: http://pm-scheme.top/app.apk"
    res = assess_safety(msg)
    assert res.verdict == VerdictType.LIKELY_SCAM
    assert res.risk_level == RiskLevel.HIGH
    assert any("APK" in r for r in res.reasons)

def test_work_from_home_task_fraud():
    msg = "Part time job: Earn Rs 4000 daily from home just by liking YouTube videos. Contact HR on Telegram @EarnJobDaily"
    res = assess_safety(msg)
    assert res.verdict == VerdictType.LIKELY_SCAM
    assert res.risk_level == RiskLevel.HIGH
    assert res.analyzed_features.offers_remote_job is True

def test_legitimate_bank_transaction():
    msg = "Your A/C ending 4921 has been debited with INR 250.00 on 10-Oct-2024 via UPI. Ref No: 42918491829. Avail bal: INR 14,210.00. - HDFC Bank"
    res = assess_safety(msg)
    assert res.verdict == VerdictType.LIKELY_SAFE
    assert res.risk_level == RiskLevel.LOW
    assert len(res.reasons) >= 1

def test_legitimate_otp_notification():
    msg = "492019 is your OTP for logging into Swiggy. Valid for 5 minutes. Do not share with anyone."
    res = assess_safety(msg)
    # The message tells user NOT to share, so requests_otp_or_pin is false
    assert res.analyzed_features.requests_otp_or_pin is False
    assert res.verdict in [VerdictType.LIKELY_SAFE, VerdictType.SUSPICIOUS]

def test_insufficient_evidence():
    short_msgs = ["Hi", "Ok", "good morning", "yes please", "hello"]
    for m in short_msgs:
        res = assess_safety(m)
        assert res.verdict == VerdictType.INSUFFICIENT_EVIDENCE
        assert res.confidence is None
        assert res.risk_level == RiskLevel.UNKNOWN

def test_suspicious_shortener():
    msg = "Special festive promotion offer: Check details at http://bit.ly/deal2024"
    res = assess_safety(msg)
    assert res.verdict in [VerdictType.SUSPICIOUS, VerdictType.LIKELY_SCAM]
    assert any("link shortener" in r for r in res.reasons)
