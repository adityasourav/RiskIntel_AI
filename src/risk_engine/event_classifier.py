from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class EventResult:
    event_type: str
    confidence: float
    all_scores: Dict[str, float]

class EventClassifier:
    """Classifies text into major financial risk event types."""
    
    EVENT_TYPES = [
        'Geopolitical', 'Macroeconomic', 'Credit Event', 
        'Merger and Acquisition', 'Product Launch', 
        'Earnings and Financial Results', 'Regulatory', 
        'Market and Financial', 'Other'
    ]
    
    _pipeline: Optional[Any] = None
    
    @classmethod
    def _get_pipeline(cls):
        if cls._pipeline is None:
            from transformers import pipeline
            cls._pipeline = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
        return cls._pipeline
        
    def classify(self, text: str) -> EventResult:
        if not text or not text.strip():
            return EventResult(
                event_type='Other', 
                confidence=1.0, 
                all_scores={evt: 0.0 for evt in self.EVENT_TYPES}
            )
            
        try:
            pipe = self._get_pipeline()
            result = pipe(text, self.EVENT_TYPES, truncation=True, max_length=512)
            labels = result['labels']
            scores = result['scores']
            all_scores = {labels[i]: scores[i] for i in range(len(labels))}
            return EventResult(
                event_type=labels[0],
                confidence=scores[0],
                all_scores=all_scores
            )
        except Exception:
            # Domain-rule event classification fallback
            lower = text.lower()
            if any(k in lower for k in ["tariff", "tariffs", "trade war", "sanction", "geopolitical", "border", "military", "tensions"]):
                top_event = "Geopolitical"
            elif any(k in lower for k in ["interest rate", "basis points", "inflation", "central bank", "federal reserve", "fed", "macro", "recession"]):
                top_event = "Macroeconomic"
            elif any(k in lower for k in ["downgrade", "credit default", "insolvency", "liquidity", "debt", "rating agency"]):
                top_event = "Credit Event"
            elif any(k in lower for k in ["merger", "acquisition", "acquire", "takeover", "buyout"]):
                top_event = "Merger and Acquisition"
            elif any(k in lower for k in ["earnings", "revenue", "quarter", "q1", "q2", "q3", "q4", "eps", "profit"]):
                top_event = "Earnings and Financial Results"
            elif any(k in lower for k in ["regulatory", "investigation", "sec", "doj", "probe", "fine", "compliance"]):
                top_event = "Regulatory"
            elif any(k in lower for k in ["launches", "product", "launch", "unveil", "feature"]):
                top_event = "Product Launch"
            elif any(k in lower for k in ["stock", "shares", "rally", "selloff", "market", "equities", "crash"]):
                top_event = "Market and Financial"
            else:
                top_event = "Other"
                
            all_scores = {evt: (0.85 if evt == top_event else 0.02) for evt in self.EVENT_TYPES}
            return EventResult(
                event_type=top_event,
                confidence=0.85,
                all_scores=all_scores
            )
