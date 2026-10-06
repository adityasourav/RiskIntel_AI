from dataclasses import dataclass
from typing import List, Optional, Any

@dataclass
class SentimentResult:
    label: str
    confidence: float
    numerical_score: float

class SentimentAnalyzer:
    """Analyzes financial sentiment using ProsusAI/finbert."""
    
    _pipeline: Optional[Any] = None
    
    @classmethod
    def _get_pipeline(cls):
        if cls._pipeline is None:
            from transformers import pipeline
            cls._pipeline = pipeline('sentiment-analysis', model='ProsusAI/finbert', tokenizer='ProsusAI/finbert')
        return cls._pipeline

    def analyze(self, text: str) -> SentimentResult:
        if not text or not text.strip():
            return SentimentResult(label='neutral', confidence=0.0, numerical_score=0.0)
            
        try:
            pipe = self._get_pipeline()
            result = pipe(text, truncation=True, max_length=512)[0]
            label = result['label'].lower()
            confidence = float(result['score'])
            
            if label == 'positive':
                score = confidence
            elif label == 'negative':
                score = -confidence
            else:
                score = confidence * 0.05
        except Exception:
            # Robust rule-based financial sentiment fallback (offline/lightweight mode)
            lower = text.lower()
            pos_words = ["strong", "stronger", "growth", "beat", "positive", "crushed", "surge", "highs", "gain", "profit"]
            neg_words = ["decline", "fall", "tariff", "tariffs", "crash", "recession", "crashing", "loss", "downgrade", "crisis", "fears", "cut", "inflation"]
            
            pos_count = sum(1 for w in pos_words if w in lower)
            neg_count = sum(1 for w in neg_words if w in lower)
            
            if neg_count > pos_count:
                label = "negative"
                confidence = min(0.65 + 0.1 * neg_count, 0.95)
                score = -confidence
            elif pos_count > neg_count:
                label = "positive"
                confidence = min(0.65 + 0.1 * pos_count, 0.95)
                score = confidence
            else:
                label = "neutral"
                confidence = 0.50
                score = 0.0
            
        return SentimentResult(
            label=label,
            confidence=confidence,
            numerical_score=score
        )
        
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        return [self.analyze(text) for text in texts]
