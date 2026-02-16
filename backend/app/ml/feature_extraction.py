"""
Feature extraction from MediaPipe landmarks
Converts MediaPipe Holistic landmarks to feature vectors for LSTM model
"""
import numpy as np
from typing import List, Optional, Dict
from app.schemas.lsp import LSPFrame, LSPKeypoint


# MediaPipe landmark counts
FACE_LANDMARKS_COUNT = 468
LEFT_HAND_LANDMARKS_COUNT = 21
RIGHT_HAND_LANDMARKS_COUNT = 21
POSE_LANDMARKS_COUNT = 33

# Feature dimensions per landmark (x, y, z, visibility)
FEATURES_PER_LANDMARK = 4

# Total features per frame (using Holistic)
# Face: 468 * 4 = 1872 (we'll use subset)
# Hands: 21 * 4 * 2 = 168
# Pose: 33 * 4 = 132
# Total optimized: ~1662 features (configurable)


def extract_keypoint_features(keypoint: LSPKeypoint) -> np.ndarray:
    """
    Extract features from a single keypoint
    
    Args:
        keypoint: LSPKeypoint object
        
    Returns:
        numpy array [x, y, z, visibility]
    """
    return np.array([
        keypoint.x,
        keypoint.y,
        keypoint.z if keypoint.z is not None else 0.0,
        keypoint.visibility if keypoint.visibility is not None else 1.0
    ])


def extract_landmarks_features(
    landmarks: Optional[List[LSPKeypoint]],
    expected_count: int
) -> np.ndarray:
    """
    Extract features from a list of landmarks
    
    Args:
        landmarks: List of LSPKeypoint objects
        expected_count: Expected number of landmarks
        
    Returns:
        numpy array of shape (expected_count * 4,) with zero-padding if needed
    """
    if landmarks is None or len(landmarks) == 0:
        # Return zero-padded array
        return np.zeros(expected_count * FEATURES_PER_LANDMARK)
    
    # Extract features from each landmark
    features = []
    for i in range(expected_count):
        if i < len(landmarks):
            features.extend(extract_keypoint_features(landmarks[i]))
        else:
            # Zero-pad if fewer landmarks than expected
            features.extend([0.0, 0.0, 0.0, 0.0])
    
    return np.array(features)


def extract_frame_features(frame: LSPFrame) -> np.ndarray:
    """
    Extract all features from a single frame
    
    For this MVP, we focus on hands and simplified pose
    Feature vector structure:
    - Left hand: 21 * 4 = 84
    - Right hand: 21 * 4 = 84
    - Pose (selected): 33 * 4 = 132
    - Face (selected key points): ~50 * 4 = 200
    Total: ~500 features (can be adjusted)
    
    Args:
        frame: LSPFrame object with landmarks
        
    Returns:
        numpy array of shape (feature_dim,)
    """
    features = []
    
    # Extract hand features (most important for sign language)
    left_hand_features = extract_landmarks_features(
        frame.left_hand_landmarks,
        LEFT_HAND_LANDMARKS_COUNT
    )
    right_hand_features = extract_landmarks_features(
        frame.right_hand_landmarks,
        RIGHT_HAND_LANDMARKS_COUNT
    )
    
    # Extract pose features
    pose_features = extract_landmarks_features(
        frame.pose_landmarks,
        POSE_LANDMARKS_COUNT
    )
    
    # For MVP, skip face landmarks (or use subset)
    # If needed, extract key facial landmarks for expressions
    # face_features = extract_landmarks_features(
    #     frame.face_landmarks,
    #     FACE_LANDMARKS_COUNT  # or subset like 50
    # )
    
    # Combine all features
    features.extend(left_hand_features)
    features.extend(right_hand_features)
    features.extend(pose_features)
    # features.extend(face_features)  # Optional
    
    return np.array(features)


def extract_sequence_features(
    frames: List[LSPFrame],
    sequence_length: int = 15
) -> np.ndarray:
    """
    Extract features from a sequence of frames
    
    Args:
        frames: List of LSPFrame objects
        sequence_length: Fixed sequence length (pad or truncate)
        
    Returns:
        numpy array of shape (sequence_length, feature_dim)
    """
    features_list = []
    
    # Extract features from each frame
    for frame in frames[:sequence_length]:
        frame_features = extract_frame_features(frame)
        features_list.append(frame_features)
    
    # Convert to numpy array
    features_array = np.array(features_list)
    
    # Pad or truncate to fixed sequence length
    if len(features_array) < sequence_length:
        # Pad with zeros
        padding = np.zeros((sequence_length - len(features_array), features_array.shape[1]))
        features_array = np.vstack([features_array, padding])
    elif len(features_array) > sequence_length:
        # Truncate
        features_array = features_array[:sequence_length]
    
    return features_array


def calculate_feature_dimension() -> int:
    """
    Calculate the total feature dimension per frame
    
    Returns:
        Total feature dimension
    """
    dim = 0
    dim += LEFT_HAND_LANDMARKS_COUNT * FEATURES_PER_LANDMARK  # 84
    dim += RIGHT_HAND_LANDMARKS_COUNT * FEATURES_PER_LANDMARK  # 84
    dim += POSE_LANDMARKS_COUNT * FEATURES_PER_LANDMARK  # 132
    # dim += FACE_SUBSET_COUNT * FEATURES_PER_LANDMARK  # Optional
    
    return dim


# Calculate feature dimension for config validation
FEATURE_DIM = calculate_feature_dimension()

print(f"Feature dimension per frame: {FEATURE_DIM}")
