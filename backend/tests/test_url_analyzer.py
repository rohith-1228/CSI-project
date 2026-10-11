"""Unit tests for CyberSaathi URL analysis engine."""

import pytest
from backend.app.services.url_analyzer import extract_urls, analyze_url, is_ip_host, is_private_ip

def test_extract_urls_multiple():
    text = "Check this site http://example.com/verify and also https://secure.bank.org/test"
    urls = extract_urls(text)
    assert len(urls) == 2
    assert "http://example.com/verify" in urls
    assert "https://secure.bank.org/test" in urls

def test_extract_urls_no_scheme():
    text = "Visit bit.ly/3x9abc for details"
    urls = extract_urls(text)
    assert len(urls) >= 1
    assert any("bit.ly" in u for u in urls)

def test_ip_address_analysis():
    # Public IP
    res_pub = analyze_url("http://198.51.100.25/login")
    assert res_pub["is_ip_address"] is True
    assert any("raw IP address" in s for s in res_pub["risk_summary"])

    # Private IP
    res_priv = analyze_url("http://192.168.1.1/admin")
    assert res_priv["is_ip_address"] is True
    assert any("private or internal" in s for s in res_priv["risk_summary"])

def test_url_shortener_detection():
    res = analyze_url("https://bit.ly/claim-prize")
    assert res["is_shortener"] is True
    assert any("link shortener" in s for s in res["risk_summary"])

def test_risky_tld_detection():
    res = analyze_url("http://banking-update.xyz/login")
    assert res["is_risky_tld"] is True
    assert any(".xyz" in s for s in res["risk_summary"])

def test_brand_spoofing_detection():
    res = analyze_url("http://sbi-verification-secure.com/pan")
    assert res["is_brand_spoof"] is True
    assert any("SBI" in s for s in res["risk_summary"])

def test_apk_extension_detection():
    res = analyze_url("https://pm-yojana-funds.top/download/app.apk")
    assert res["has_risky_extension"] is True
    assert any("Android APK" in s for s in res["risk_summary"])

def test_redirect_parameter_detection():
    res = analyze_url("https://tracker.example.com/jump?redirect=http://malicious.site")
    assert res["has_redirect_param"] is True
    assert any("redirect parameter" in s for s in res["risk_summary"])

def test_safe_legitimate_url():
    res = analyze_url("https://www.wikipedia.org/wiki/Computer_security")
    assert res["is_https"] is True
    assert res["is_ip_address"] is False
    assert res["is_shortener"] is False
    assert res["is_risky_tld"] is False
    assert res["is_brand_spoof"] is False
    assert res["has_risky_extension"] is False
    assert len(res["risk_summary"]) == 0
