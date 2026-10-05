import re
from dataclasses import dataclass, field
from typing import List, Dict, Set
import hashlib

@dataclass
class CleanedText:
    original_text: str
    clean_text: str
    extracted_entities: List[str]
    extracted_tickers: List[str]

class TextCleaner:
    """Cleans text for NLP processing and extracts metadata."""
    
    MAJOR_ENTITIES = {
        "Apple": "Apple", "Tesla": "Tesla", "Google": "Google", 
        "Microsoft": "Microsoft", "Amazon": "Amazon", "Meta": "Meta", 
        "NVIDIA": "NVIDIA", "JPMorgan": "JPMorgan", "Goldman Sachs": "Goldman Sachs",
        "AAPL": "Apple", "TSLA": "Tesla", "GOOGL": "Google",
        "MSFT": "Microsoft", "AMZN": "Amazon", "META": "Meta",
        "NVDA": "NVIDIA", "JPM": "JPMorgan", "GS": "Goldman Sachs",
        "Federal Reserve": "Federal Reserve", "Fed": "Federal Reserve",
        "US": "US", "U.S.": "US", "United States": "US",
        "China": "China", "EU": "EU", "European Union": "EU",
        "ECB": "ECB", "European Central Bank": "ECB"
    }

    def clean(self, text: str) -> CleanedText:
        original_text = text
        
        # 2. Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # 3. Remove emojis and non-ASCII decorators
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        # 4. Extract tickers ($AAPL)
        tickers = re.findall(r'\$([A-Za-z]+)', text)
        extracted_tickers = [t.upper() for t in tickers]
        
        # Remove $ prefix from tickers in text
        text = re.sub(r'\$([A-Za-z]+)', r'\1', text)
        
        # 8. Extract entities (case-insensitive search against original_text)
        extracted_entities = []
        for entity_name, entity_val in self.MAJOR_ENTITIES.items():
            if re.search(r'\b' + re.escape(entity_name) + r'\b', original_text, re.IGNORECASE):
                if entity_val not in extracted_entities:
                    extracted_entities.append(entity_val)
                    
        # 5. Lowercase
        text = text.lower()
        
        # 6. Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # 7. Strip leading/trailing whitespace
        clean_text = text.strip()
        
        return CleanedText(
            original_text=original_text,
            clean_text=clean_text,
            extracted_entities=list(set(extracted_entities)),
            extracted_tickers=list(set(extracted_tickers))
        )
        
    @classmethod
    def deduplicate(cls, texts: List[CleanedText]) -> List[CleanedText]:
        seen_hashes = set()
        deduped = []
        for t in texts:
            text_hash = hashlib.md5(t.clean_text.encode('utf-8')).hexdigest()
            if text_hash not in seen_hashes:
                seen_hashes.add(text_hash)
                deduped.append(t)
        return deduped
