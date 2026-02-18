"""
Feature extraction - CORREGIDO para coincidir con el modelo entrenado
Extrae exactamente (30, 126) como lo hace 1_grabar_dataset.py
"""
import numpy as np
from typing import List
from app.schemas.lsp import LSPFrame


def extract_frame_features(frame: LSPFrame) -> np.ndarray:
    """
    Extrae 126 features de un frame (igual que el script de entrenamiento).
    - Mano izquierda: 21 × 3 (x,y,z) = 63
    - Mano derecha: 21 × 3 (x,y,z) = 63
    Total: 126
    
    SIN visibility, SIN pose, SIN face — solo manos x,y,z
    """
    zeros63 = np.zeros(63)
    
    # Mano izquierda
    if frame.left_hand_landmarks and len(frame.left_hand_landmarks) == 21:
        left = np.array([[lm.x, lm.y, lm.z if lm.z else 0.0] 
                         for lm in frame.left_hand_landmarks]).flatten()
    else:
        left = zeros63
    
    # Mano derecha
    if frame.right_hand_landmarks and len(frame.right_hand_landmarks) == 21:
        right = np.array([[lm.x, lm.y, lm.z if lm.z else 0.0] 
                          for lm in frame.right_hand_landmarks]).flatten()
    else:
        right = zeros63
    
    return np.concatenate([left, right])  # (126,)


def extract_sequence_features(
    frames: List[LSPFrame],
    sequence_length: int = 30
) -> np.ndarray:
    """
    Extrae features de una secuencia de frames.
    Salida: (30, 126) — exactamente como el modelo fue entrenado
    """
    features_list = []
    
    for frame in frames[:sequence_length]:
        frame_feats = extract_frame_features(frame)
        features_list.append(frame_feats)
    
    # Stack
    features_array = np.array(features_list)
    
    # Pad con ceros si hay menos de 30 frames
    if len(features_array) < sequence_length:
        last_frame = features_array[-1] if len(features_array) > 0 else np.zeros(126)
        padding = np.tile(last_frame, (sequence_length - len(features_array), 1))
        features_array = np.vstack([features_array, padding])
    
    # Truncar si hay más de 30 frames
    elif len(features_array) > sequence_length:
        features_array = features_array[-sequence_length:]
    
    return features_array  # (30, 126)


def calculate_feature_dimension() -> int:
    """Dimensión de features: 126 (2 manos × 21 puntos × 3 coords)"""
    return 126


FEATURE_DIM = calculate_feature_dimension()