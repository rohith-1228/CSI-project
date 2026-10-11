"""
CyberSaathi Machine Learning Classifier Wrapper.
Handles thread-safe model artifact loading, probability prediction, and metadata reporting.
"""

import os
import json
import logging
import joblib
from typing import Optional, Dict, Any

logger = logging.getLogger("cybersaathi.classifier")

class ScamClassifier:
    def __init__(self, model_path: str = "models/cybersaathi_text_classifier_v1.joblib", metadata_path: str = "models/model_metadata.json"):
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.pipeline = None
        self.metadata = {}
        self._is_loaded = False

    def _resolve_path(self, path: str) -> str:
        """Finds artifact path across project root and working directory variations."""
        if os.path.exists(path):
            return path
        # Try relative to repo root
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        candidate = os.path.join(repo_root, path)
        if os.path.exists(candidate):
            return candidate
        # Try relative to backend dir
        backend_rel = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", path))
        if os.path.exists(backend_rel):
            return backend_rel
        return path

    def load(self) -> bool:
        """Loads model pipeline and metadata from disk."""
        try:
            resolved_model = self._resolve_path(self.model_path)
            resolved_meta = self._resolve_path(self.metadata_path)

            if not os.path.exists(resolved_model):
                logger.warning(f"Model artifact not found at {self.model_path} (resolved: {resolved_model}). Fallback rule engine will be used.")
                self._is_loaded = False
                self.pipeline = None
                return False

            self.pipeline = joblib.load(resolved_model)
            self._is_loaded = True
            logger.info(f"Loaded ML model successfully from {resolved_model}")

            if os.path.exists(resolved_meta):
                with open(resolved_meta, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded model metadata version {self.metadata.get('model_version')}")
            else:
                self.metadata = {"model_version": "cybersaathi-v1.0.0-unversioned"}

            return True
        except Exception as e:
            logger.error(f"Failed to load ML model artifact: {e}", exc_info=True)
            self._is_loaded = False
            self.pipeline = None
            return False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded and self.pipeline is not None

    @property
    def version(self) -> str:
        return self.metadata.get("model_version", "cybersaathi-v1.0.0" if self.is_loaded else "rule-fallback")

    def predict_probability(self, text: str) -> Optional[float]:
        """
        Returns calibrated probability P(scam | text) in [0.0, 1.0].
        Returns None if model is unavailable.
        """
        if not self.is_loaded:
            return None

        try:
            # Minimal clean
            cleaned = " ".join(text.split()).strip()
            if not cleaned:
                return 0.0

            probs = self.pipeline.predict_proba([cleaned])[0]
            # Prob for class 1 (scam/spam)
            scam_prob = float(probs[1])
            return round(scam_prob, 4)
        except Exception as e:
            logger.error(f"Error during ML inference: {e}")
            return None

# Global singleton instance
classifier = ScamClassifier()
