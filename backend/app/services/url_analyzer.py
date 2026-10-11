"""
CyberSaathi URL Risk Analysis Module.
Performs observable static lexical and structural analysis of URLs without making
outbound HTTP requests, preventing SSRF, DNS rebinding, and outbound leaks.
"""

import re
import ipaddress
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any, Optional

# Regex to safely find URLs or domain-like links inside text
URL_PATTERN = re.compile(
    r'(?:https?://|www\.)[^\s<>"\'`()]+|(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|in|co|gov|edu|xyz|top|buzz|work|click|cam|link|live|loan|site|info|biz|me|cc|io|app|ly|gd|gl|to|is|so|ae)/[^\s<>"\'`()]*',
    re.IGNORECASE
)

# Known URL shortener services
KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "is.gd", "t.co", "cutt.ly",
    "ow.ly", "rb.gy", "shorturl.at", "goo.gl", "buff.ly",
    "rebrand.ly", "tiny.cc", "t.ly", "v.gd", "soo.gd", "qr.ae"
}

# TLDs disproportionately abused in automated mass scams and phishing campaigns
RISKY_TLDS = {
    "xyz", "top", "buzz", "work", "click", "cam", "link",
    "live", "loan", "stream", "gq", "cf", "ml", "ga",
    "country", "bid", "date", "racing", "download", "win",
    "party", "trade", "accountant", "review"
}

# High-trust brand keywords commonly targeted for spoofing in India and globally
TARGETED_BRANDS = [
    "sbi", "hdfc", "icici", "pnb", "axis", "kotak", "bob", "canara",
    "paytm", "phonepe", "gpay", "googlepay", "bhim", "upi",
    "amazon", "flipkart", "meesho", "myntra", "indiapost",
    "uidai", "aadhaar", "incometax", "digilocker", "parivahan",
    "netflix", "apple", "microsoft", "whatsapp", "telegram"
]

# Risky executable or package file extensions in path
RISKY_FILE_EXTENSIONS = [
    ".apk", ".exe", ".bat", ".scr", ".cmd", ".vbs", ".msi", ".jar", ".ps1", ".reg"
]

# Open redirect query parameters
REDIRECT_PARAMS = [
    "redirect", "url", "next", "dest", "target", "return_to", "link", "goto", "out"
]

def extract_urls(text: str) -> List[str]:
    """Safely extracts candidate URLs and domain links from user text."""
    if not text:
        return []
    matches = URL_PATTERN.findall(text)
    cleaned = []
    for m in matches:
        m = m.strip(".,;:?!'\"()[]{}")
        if not m.startswith("http://") and not m.startswith("https://"):
            m = "http://" + m
        if m not in cleaned:
            cleaned.append(m)
    return cleaned

def is_ip_host(host: str) -> bool:
    """Checks if hostname is an IPv4 or IPv6 address."""
    if not host:
        return False
    # Strip port if present
    h = host.split(":")[0]
    try:
        ipaddress.ip_address(h)
        return True
    except ValueError:
        return False

def is_private_ip(host: str) -> bool:
    """Checks if IP host is within private, loopback, or link-local ranges."""
    h = host.split(":")[0]
    try:
        ip = ipaddress.ip_address(h)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        return False

def analyze_url(url: str) -> Dict[str, Any]:
    """
    Performs observable lexical analysis on a single URL.
    Returns findings without performing any outbound network connections.
    """
    risk_summary = []
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parsed.query.lower()

    # Normalize host without port
    host = netloc.split(":")[0] if ":" in netloc else netloc

    is_https = (scheme == "https")
    is_ip = is_ip_host(host)
    is_priv = is_private_ip(host) if is_ip else False

    # 1. Scheme check
    if not is_https:
        risk_summary.append("Uses unencrypted HTTP connection instead of secure HTTPS.")

    # 2. Host check: Raw IP host
    if is_ip:
        risk_summary.append(f"Uses a raw IP address ({host}) instead of an authentic domain name, a hallmark of malicious phishing sites.")
        if is_priv:
            risk_summary.append(f"The address ({host}) is a private or internal network address, which cannot be a legitimate public internet service.")

    # 3. Known URL Shortener
    is_shortener = False
    for shortener in KNOWN_SHORTENERS:
        if host == shortener or host.endswith("." + shortener):
            is_shortener = True
            risk_summary.append(f"Uses link shortener ({host}) which hides the real destination website.")
            break

    # 4. Risky or unusual TLD check
    is_risky_tld = False
    parts = host.split(".")
    if len(parts) >= 2:
        tld = parts[-1]
        if tld in RISKY_TLDS:
            is_risky_tld = True
            risk_summary.append(f"Uses the '.{tld}' domain extension, which is frequently associated with disposable scam websites.")

    # 5. Brand Spoofing / Impersonation Check
    is_brand_spoof = False
    if not is_ip:
        for brand in TARGETED_BRANDS:
            # Check if brand appears in hostname but isn't the primary legitimate domain
            if brand in host:
                # Legitimate patterns would be like sbi.co.in, onlinesbi.sbi, hdfcbank.com, amazon.in, etc.
                # A brand inside a compound domain like 'sbi-update.xyz' or 'hdfc-kyc.com' is suspicious
                legit_domains = [
                    f"{brand}.co.in", f"{brand}.com", f"{brand}.in", f"{brand}.gov.in",
                    f"{brand}bank.com", f"online{brand}.com", f"{brand}pay.in"
                ]
                is_legit = any(host == ld or host.endswith("." + ld) for ld in legit_domains)
                if not is_legit:
                    is_brand_spoof = True
                    risk_summary.append(f"Impersonates the brand name '{brand.upper()}' in an unofficial web address ({host}).")
                    break

    # 6. IDN / Punycode homograph
    if "xn--" in host:
        risk_summary.append("Uses Punycode encoded characters (xn--), which can disguise lookalike deceptive letters.")

    # 7. Excessive subdomains or unusual structure
    if len(parts) > 4:
        risk_summary.append("Contains an abnormally high number of subdomains, a technique often used to disguise fake websites.")

    # 8. Risky file downloads (APK, EXE)
    has_risky_ext = False
    for ext in RISKY_FILE_EXTENSIONS:
        if path.endswith(ext) or (ext in path):
            has_risky_ext = True
            if ext == ".apk":
                risk_summary.append("Directly points to an Android APK application package, which may install spyware or banking trojans.")
            else:
                risk_summary.append(f"Points directly to an executable file ({ext}), which may download dangerous software.")
            break

    # 9. Suspicious open redirect query parameters
    has_redirect = False
    qs = parse_qs(query)
    for rp in REDIRECT_PARAMS:
        if rp in qs:
            has_redirect = True
            risk_summary.append(f"Contains a redirect parameter ('{rp}='), which can secretly route your browser to an unverified malicious page.")
            break

    return {
        "url": url,
        "is_https": is_https,
        "is_ip_address": is_ip,
        "is_shortener": is_shortener,
        "is_risky_tld": is_risky_tld,
        "is_brand_spoof": is_brand_spoof,
        "has_risky_extension": has_risky_ext,
        "has_redirect_param": has_redirect,
        "risk_summary": risk_summary
    }

def analyze_all_urls(text: str) -> List[Dict[str, Any]]:
    """Extracts and analyzes all URLs found in the given text."""
    urls = extract_urls(text)
    return [analyze_url(u) for u in urls]
