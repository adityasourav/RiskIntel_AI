"""Standard library unittest tests for TextCleaner preprocessing module."""

import unittest
from preprocessing.text_cleaner import TextCleaner


class TestTextCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = TextCleaner()

    def test_clean_urls_and_emojis(self):
        raw = "BREAKING: Apple announces stronger-than-expected earnings! $AAPL 🚀 https://bloomberg.com/news/123"
        res = self.cleaner.clean(raw)
        self.assertNotIn("https://", res.clean_text)
        self.assertNotIn("🚀", res.clean_text)
        self.assertIn("AAPL", res.extracted_tickers)
        self.assertIn("Apple", res.extracted_entities)

    def test_clean_whitespace_and_lowercase(self):
        raw = "   Federal   Reserve   raises   interest rates.   "
        res = self.cleaner.clean(raw)
        self.assertEqual(res.clean_text, "federal reserve raises interest rates.")

    def test_deduplicate(self):
        t1 = self.cleaner.clean("Gold prices surge to new high")
        t2 = self.cleaner.clean("Gold prices surge to new high")
        t3 = self.cleaner.clean("Different news article about oil")
        deduped = TextCleaner.deduplicate([t1, t2, t3])
        self.assertEqual(len(deduped), 2)


if __name__ == "__main__":
    unittest.main()
