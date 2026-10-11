# CyberSaathi — AI-Powered Community Cyber Safety Platform

> **"Think before you click."**  
> A public-service, privacy-first cybersecurity awareness web platform designed to help ordinary citizens, seniors, and non-technical users spot scam messages, phishing links, fraudulent offers, and cyber threats.

---

## 1. Product Vision & Architecture

CyberSaathi addresses the rampant rise of cyber-fraud in SMS, WhatsApp, Telegram, and email communications. Many community members lack the technical literacy to distinguish authentic bank notices or utility messages from deceptive phishing campaigns.

### The 5-Second User Journey:
1. **Open the website**: Clean, calm, public-service interface without logins or clutter.
2. **Paste the suspicious message or link**: Large accessible text area with real-time character counter.
3. **Press "Check Safety"**: Clear primary button.
4. **Receive a grounded verdict**:
   - `LIKELY SAFE` (No known threat indicators detected; caution advised)
   - `SUSPICIOUS` (Subtle warning signs; independent verification required)
   - `LIKELY SCAM` (Strong fraud indicators detected; avoid links/payments/OTPs)
   - `INSUFFICIENT INFORMATION` (Text is too brief or ambiguous to reliably determine)
5. **Take immediate action**: Plain-English "What should you do next?" guidance.

### System Architecture
```
┌────────────────────────────────────────────────────────┐
│             Frontend (React 19 + Vite + TypeScript)    │
│ - Tailwind CSS restrained public-service design system │
│ - WCAG AA accessible contrast, keyboard navigation    │
│ - Zero-retention: messages never stored in browser     │
└───────────────────────────┬────────────────────────────┘
                            │ POST /api/v1/analyze
                            ▼
┌────────────────────────────────────────────────────────┐
│             FastAPI Backend Application                │
│ - Pydantic request validation & strict size limits    │
│ - Sliding-window rate limiter (60 req/min/IP)          │
│ - Log sanitization (redacts OTPs, phones, cards)       │
│ - Security headers: CSP, X-Frame-Options, nosniff      │
└─────────────┬──────────────────────────┬───────────────┘
              │                          │
              ▼                          ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│  Text ML Pipeline         │ │  Static URL Analyzer     │
│ - Scikit-learn Pipeline   │ │ - Lexical & TLD checks   │
│ - Word & Char TF-IDF      │ │ - IP host & shorteners   │
│ - Calibrated Classifier   │ │ - Brand spoofing alerts  │
│ - Trained on UCI SMS +    │ │ - SSRF-safe (No outbound │
│   Modern Scam templates   │ │   arbitrary HTTP calls)  │
└─────────────┬─────────────┘ └────────────┬─────────────┘
              │                            │
              ▼                            ▼
┌────────────────────────────────────────────────────────┐
│             Unified Safety Assessment Engine           │
│ - Combines ML probabilities & URL signals              │
│ - Hard Scam Rules (OTP theft, APK links, KYC threats)  │
│ - Grounded Explainability & Actionable Advice          │
└────────────────────────────────────────────────────────┘
```

---

## 2. Machine Learning & Detection Pipeline

