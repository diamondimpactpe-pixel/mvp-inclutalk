"""
LSP (Lengua de Señas Peruana) schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class LSPKeypoint(BaseModel):
    """Single keypoint (landmark) schema"""
    x: float = Field(..., ge=0.0, le=1.0, description="Normalized x coordinate")
    y: float = Field(..., ge=0.0, le=1.0, description="Normalized y coordinate")
    z: Optional[float] = Field(None, description="Depth coordinate")
    visibility: Optional[float] = Field(None, ge=0.0, le=1.0, description="Visibility score")


class LSPFrame(BaseModel):
    """Single frame with keypoints"""
    timestamp: float = Field(..., description="Frame timestamp in seconds")
    face_landmarks: Optional[List[LSPKeypoint]] = Field(None, max_length=468)
    left_hand_landmarks: Optional[List[LSPKeypoint]] = Field(None, max_length=21)
    right_hand_landmarks: Optional[List[LSPKeypoint]] = Field(None, max_length=21)
    pose_landmarks: Optional[List[LSPKeypoint]] = Field(None, max_length=33)


class LSPSequence(BaseModel):
    """Sequence of frames for LSP prediction"""
    frames: List[LSPFrame] = Field(..., min_length=1, max_length=60)
    session_id: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "frames": [
                    {
                        "timestamp": 0.0,
                        "left_hand_landmarks": [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 1.0}] * 21,
                        "right_hand_landmarks": [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 1.0}] * 21
                    }
                ],
                "session_id": 123
            }
        }


class LSPPrediction(BaseModel):
    """LSP prediction result"""
    label: str = Field(..., description="Predicted word/class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    is_confident: bool = Field(..., description="True if confidence >= threshold")
    threshold: float = Field(..., description="Confidence threshold used")
    alternatives: Optional[List[dict]] = Field(None, description="Alternative predictions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "label": "DNI",
                "confidence": 0.85,
                "is_confident": True,
                "threshold": 0.70,
                "alternatives": [
                    {"label": "DOCUMENTO", "confidence": 0.12},
                    {"label": "CARNET", "confidence": 0.03}
                ]
            }
        }


class LSPVocabulary(BaseModel):
    """Available LSP vocabulary"""
    words: List[str]
    total_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "words": ["DNI", "CITA", "PAGO", "RECLAMO"],
                "total_count": 4
            }
        }
