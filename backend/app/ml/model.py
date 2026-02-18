"""
LSTM Model loader and manager (LSP)
- Loads model from settings.ML_MODEL_PATH
- Loads vocabulary from etiquetas.json (your trained classes)
"""

import os
import json
import numpy as np
from typing import Optional, Dict, List

from app.config import settings
from app.utils.logger import log_info, log_warning, log_error

try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    log_warning("TensorFlow not available. Predictions will run in fallback mode.")


class LSPModel:
    """LSTM Model for LSP (Lengua de Señas Peruana) recognition"""

    def __init__(self):
        self.model: Optional["keras.Model"] = None
        self.vocabulary: List[str] = self._load_vocabulary_from_labels()
        self.is_loaded = False

        # Only load the keras model if allowed and TF exists
        if not settings.ML_DEMO_MODE and TENSORFLOW_AVAILABLE:
            self._load_model()
        else:
            # If demo mode is ON, keep behavior safe: vocabulary still your 10 words
            if settings.ML_DEMO_MODE:
                log_warning("ML_DEMO_MODE=True. Returning fallback predictions (UNKNOWN) unless you change it.")
            if not TENSORFLOW_AVAILABLE:
                log_warning("TensorFlow not installed. Returning fallback predictions (UNKNOWN).")

    def _labels_path(self) -> str:
        # If you don't have ML_LABELS_PATH in settings, fallback to app/ml/models/etiquetas.json
        return getattr(settings, "ML_LABELS_PATH", os.path.join("app", "ml", "models", "etiquetas.json"))

    def _load_vocabulary_from_labels(self) -> List[str]:
        """
        Load vocabulary from etiquetas.json produced by training.
        Expected format:
        {
          "palabras": ["SABER", ...],
          "indice_a_palabra": {...}
        }
        """
        path = self._labels_path()
        if not os.path.exists(path):
            log_warning(f"Labels file not found at {path}. Using minimal vocabulary ['UNKNOWN'].")
            return ["UNKNOWN"]

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            words = data.get("palabras") or []
            words = [str(w).strip() for w in words if str(w).strip()]

            # Ensure UNIQUE + stable order
            seen = set()
            vocab = []
            for w in words:
                if w not in seen:
                    vocab.append(w)
                    seen.add(w)

            # Always keep UNKNOWN as fallback class (not part of your model output)
            if "UNKNOWN" not in vocab:
                vocab.append("UNKNOWN")

            log_info(f"Loaded vocabulary from labels: {vocab}")
            return vocab

        except Exception as e:
            log_error(f"Error reading labels file: {e}", exc_info=True)
            return ["UNKNOWN"]

    def _load_model(self):
        model_path = settings.ML_MODEL_PATH

        if not os.path.exists(model_path):
            log_warning(f"Model file not found at {model_path}. Predictions will return UNKNOWN.")
            return

        try:
            self.model = keras.models.load_model(model_path)
            self.is_loaded = True
            log_info(f"LSP model loaded successfully from {model_path}")

            # Optional sanity check: output classes vs vocab without UNKNOWN
            out_dim = int(self.model.output_shape[-1])
            vocab_no_unknown = [w for w in self.vocabulary if w != "UNKNOWN"]
            if out_dim != len(vocab_no_unknown):
                log_warning(
                    f"⚠️ Model output dim ({out_dim}) != vocab size ({len(vocab_no_unknown)}). "
                    f"Check that etiquetas.json matches the trained model."
                )

        except Exception as e:
            log_error(f"Error loading model: {str(e)}", exc_info=True)
            log_warning("Predictions will return UNKNOWN.")
            self.model = None
            self.is_loaded = False

    def predict(self, sequence: np.ndarray, return_top_k: int = 3) -> Dict:
        """
        Predict sign language word from feature sequence.

        sequence: (sequence_length, feature_dim)
        returns:
          { label, confidence, alternatives }
        """
        # Safe fallback (NO random words)
        if settings.ML_DEMO_MODE or (not self.is_loaded) or (self.model is None):
            return self._predict_fallback(return_top_k=return_top_k)

        try:
            sequence_batch = np.expand_dims(sequence, axis=0)  # (1, T, D)
            predictions = self.model.predict(sequence_batch, verbose=0)[0]  # (C,)

            vocab_no_unknown = [w for w in self.vocabulary if w != "UNKNOWN"]

            # Guard if mismatch
            c = min(len(predictions), len(vocab_no_unknown))
            preds = predictions[:c]
            vocab_used = vocab_no_unknown[:c]

            top_k_indices = np.argsort(preds)[-return_top_k:][::-1]

            results = [{"label": vocab_used[idx], "confidence": float(preds[idx])} for idx in top_k_indices]

            return {
                "label": results[0]["label"],
                "confidence": results[0]["confidence"],
                "alternatives": results[1:] if len(results) > 1 else []
            }

        except Exception as e:
            log_error(f"Error during prediction: {str(e)}", exc_info=True)
            return self._predict_fallback(return_top_k=return_top_k)

    def _predict_fallback(self, return_top_k: int = 3) -> Dict:
        """
        Fallback that NEVER invents labels outside your etiquetas.json.
        """
        # Return UNKNOWN with low confidence
        alts = []
        return {
            "label": "UNKNOWN",
            "confidence": 0.0,
            "alternatives": alts
        }

    def get_vocabulary(self) -> List[str]:
        return [w for w in self.vocabulary if w != "UNKNOWN"]


_model_instance: Optional[LSPModel] = None


def get_model() -> LSPModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = LSPModel()
    return _model_instance