### Dataset Source & Licensing
1. **Primary Corpus**: **UCI SMS Spam Collection Dataset**
   - **Authors**: Tiago A. Almeida and José María Gómez Hidalgo (*ACM DOCEng'11*).
   - **License**: Public Domain / Creative Commons Attribution 4.0 International (CC BY 4.0).
   - **Samples**: 5,171 valid deduplicated SMS messages (4,537 legitimate 'ham', 634 spam/scam).
2. **Modern Community Augmentation**:
   - **Samples**: 54 documented, realistic modern threat templates in `data/modern_community_scams.json` covering:
     - Electricity / Power bill disconnection urgency ("power cutoff tonight at 9:30 PM")
     - Bank KYC / PAN card account suspension links
     - UPI cashback / PhonePe reward scratch card traps
     - Fake courier / India Post address update phishing
     - Malicious Android `.apk` downloads
     - Work-from-home Telegram video-liking task fraud
     - KBC WhatsApp lottery scams

### Model Preprocessing & Features
- **Word-level TF-IDF**: `ngram_range=(1, 2)`, `max_features=10000`, sublinear term frequency.
- **Character-level TF-IDF**: `ngram_range=(3, 5)`, `max_features=15000` on word boundaries (`char_wb`) to detect character substitutions, typosquatting, and adversarial obfuscations (`s!bi`, `w1nner`).
- **Feature Union**: Combined 25,000-dimensional sparse feature representation.

### Classifier & Calibration
- **Algorithm**: `LogisticRegression(class_weight='balanced', C=2.0, max_iter=1000)`
- **Calibration**: Wrapped in `CalibratedClassifierCV(method='sigmoid', cv=5)` to yield true, well-calibrated posterior probabilities $P(\text{scam} \mid \text{text})$ instead of raw uncalibrated margins.

### Evaluation Metrics (Evaluated on Held-Out 20% Stratified Test Split)
| Metric | Value | Meaning |
|---|---|---|
| **Precision (Scam)** | **95.62%** | Low false positive rate (legitimate messages rarely misclassified) |
| **Recall (Scam)** | **97.04%** | Captures 97 out of 100 fraudulent attempts |
| **F1-Score** | **0.9632** | Harmonic mean of precision and recall |
| **ROC-AUC** | **0.9975** | Near-optimal ranking capability |
| **PR-AUC** | **0.9901** | High precision across all recall thresholds |
| **False Negative Rate** | **2.96%** | Critical metric: only 4 missed scams out of 135 in held-out test data |
| **False Positive Rate** | **0.66%** | Only 6 false alarms out of 908 legitimate ham messages |

### Static URL Risk Analysis (SSRF-Safe)
The URL module analyzes observable lexical features **without making outbound network connections**, completely eliminating Server-Side Request Forgery (SSRF) and DNS rebinding risks:
- Scheme verification (HTTP vs. HTTPS)
- Raw IP address hosts (including RFC 1918 / loopback / documentation IP addresses)
- Known URL shortener services (`bit.ly`, `tinyurl.com`, `is.gd`, `t.co`, `cutt.ly`, etc.)
- High-risk TLDs disproportionately abused in mass spam (`.xyz`, `.top`, `.buzz`, `.click`, `.cam`, `.link`, `.live`, `.loan`, `.stream`)
- Brand impersonation (detects trusted financial keywords like `sbi`, `hdfc`, `paytm`, `indiapost` embedded inside foreign domains)
- Executable or Android package downloads (`.apk`, `.exe`, `.bat`)
- Open redirect parameters (`?redirect=`, `?url=`, `?next=`)

---

## 3. Project Directory Structure

```
cybersaathi/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── endpoints.py          # /api/v1/analyze & /api/v1/info
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Pydantic v2 application settings
│   │   │   └── security.py           # Rate limiting & log redaction
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   └── classifier.py         # Model loader & inference wrapper
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── analysis.py           # Request & response validation schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── safety_engine.py      # Unified decision policy engine
│   │   │   └── url_analyzer.py       # SSRF-safe static URL parser
│   │   ├── __init__.py
│   │   └── main.py                   # FastAPI app with health & ready probes
│   ├── scripts/
│   │   └── train_model.py            # Reproducible training & evaluation pipeline
│   ├── tests/
│   │   ├── test_api.py               # End-to-end API integration tests
│   │   ├── test_safety_engine.py     # Scam rules & edge-case tests
│   │   └── test_url_analyzer.py      # Lexical URL analyzer tests
│   ├── Dockerfile                    # Production backend container definition
│   ├── render.yaml                   # Render deployment configuration
│   └── requirements.txt              # Pinned backend dependencies
├── data/
│   ├── sms_spam_uci.tsv              # UCI SMS Spam Collection dataset
│   ├── modern_community_scams.json   # Curated community cyber threat templates
│   ├── generate_modern_dataset.py    # Script to regenerate modern templates
│   └── README.md                     # Dataset provenance & license documentation
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Footer.tsx            # Community mission & privacy notice
│   │   │   ├── Header.tsx            # Sticky brand header & navigation
│   │   │   ├── Hero.tsx              # Introductory hero banner
│   │   │   ├── HowItWorks.tsx        # 3-step explanation guide
│   │   │   ├── ResultPanel.tsx       # Verdict, reasons & actionable guidance
│   │   │   ├── SafetyChecker.tsx     # Main checker, samples, & character counter
│   │   │   └── SafetyTips.tsx        # 5 practical golden cyber safety tips
│   │   ├── services/
│   │   │   └── api.ts                # Frontend API client with timeouts & retry
│   │   ├── tests/
│   │   │   └── checker.test.tsx      # Vitest & Testing Library tests
│   │   ├── types/
│   │   │   └── api.ts                # TypeScript interfaces
│   │   ├── App.tsx                   # Main application assembly
│   │   ├── index.css                 # Tailwind CSS styling & accessible focus
│   │   ├── main.tsx                  # React DOM mount point
│   │   └── setupTests.ts             # Vitest test setup & polyfills
│   ├── Dockerfile                    # Production frontend container
│   ├── nginx.conf                    # Nginx web server configuration
│   ├── package.json                  # Frontend scripts & dependencies
│   ├── postcss.config.js             # PostCSS plugins
│   ├── tailwind.config.js            # Tailwind color system & typography
│   ├── tsconfig.json                 # TypeScript project configuration
│   ├── vercel.json                   # Vercel deployment configuration
│   └── vite.config.ts                # Vite & Vitest configuration
├── models/
│   ├── cybersaathi_text_classifier_v1.joblib # Trained scikit-learn model artifact
│   ├── model_metadata.json           # Model configuration, metrics, & thresholds
│   └── README.md                     # Model architecture documentation
├── .env.example                      # Environment variables reference
├── .gitignore                        # Git exclusion rules
├── docker-compose.yml                # Unified multi-service local container runner
└── README.md                         # Project documentation
```

---

## 4. Quick Start & Local Execution

### Prerequisites
- **Python**: 3.10+ (tested on Python 3.11)
- **Node.js**: 18+ (tested on Node v24)
- **npm**: 9+

---

### Step 1: Backend Setup & Execution

1. Open a terminal in the project root:
   ```bash
   # Install dependencies
   pip install -r backend/requirements.txt
   ```

2. (Optional) Re-train the model from scratch:
   ```bash
   python backend/scripts/train_model.py
   ```

3. Run the backend tests:
   ```bash
   python -m pytest backend/tests -v
   ```

4. Start the FastAPI development server:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. The API is now live:
   - **Interactive API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **Liveness Probe**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
   - **Readiness Probe**: [http://127.0.0.1:8000/ready](http://127.0.0.1:8000/ready)

---

### Step 2: Frontend Setup & Execution

1. Open a second terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   npm install
   ```

2. Run the frontend tests:
   ```bash
   npm run test
   ```

3. Run the production build validation:
   ```bash
   npm run build
   ```

4. Start the local Vite development server:
   ```bash
   npm run dev
   ```

5. Open your browser at [http://127.0.0.1:5173](http://127.0.0.1:5173).

---

### Step 3: Run with Docker Compose (One-Click)

To run both services simultaneously in containers:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

---

## 5. API Documentation

### Primary Endpoint: `POST /api/v1/analyze`

#### Request Body
```json
{
  "message": "Dear customer, your SBI NetBanking account is suspended today due to KYC pending. Update immediately at http://sbi-kyc-verify.xyz"
}
```

#### Response Body (`200 OK`)
```json
{
  "verdict": "likely_scam",
  "verdict_label": "Likely Scam",
  "confidence": 0.9852,
  "risk_level": "high",
  "reasons": [
    "The web link impersonates a trusted financial institution or organization using an unofficial domain name.",
    "Claims your bank account or card is suspended and instructs you to submit PAN, Aadhaar, or KYC details on an external link."
  ],
  "recommended_action": "Do NOT click any links, do NOT dial any phone numbers listed in the message, and never share OTPs, passwords, or banking details. Delete the message and report the sender.",
  "analyzed_features": {
    "message_length": 133,
    "urls_found": ["http://sbi-kyc-verify.xyz"],
    "url_details": [
      {
        "url": "http://sbi-kyc-verify.xyz",
        "is_https": false,
        "is_ip_address": false,
        "is_shortener": false,
        "is_risky_tld": true,
        "is_brand_spoof": true,
        "has_risky_extension": false,
        "has_redirect_param": false,
        "risk_summary": [
          "Uses unencrypted HTTP connection instead of secure HTTPS.",
          "Uses the '.xyz' domain extension, which is frequently associated with disposable scam websites.",
          "Impersonates the brand name 'SBI' in an unofficial web address (sbi-kyc-verify.xyz)."
        ]
      }
    ],
    "has_urgency": true,
    "requests_otp_or_pin": false,
    "requests_payment_or_money": false,
    "claims_lottery_or_prize": false,
    "threatens_service_cutoff": false,
    "mentions_kyc_or_pan": true,
    "offers_remote_job": false,
    "ml_scam_probability": 0.9852
  },
  "model_version": "cybersaathi-v1.0.0",
  "disclaimer": "CyberSaathi provides automated safety analysis based on machine learning and known threat patterns. Automated detection cannot provide a 100% guarantee of safety. When in doubt, always verify directly with the official organization using contact information from their genuine website or official app."
}
```

---

## 6. Privacy & Security Guarantees

1. **Zero-Retention Architecture**:
   - Submitted messages are processed transiently in server memory and discarded immediately.
   - No database, Redis cache, or disk storage stores the user message.
2. **PII Masking in Logs**:
   - Internal logging never records submitted text.
   - Logs only capture operational metrics (e.g., `client_ip=127.0.0.1, length=113, verdict=likely_scam`).
   - Built-in redaction masks any inadvertent OTPs, phone numbers, or credit card sequences.
3. **SSRF & Outbound Protection**:
   - The backend **never performs arbitrary outbound HTTP requests** to user-supplied URLs.
   - Prevents SSRF attacks against internal infrastructure or cloud metadata endpoints (`169.254.169.254`).
4. **Rate Limiting**:
   - Sliding-window limiter restricts abuse to 60 requests/minute per IP.
5. **Security Headers**:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `X-XSS-Protection: 1; mode=block`
   - `Referrer-Policy: strict-origin-when-cross-origin`

---

## 7. Production Deployment Guides

### Frontend Deployment (Vercel)
1. Push repository to GitHub/GitLab.
2. Import project into Vercel and select root directory `frontend/`.
3. Set environment variable:
   - `VITE_API_BASE_URL`: `https://your-backend-service.onrender.com`
4. Deploy. The included `frontend/vercel.json` ensures client-side routing rewrites are handled seamlessly.

### Backend Deployment (Render)
1. Create a new **Web Service** on Render pointing to your repository.
2. Select **Python** runtime with the configuration defined in `backend/render.yaml`:
   - **Build Command**: `pip install -r backend/requirements.txt && python backend/scripts/train_model.py`
   - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
3. Set environment variables:
   - `ENVIRONMENT`: `production`
   - `CORS_ORIGINS`: `https://your-frontend-domain.vercel.app`
   - `RATE_LIMIT_PER_MINUTE`: `60`
   - `MODEL_PATH`: `models/cybersaathi_text_classifier_v1.joblib`
   - `MODEL_METADATA_PATH`: `models/model_metadata.json`

---

## 8. Automated Test Summary

### Backend Tests (`pytest backend/tests -v`):
- **30 / 30 tests passing (100%)**
- Execution time: ~1.5 seconds
- Coverage:
  - Input validation (empty, whitespace, 5000+ char limit)
  - Obvious phishing, bank KYC threats, electricity disconnections
  - OTP theft detection & pin requests
  - UPI cashback & scratch card lures
  - Android `.apk` delivery traps
  - Genuine transactional SMS & legitimate OTP delivery notices
  - Shortened URLs, IPv4/IPv6 hosts, brand spoofing heuristics
  - Rate limiting (429 Too Many Requests)
  - Security headers & CORS preflight
  - Health & readiness probes

### Frontend Tests (`vitest run`):
- **6 / 6 tests passing (100%)**
- Execution time: ~3.5 seconds
- Coverage:
  - Component rendering (Header, Hero, Checker, How It Works, Safety Tips, Footer)
  - Form validation & disabled state handling
  - Sample button selection
  - Real-time `LIKELY SCAM` verdict presentation with reasons and advice
  - Real-time `LIKELY SAFE` verdict presentation
  - Error alert & server failure guidance

---

## 9. Limitations & Future Roadmap

- **Active Network Reputation**: Future releases will add optional opt-in lookup with official threat feeds (e.g. Google Safe Browsing / VirusTotal) with user consent.
- **Multilingual Support**: Expanding dialect coverage to Hindi, Tamil, Telugu, Bengali, and Marathi scam templates.
- **Image / Screenshot OCR**: Allowing users to upload screenshots of WhatsApp conversations for direct image-based scam recognition.

---

## 10. License & Credits
- **Primary SMS Dataset**: UCI Machine Learning Repository (CC BY 4.0).
- **Icons**: [Lucide React](https://lucide.dev/).
- **Project**: Open-source community safety project under the MIT License.
