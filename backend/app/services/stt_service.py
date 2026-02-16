"""
Speech-to-Text service
Mock implementation for MVP - can be replaced with Whisper API
"""
import random
from typing import Optional
from app.utils.logger import log_info, log_warning
from app.config import settings


class STTService:
    """Speech-to-Text service"""
    
    def __init__(self):
        self.demo_mode = settings.STT_DEMO_MODE
        
        if not self.demo_mode:
            try:
                import whisper
                self.model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
                log_info(f"Whisper model loaded: {settings.WHISPER_MODEL_SIZE}")
            except ImportError:
                log_warning("Whisper not available, using demo mode")
                self.demo_mode = True
    
    def transcribe_audio(self, audio_data: bytes) -> dict:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio file bytes
            
        Returns:
            Dictionary with text and confidence
        """
        if self.demo_mode:
            return self._transcribe_demo()
        
        # TODO: Implement real Whisper transcription
        # Save audio_data to temp file
        # result = self.model.transcribe(temp_file)
        # return {"text": result["text"], "confidence": 0.95}
        
        return self._transcribe_demo()
    
    def _transcribe_demo(self) -> dict:
        """Demo transcription with sample phrases"""
        sample_phrases = [
            "Necesito renovar mi DNI",
            "Quiero hacer un pago",
            "Tengo una cita programada",
            "Necesito presentar un reclamo",
            "¿Dónde puedo obtener un certificado?",
            "Mi documento está vencido",
            "Necesito ayuda con un trámite",
        ]
        
        text = random.choice(sample_phrases)
        confidence = random.uniform(0.85, 0.98)
        
        return {
            "text": text,
            "confidence": confidence,
            "language": "es"
        }


# Global instance
_stt_service: Optional[STTService] = None


def get_stt_service() -> STTService:
    """Get STT service instance"""
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service
