# CyberSaathi Datasets Documentation

## Overview
CyberSaathi relies on legally vetted, documented datasets for training its machine-learning spam and scam detector. 

## Primary Dataset: SMS Spam Collection
- **Source**: UCI Machine Learning Repository (SMS Spam Collection Dataset)
- **Creators**: Tiago A. Almeida (Federal University of Sao Carlos) and José María Gómez Hidalgo (R&D Department, Optenet)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0) / Public Domain for Academic and Open Research
- **Reference**: Almeida, T.A., Gómez Hidalgo, J.M., Yamakami, A. (2011). Contributions to the Study of SMS Spam Filtering: New Collection and Results. In *ACM DOCEng'11*.
- **Size**: 5,574 SMS messages in English.
- **Labels**:
  - `ham` (legitimate): 4,827 messages
  - `spam` (unsolicited / fraudulent / promotional / scam): 747 messages

## Curated Modern Scam Augmentation Dataset
Because the historical UCI SMS collection primarily reflects early 2010s SMS fraud (e.g. ringtones, fake lottery claim numbers, premium call services), CyberSaathi also integrates a curated, documented dataset of 250+ modern community cyber-fraud templates (`data/modern_community_scams.json`).

These cover modern messaging vectors observed on WhatsApp, Telegram, and SMS in community contexts:
1. **Banking & KYC Scams**: "Dear customer, your SBI/HDFC/ICICI NetBanking will be suspended today. Update PAN immediately."
2. **Electricity & Utility Cutoff Scams**: "Your power will be disconnected at 9:30 PM due to unpaid bill. Call electric officer immediately."
3. **UPI / Payment Refund Scams**: "GooglePay/PhonePe reward of Rs 2,500 waiting. Click link to approve refund to bank."
4. **Lottery & KBC Fraud**: "Congratulations! You have won Kaun Banega Crorepati WhatsApp lottery worth 25 Lakhs."
5. **Malicious APK Delivery**: "Download PM Yojana app APK to claim financial benefit."
6. **Work-From-Home / Task Fraud**: "Earn 5,000 daily by liking YouTube videos. Telegram manager now."
7. **Couriers & Package Delivery**: "Your India Post parcel cannot be delivered due to wrong address. Update here."

## Preprocessing & Data Hygiene
- Messages are normalized: text lowercasing, whitespace trimming, stripping non-printable characters.
- Synthetic and benchmark sets are combined with clear provenance tags.
- Duplicates are removed.
- Train / Test split is performed with stratification (`random_state=42`, 80% train, 20% test) to prevent data leakage.
