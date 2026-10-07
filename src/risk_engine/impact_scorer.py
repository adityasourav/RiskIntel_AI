import re
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ImpactResult:
    score: float
    risk_level: str
    components: Dict[str, float]

class ImpactScorer:
    """Scores financial impact based on multiple components."""
    
    WEIGHTS = {
        'event_severity': 0.35,
        'sentiment_magnitude': 0.20,
        'entity_importance': 0.25,
        'keyword_urgency': 0.20
    }
    
    EVENT_SEVERITY_SCORES = {
        'Geopolitical': 9.0,
        'Credit Event': 8.5,
        'Macroeconomic': 8.0,
        'Regulatory': 7.0,
        'Market and Financial': 7.0,
        'Merger and Acquisition': 6.0,
        'Earnings and Financial Results': 5.0,
        'Product Launch': 4.0,
        'Other': 3.0
    }
    
    MAJOR_ENTITIES = {
        'Federal Reserve': 10, 'US': 9, 'China': 9, 'EU': 8,
        'Apple': 8, 'Google': 8, 'Microsoft': 8, 'JPMorgan': 8,
        'Goldman Sachs': 8
    }
    
    KEYWORDS = {
        'high': ['crisis', 'war', 'crash', 'collapse', 'default', 'sanctions', 'ban'],
        'medium': ['tariff', 'hike', 'cut', 'surge', 'plunge', 'investigation'],
        'low': ['announces', 'reports', 'updates', 'launches']
    }
    
    def score(self, event_type: str, sentiment_score: float, entities: List[str], text: str) -> ImpactResult:
        
        # 1. event_severity (weight=0.35)
        event_severity = self.EVENT_SEVERITY_SCORES.get(event_type, 3.0)
        
        # 2. sentiment_magnitude (weight=0.20)
        sentiment_magnitude = min(abs(sentiment_score) * 10, 10.0)
        
        # 3. entity_importance (weight=0.25)
        entity_score = 5.0
        if entities:
            scores = [self.MAJOR_ENTITIES.get(ent, 5.0) for ent in entities]
            entity_score = max(scores)
            
        # 4. keyword_urgency (weight=0.20)
        text_lower = text.lower()
        keyword_score = 4.0
        
        high_found = any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in self.KEYWORDS['high'])
        if high_found:
            keyword_score = 9.5
        else:
            medium_found = any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in self.KEYWORDS['medium'])
            if medium_found:
                keyword_score = 7.0
            else:
                low_found = any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in self.KEYWORDS['low'])
                if low_found:
                    keyword_score = 4.0
                    
        # Compute final score
        components = {
            'event_severity': event_severity,
            'sentiment_magnitude': sentiment_magnitude,
            'entity_importance': entity_score,
            'keyword_urgency': keyword_score
        }
        
        impact = sum(components[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        impact = max(1.0, min(10.0, impact))
        
        # Determine risk level
        if impact >= 7.0:
            risk_level = 'HIGH'
        elif impact >= 4.0:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
            
        return ImpactResult(
            score=impact,
            risk_level=risk_level,
            components=components
        )
