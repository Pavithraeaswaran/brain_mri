import random
from dataclasses import dataclass

@dataclass
class InferenceResult:
    prediction: str
    confidence: float

class BrainTumorClassifier:
    def __init__(self, model_path: str | None = None):
        # In a real implementation, load the torch model here
        self.model_path = model_path

    def predict(self, image_path: str) -> InferenceResult:
        # Stubbed prediction
        prediction = random.choice(["Tumor", "Normal"])
        confidence = round(random.random() * 0.3 + 0.7, 3)
        return InferenceResult(prediction=prediction, confidence=confidence)

# Singleton-like loader
_model = None

def get_model(model_path: str | None = None) -> BrainTumorClassifier:
    global _model
    if _model is None:
        _model = BrainTumorClassifier(model_path)
    return _model
