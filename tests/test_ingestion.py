"""Standard library unittest tests for Data Ingestion schemas and fallback loading."""

import unittest
from ingestion.base import DataRecord
from ingestion.gdelt_source import GdeltSource
from ingestion.social_source import SocialSource


class TestIngestion(unittest.TestCase):
    def test_data_record_creation(self):
        rec = DataRecord(
            source="news",
            timestamp="2026-10-08T10:00:00Z",
            text="Tariff tensions escalate in global markets",
            title="Tariffs escalate",
            entity="US",
            url="https://example.com"
        )
        self.assertEqual(rec.source, "news")
        self.assertEqual(rec.entity, "US")

    def test_gdelt_sample_fallback(self):
        src = GdeltSource(sample_path="data/sample/sample_news.json")
        samples = src.load_sample()
        self.assertGreater(len(samples), 0)
        self.assertTrue(any("tariff" in s.text.lower() or "tariffs" in s.text.lower() for s in samples))

    def test_social_sample_fallback(self):
        src = SocialSource(sample_path="data/sample/sample_social.json")
        samples = src.load_sample()
        self.assertGreater(len(samples), 0)
        self.assertTrue(all(s.source == "social" for s in samples))


if __name__ == "__main__":
    unittest.main()
