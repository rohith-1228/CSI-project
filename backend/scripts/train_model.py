"""
CyberSaathi Model Training and Evaluation Pipeline.
Reproducibly trains and evaluates the TF-IDF + Calibrated Classifier
on the benchmark UCI SMS dataset augmented with modern community scam templates.
"""

import os
import json
import datetime
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    classification_report
)

def load_data(uci_path="data/sms_spam_uci.tsv", modern_path="data/modern_community_scams.json"):
    records = []

    # 1. Load UCI SMS dataset
    if os.path.exists(uci_path):
        df_uci = pd.read_csv(uci_path, sep="\t", header=None, names=["label", "text"], quoting=3)
        # Drop NaN or empty
        df_uci = df_uci.dropna().drop_duplicates(subset=["text"])
        for _, row in df_uci.iterrows():
            lbl = str(row["label"]).strip().lower()
            if lbl in ["ham", "spam"]:
                records.append({
                    "text": str(row["text"]).strip(),
                    "label": lbl,
                    "source": "uci_sms_collection"
                })
        print(f"Loaded {len(records)} valid examples from {uci_path}")
    else:
        print(f"Warning: {uci_path} not found.")

    # 2. Load modern community examples
    if os.path.exists(modern_path):
        with open(modern_path, "r", encoding="utf-8") as f:
            modern_data = json.load(f)
        for item in modern_data:
            records.append({
                "text": str(item["text"]).strip(),
                "label": str(item["label"]).strip().lower(),
                "source": "modern_community_scams"
            })
        print(f"Loaded {len(modern_data)} examples from {modern_path}")
    else:
        print(f"Warning: {modern_path} not found.")

    df = pd.DataFrame(records)
    # Deduplicate while preserving order
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)
    return df

def clean_text(text: str) -> str:
    """Minimal text normalization preserving signal like currency & links."""
    if not isinstance(text, str):
        return ""
    # Normalize whitespaces
    text = " ".join(text.split())
    return text.strip()

def build_model_pipeline():
    """Builds a dual-feature (word + char n-gram) TF-IDF feature union with calibrated classifier."""
    word_vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        max_features=10000,
        sublinear_tf=True,
        min_df=2
    )

    char_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        max_features=15000,
        sublinear_tf=True,
        min_df=2
    )

    features = FeatureUnion([
        ("word_tfidf", word_vectorizer),
        ("char_tfidf", char_vectorizer)
    ])

    base_clf = LogisticRegression(
        C=2.0,
        class_weight="balanced",
        max_iter=1000,
        random_state=42,
        solver="lbfgs"
    )

    # Calibrate probabilities using 5-fold cross-validation
    calibrated_clf = CalibratedClassifierCV(
        estimator=base_clf,
        method="sigmoid",
        cv=5
    )

    pipeline = Pipeline([
        ("features", features),
        ("classifier", calibrated_clf)
    ])

    return pipeline

