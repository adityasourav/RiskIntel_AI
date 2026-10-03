import json
from typing import List
from .base import DataSource, DataRecord

class SocialSource(DataSource):
    """Social media data source."""

    def __init__(self, sample_path: str = "data/sample/sample_social.json"):
        self.sample_path = sample_path
        self.dataset_name = "zeroshot/twitter-financial-news-sentiment"

    def fetch(self, keyword: str, max_results: int = 100) -> List[DataRecord]:
        """Fetch from huggingface datasets."""
        try:
            from datasets import load_dataset
            dataset = load_dataset(self.dataset_name, split="train")
            
            records = []
            count = 0
            for item in dataset:
                text = item.get("text", "")
                if keyword.lower() in text.lower():
                    record = DataRecord(
                        source="social",
                        timestamp="2026-10-08T00:00:00Z", # placeholder
                        text=text,
                        title="",
                        entity=keyword,
                        url="",
                        metadata={"label": item.get("label", -1)}
                    )
                    records.append(record)
                    count += 1
                    if count >= max_results:
                        break
                        
            return records
            
        except Exception as e:
            print(f"Social fetch failed: {e}. Falling back to sample data.")
            return self.load_sample()

    def load_sample(self) -> List[DataRecord]:
        """Load from sample JSON with fallback paths."""
        import os
        candidate_paths = [
            self.sample_path,
            os.path.join("data", "sample", "sample_social.json"),
            os.path.join("..", "data", "sample", "sample_social.json"),
            os.path.join(os.path.dirname(__file__), "..", "data", "sample", "sample_social.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "sample_social.json"),
            os.path.join(os.path.expanduser("~"), "Desktop", "college-aditya-saurav-hackathon", "data", "sample", "sample_social.json"),
            "/Users/adityasaurav/.gemini/antigravity/scratch/RiskIntel_AI/data/sample/sample_social.json"
        ]

        data = None
        for p in candidate_paths:
            if p and os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    break
                except Exception:
                    continue

        if data is None:
            data = [
                {"source": "social", "timestamp": "2026-10-01T09:00:00Z", "text": "$AAPL earnings crushed expectations!", "title": "", "entity": "AAPL", "url": ""},
                {"source": "social", "timestamp": "2026-10-02T10:30:00Z", "text": "Fed rate hike is going to destroy the housing market", "title": "", "entity": "Fed", "url": ""},
                {"source": "social", "timestamp": "2026-10-03T12:15:00Z", "text": "Just sold all my $TSLA shares, this company is done", "title": "", "entity": "TSLA", "url": ""},
                {"source": "social", "timestamp": "2026-10-04T14:45:00Z", "text": "Breaking: China retaliates with tariffs on US goods", "title": "", "entity": "China", "url": ""},
                {"source": "social", "timestamp": "2026-10-05T08:20:00Z", "text": "$SPY hitting all-time highs, bears in shambles", "title": "", "entity": "SPY", "url": ""},
                {"source": "social", "timestamp": "2026-10-06T16:50:00Z", "text": "Massive insider selling at $META, something is wrong", "title": "", "entity": "META", "url": ""},
                {"source": "social", "timestamp": "2026-10-07T11:10:00Z", "text": "Gold surging as geopolitical tensions rise", "title": "", "entity": "Gold", "url": ""},
                {"source": "social", "timestamp": "2026-10-08T09:30:00Z", "text": "Banking crisis fears spreading to European markets", "title": "", "entity": "Banking", "url": ""},
                {"source": "social", "timestamp": "2026-10-08T13:45:00Z", "text": "$NVDA AI hype is real, revenue up 200%", "title": "", "entity": "NVDA", "url": ""},
                {"source": "social", "timestamp": "2026-10-08T15:20:00Z", "text": "Credit default swaps widening, recession incoming", "title": "", "entity": "Credit default swaps", "url": ""},
            ]

        records = []
        for item in data:
            records.append(DataRecord(
                source=item.get("source", "social"),
                timestamp=item.get("timestamp", ""),
                text=item.get("text", ""),
                title=item.get("title", ""),
                entity=item.get("entity", ""),
                url=item.get("url", ""),
                metadata=item.get("metadata", {})
            ))
        return records
