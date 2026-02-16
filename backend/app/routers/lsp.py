"""LSP (Lengua de Señas) recognition router"""
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.lsp import LSPSequence, LSPPrediction, LSPVocabulary
from app.ml.predict import predict_lsp_sequence, get_available_vocabulary
from app.utils.logger import log_info, log_error

router = APIRouter(prefix="/lsp", tags=["LSP Recognition"])

@router.post("/predict", response_model=LSPPrediction)
def predict_sign(sequence: LSPSequence):
    """
    Predict sign language word from keypoint sequence
    """
    try:
        prediction = predict_lsp_sequence(sequence)
        return prediction
    except Exception as e:
        log_error(f"Error in LSP prediction: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/vocabulary", response_model=LSPVocabulary)
def get_vocabulary():
    """Get available LSP vocabulary"""
    words = get_available_vocabulary()
    return LSPVocabulary(words=words, total_count=len(words))
