import json
from datetime import datetime, timedelta
from typing import List
from .base import DataSource, DataRecord

class GdeltSource(DataSource):
    """GDELT news data source."""

    def __init__(self, sample_path: str = "data/sample/sample_news.json"):
        self.sample_path = sample_path

    def fetch(self, keyword: str, max_results: int = 100) -> List[DataRecord]:
        """Fetch data from GDELT."""
        try:
            from gdeltdoc import GdeltDoc, Filters
            gd = GdeltDoc()
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            f = Filters(
                keyword=keyword,
                start_date=start_date,
                end_date=end_date
            )
            
            articles = gd.article_search(f)
            
            records = []
            for _, row in articles.head(max_results).iterrows():
                record = DataRecord(
                    source="news",
                    timestamp=str(row.get("seendate", "")),
                    text=str(row.get("title", "")),
                    title=str(row.get("title", "")),
                    entity=keyword,
                    url=str(row.get("url", "")),
                    metadata={"domain": str(row.get("domain", ""))}
                )
                records.append(record)
            return records
            
        except Exception as e:
            print(f"GDELT fetch failed: {e}. Falling back to sample data.")
            return self.load_sample()

    def load_sample(self) -> List[DataRecord]:
        """Load from sample JSON with fallback paths."""
        import os
        candidate_paths = [
            self.sample_path,
            os.path.join("data", "sample", "sample_news.json"),
            os.path.join("..", "data", "sample", "sample_news.json"),
            os.path.join(os.path.dirname(__file__), "..", "data", "sample", "sample_news.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "sample_news.json"),
            os.path.join(os.path.expanduser("~"), "Desktop", "college-aditya-saurav-hackathon", "data", "sample", "sample_news.json"),
            "/Users/adityasaurav/.gemini/antigravity/scratch/RiskIntel_AI/data/sample/sample_news.json"
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
                {"source": "news", "timestamp": "2026-10-01T10:00:00Z", "text": "US announces new tariffs on Chinese imports. Markets react negatively.", "title": "US announces new tariffs on Chinese imports", "entity": "US", "url": "http://example.com/news/1"},
                {"source": "news", "timestamp": "2026-10-02T11:00:00Z", "text": "Federal Reserve raises interest rates by 50 basis points to combat inflation.", "title": "Federal Reserve raises interest rates by 50 basis points", "entity": "Federal Reserve", "url": "http://example.com/news/2"},
                {"source": "news", "timestamp": "2026-10-03T09:30:00Z", "text": "Apple reports stronger-than-expected Q3 earnings, sending stock soaring.", "title": "Apple reports stronger-than-expected Q3 earnings", "entity": "Apple", "url": "http://example.com/news/3"},
                {"source": "news", "timestamp": "2026-10-04T14:15:00Z", "text": "Major bank faces regulatory investigation over mortgage lending practices.", "title": "Major bank faces regulatory investigation", "entity": "Major Bank", "url": "http://example.com/news/4"},
                {"source": "news", "timestamp": "2026-10-05T08:45:00Z", "text": "Oil prices surge amid Middle East tensions, causing concern for global supply.", "title": "Oil prices surge amid Middle East tensions", "entity": "Oil", "url": "http://example.com/news/5"},
                {"source": "news", "timestamp": "2026-10-06T13:00:00Z", "text": "European Central Bank signals rate cut as economic growth slows.", "title": "European Central Bank signals rate cut", "entity": "European Central Bank", "url": "http://example.com/news/6"},
                {"source": "news", "timestamp": "2026-10-07T16:20:00Z", "text": "Tech giant announces $10B acquisition of AI startup.", "title": "Tech giant announces $10B acquisition", "entity": "Tech Giant", "url": "http://example.com/news/7"},
                {"source": "news", "timestamp": "2026-10-08T09:10:00Z", "text": "Credit rating agency downgrades major corporation due to debt levels.", "title": "Credit rating agency downgrades major corporation", "entity": "Major Corporation", "url": "http://example.com/news/8"},
                {"source": "news", "timestamp": "2026-10-08T11:40:00Z", "text": "New trade agreement signed between US and EU, boosting cross-border commerce.", "title": "New trade agreement signed between US and EU", "entity": "US", "url": "http://example.com/news/9"},
                {"source": "news", "timestamp": "2026-10-08T15:55:00Z", "text": "Company announces major product recall following safety concerns.", "title": "Company announces major product recall", "entity": "Company", "url": "http://example.com/news/10"}
            ]

        records = []
        for item in data:
            records.append(DataRecord(
                source=item.get("source", "news"),
                timestamp=item.get("timestamp", ""),
                text=item.get("text", ""),
                title=item.get("title", ""),
                entity=item.get("entity", ""),
                url=item.get("url", ""),
                metadata=item.get("metadata", {})
            ))
        return records
