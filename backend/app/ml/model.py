"""
LSTM Model loader and manager
"""
import os
import numpy as np
from typing import Optional, Dict, List
from app.config import settings
from app.utils.logger import log_info, log_warning, log_error

# Try to import tensorflow, but handle gracefully if not available
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    log_warning("TensorFlow not available. Running in demo mode.")


class LSPModel:
    """LSTM Model for LSP (Lengua de Señas Peruana) recognition"""
    
    def __init__(self):
        """Initialize the LSP model"""
        self.model: Optional[keras.Model] = None
        self.vocabulary: List[str] = self._load_vocabulary()
        self.is_loaded = False
        
        if not settings.ML_DEMO_MODE and TENSORFLOW_AVAILABLE:
            self._load_model()
    
    def _load_vocabulary(self) -> List[str]:
        """
        Load vocabulary (available sign words/classes)
        
        Returns:
            List of available words
        """
        # MVP vocabulary - limited to common service desk interactions
        vocabulary = [
            "DNI", "CITA", "PAGO", "RECLAMO", "CONSULTA",
            "NOMBRE", "FECHA", "MONTO", "VENCIDO", "PERDIDO",
            "RENOVAR", "EMERGENCIA", "AYUDA", "GRACIAS", "SI",
            "NO", "HOLA", "ADIOS", "ESPERAR", "FIRMAR",
            "DOCUMENTO", "CARNET", "DINERO", "TARJETA", "EFECTIVO",
            "BANCO", "CUENTA", "DEPOSITO", "RETIRO", "TRAMITE",
            "CERTIFICADO", "CONSTANCIA", "REGISTRO", "TURNO", "NUMERO",
            "HORA", "DIA", "MES", "AÑO", "HOY",
            "MAÑANA", "AYER", "AHORA", "DESPUES", "ANTES",
            "UNKNOWN"  # Fallback class for low confidence predictions
        ]
        return vocabulary
    
    def _load_model(self):
        """Load the trained LSTM model from disk"""
        model_path = settings.ML_MODEL_PATH
        
        if not os.path.exists(model_path):
            log_warning(f"Model file not found at {model_path}. Running in demo mode.")
            return
        
        try:
            self.model = keras.models.load_model(model_path)
            self.is_loaded = True
            log_info(f"LSP model loaded successfully from {model_path}")
        except Exception as e:
            log_error(f"Error loading model: {str(e)}", exc_info=True)
            log_warning("Falling back to demo mode")
    
    def predict(
        self,
        sequence: np.ndarray,
        return_top_k: int = 3
    ) -> Dict:
        """
        Predict sign language word from feature sequence
        
        Args:
            sequence: numpy array of shape (sequence_length, feature_dim)
            return_top_k: Number of top predictions to return
            
        Returns:
            Dictionary with prediction results
        """
        if settings.ML_DEMO_MODE or not self.is_loaded:
            return self._predict_demo(sequence, return_top_k)
        
        try:
            # Add batch dimension: (1, sequence_length, feature_dim)
            sequence_batch = np.expand_dims(sequence, axis=0)
            
            # Get predictions
            predictions = self.model.predict(sequence_batch, verbose=0)[0]
            
            # Get top k predictions
            top_k_indices = np.argsort(predictions)[-return_top_k:][::-1]
            
            results = []
            for idx in top_k_indices:
                if idx < len(self.vocabulary):
                    results.append({
                        "label": self.vocabulary[idx],
                        "confidence": float(predictions[idx])
                    })
            
            return {
                "label": results[0]["label"],
                "confidence": results[0]["confidence"],
                "alternatives": results[1:] if len(results) > 1 else []
            }
            
        except Exception as e:
            log_error(f"Error during prediction: {str(e)}", exc_info=True)
            return self._predict_demo(sequence, return_top_k)
    
    def _predict_demo(
        self,
        sequence: np.ndarray,
        return_top_k: int = 3
    ) -> Dict:
        """
        Demo prediction with simulated results for testing
        
        Args:
            sequence: numpy array (not used in demo)
            return_top_k: Number of top predictions
            
        Returns:
            Simulated prediction results
        """
        # Simulate prediction with random results
        import random
        
        # Select random words from vocabulary (excluding UNKNOWN)
        available_words = [w for w in self.vocabulary if w != "UNKNOWN"]
        selected_words = random.sample(available_words, min(return_top_k, len(available_words)))
        
        # Generate fake confidences
        confidences = sorted([random.uniform(0.5, 0.95) for _ in selected_words], reverse=True)
        
        results = [
            {"label": word, "confidence": conf}
            for word, conf in zip(selected_words, confidences)
        ]
        
        return {
            "label": results[0]["label"],
            "confidence": results[0]["confidence"],
            "alternatives": results[1:] if len(results) > 1 else []
        }
    
    def get_vocabulary(self) -> List[str]:
        """
        Get available vocabulary
        
        Returns:
            List of available words
        """
        return [w for w in self.vocabulary if w != "UNKNOWN"]


# Global model instance (singleton)
_model_instance: Optional[LSPModel] = None


def get_model() -> LSPModel:
    """
    Get or create the global model instance
    
    Returns:
        LSPModel instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = LSPModel()
    return _model_instance