def train_and_evaluate():
    print("=" * 60)
    print("CyberSaathi: Training ML Text Classifier")
    print("=" * 60)

    df = load_data()
    print(f"Total dataset size: {len(df)} samples")
    print("Class distribution:\n", df["label"].value_counts())

    # Map labels: ham -> 0 (Safe), spam -> 1 (Scam/Spam)
    y_list = [0 if lbl == "ham" else 1 for lbl in df["label"].tolist()]
    X_list = [clean_text(t) for t in df["text"].tolist()]
    y = np.array(y_list, dtype=np.int32)
    X = np.array(X_list, dtype=object)

    # Stratified 80/20 train/test split with seed 42 to prevent data leakage
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(f"\nTrain set: {len(X_train)} samples ({sum(y_train)} spam / {len(y_train) - sum(y_train)} ham)")
    print(f"Test set:  {len(X_test)} samples ({sum(y_test)} spam / {len(y_test) - sum(y_test)} ham)")

    pipeline = build_model_pipeline()
    print("\nFitting TF-IDF FeatureUnion and Calibrated Classifier on training data...")
    pipeline.fit(X_train, y_train)
    print("Training complete!")

    # Evaluate on held-out test set
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)

    precision = float(precision_score(y_test, y_pred, pos_label=1))
    recall = float(recall_score(y_test, y_pred, pos_label=1))
    f1 = float(f1_score(y_test, y_pred, pos_label=1))
    roc_auc = float(roc_auc_score(y_test, y_pred_proba))
    pr_auc = float(average_precision_score(y_test, y_pred_proba))

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = [int(val) for val in cm.ravel()]
    false_negative_rate = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0
    false_positive_rate = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    print("\n" + "=" * 40)
    print("EVALUATION RESULTS ON TEST SET (Held-Out 20%)")
    print("=" * 40)
    print(f"Precision (Spam/Scam):   {precision:.4f} ({precision * 100:.2f}%)")
    print(f"Recall (Spam/Scam):      {recall:.4f} ({recall * 100:.2f}%)")
    print(f"F1-Score:                {f1:.4f}")
    print(f"ROC-AUC:                 {roc_auc:.4f}")
    print(f"PR-AUC:                  {pr_auc:.4f}")
    print(f"False Negative Rate:     {false_negative_rate:.4f} ({fn} missed scams out of {fn + tp})")
    print(f"False Positive Rate:     {false_positive_rate:.4f} ({fp} false alarms out of {fp + tn})")
    print("\nConfusion Matrix:")
    print(f"  True Negatives (Ham as Safe):  {tn}")
    print(f"  False Positives (Ham as Scam): {fp}")
    print(f"  False Negatives (Scam as Safe): {fn}")
    print(f"  True Positives (Scam as Scam): {tp}")

    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Ham / Safe", "Spam / Scam"], digits=4))

    # Save artifacts
    os.makedirs("models", exist_ok=True)
    model_path = "models/cybersaathi_text_classifier_v1.joblib"
    joblib.dump(pipeline, model_path, compress=3)
    print(f"\nModel artifact saved to {model_path} ({os.path.getsize(model_path) / 1024:.1f} KB)")

    metadata = {
        "model_name": "CyberSaathi Calibrated Text Classifier",
        "model_version": "cybersaathi-v1.0.0",
        "trained_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "algorithm": "LogisticRegression (calibrated via CalibratedClassifierCV sigmoid)",
        "features": {
            "word_tfidf": "ngram_range=(1,2), max_features=10000, sublinear_tf=True",
            "char_tfidf": "char_wb, ngram_range=(3,5), max_features=15000, sublinear_tf=True"
        },
        "dataset": {
            "primary": "UCI SMS Spam Collection (5,572 rows, CC BY 4.0)",
            "supplementary": "Modern community cyber fraud templates (54 rows)",
            "total_samples": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "split_ratio": "80/20 stratified"
        },
        "metrics": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "false_negative_rate": round(false_negative_rate, 4),
            "false_positive_rate": round(false_positive_rate, 4),
            "confusion_matrix": {
                "true_negative": tn,
                "false_positive": fp,
                "false_negative": fn,
                "true_positive": tp
            }
        },
        "thresholds": {
            "scam_threshold": 0.65,
            "suspicious_threshold": 0.35
        },
        "limitations": [
            "Evaluates text and lexical content; does not perform active network probes.",
            "Heavily targeted personalized social engineering without explicit scam triggers may have lower confidence.",
            "Relies on plain English and common transliterated scam idioms."
        ]
    }

    meta_path = "models/model_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Model metadata saved to {meta_path}")

    # Sanity test predictions
    test_cases = [
        "Hey are we still having lunch at 1pm?",
        "Your SBI NetBanking is suspended. Update PAN at http://sbi-kyc.xyz or account blocked",
        "Electricity will be cut off at 9:30 PM. Call Rahul Sharma immediately",
        "Congratulations you won 25 Lakhs in KBC lucky draw. Send your details",
        "Your Amazon OTP is 491024 for logging in. Do not share with anyone."
    ]
    print("\n--- SANITY TEST RUN ---")
    for t in test_cases:
        p = float(pipeline.predict_proba([clean_text(t)])[0][1])
        lbl = "SCAM" if p >= 0.65 else ("SUSPICIOUS" if p >= 0.35 else "SAFE")
        print(f"[{lbl:10s} | Prob={p:.3f}] {t}")

if __name__ == "__main__":
    train_and_evaluate()
