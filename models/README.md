# CyberSaathi Machine Learning Models

## Model Artifacts
- **Primary Model**: `cybersaathi_text_classifier_v1.joblib`
- **Metadata Specification**: `model_metadata.json`

## Model Architecture
The text classification pipeline is composed of:
1. **Preprocessor**: Text normalizer (lowercase, stripping control characters, whitespace consolidation, token marker tags for URLs, currency symbols, and phone numbers).
2. **Feature Extractor**:
   - `FeatureUnion` of:
     - **Word-level TF-IDF**: `ngram_range=(1, 2)`, `max_features=12000`, sublinear TF scaling.
     - **Character-level TF-IDF**: `ngram_range=(3, 5)`, `max_features=18000`, capturing obfuscations, typo tricks, and unusual prefixes.
3. **Classifier**:
   - `CalibratedClassifierCV` wrapping `LogisticRegression(class_weight='balanced', C=1.5, max_iter=1000)` or `LinearSVC`.
   - Produces well-calibrated posterior probabilities `P(scam|text)`.

## Evaluation Criteria
- **Precision**: Minimizes false positives so legitimate messages are not wrongly flagged.
- **Recall**: Maximizes detection of real scam threats.
- **False Negative Rate**: Kept as low as possible for critical scam categories.
- **Explainability**: Important feature weights and decision thresholds are audited and surfaced.

## Safety Fallback Policy
If the model file is absent or corrupted, the system falls back to the deterministic rule and regex engine with clear disclosure in the API response `model_version: "fallback-rule-engine"`.
Never does the system return fabricated scores or crash silently.
