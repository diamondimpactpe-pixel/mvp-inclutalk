"""
LSP Prediction service
Coordinates feature extraction and model prediction
"""
from typing import Dict, List
from app.schemas.lsp import LSPSequence, LSPPrediction, LSPFrame
from app.ml.feature_extraction import extract_sequence_features
from app.ml.model import get_model
from app.config import settings
from app.utils.logger import log_info, log_debug


def predict_lsp_sequence(sequence: LSPSequence) -> LSPPrediction:
    """
    Predict LSP word from a sequence of frames
    
    Args:
        sequence: LSPSequence with frames and keypoints
        
    Returns:
        LSPPrediction with label, confidence, and alternatives
    """
    # Extract features from sequence
    log_debug(f"Extracting features from {len(sequence.frames)} frames")
    feature_sequence = extract_sequence_features(
        sequence.frames,
        sequence_length=settings.ML_SEQUENCE_LENGTH
    )
    
    # Get model and predict
    model = get_model()
    prediction_result = model.predict(feature_sequence, return_top_k=3)
    
    # Extract results
    label = prediction_result["label"]
    confidence = prediction_result["confidence"]
    alternatives = prediction_result.get("alternatives", [])
    
    # Check confidence threshold
    is_confident = confidence >= settings.ML_CONFIDENCE_THRESHOLD
    
    # If not confident enough, mark as UNKNOWN
    if not is_confident:
        log_info(f"Low confidence prediction: {label} ({confidence:.2f})")
        label = "UNKNOWN"
    
    log_info(f"LSP Prediction: {label} (confidence: {confidence:.2f})")
    
    return LSPPrediction(
        label=label,
        confidence=confidence,
        is_confident=is_confident,
        threshold=settings.ML_CONFIDENCE_THRESHOLD,
        alternatives=alternatives
    )


def get_available_vocabulary() -> List[str]:
    """
    Get list of available LSP words
    
    Returns:
        List of vocabulary words
    """
    model = get_model()
    return model.get_vocabulary()
