"""Standard library unittest tests for ImpactScorer component."""

import unittest
from risk_engine.impact_scorer import ImpactScorer


class TestImpactScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = ImpactScorer()

    def test_high_impact_geopolitical(self):
        res = self.scorer.score(
            event_type="Geopolitical",
            sentiment_score=-0.8,
            entities=["US", "China"],
            text="US imposes major tariffs and sanctions on Chinese tech firms, risking global trade war"
        )
        self.assertGreaterEqual(res.score, 7.0)
        self.assertEqual(res.risk_level, "HIGH")
        self.assertIn("event_severity", res.components)
        self.assertEqual(res.components["event_severity"], 9.0)

    def test_low_impact_product_launch(self):
        res = self.scorer.score(
            event_type="Product Launch",
            sentiment_score=0.4,
            entities=["RandomApp"],
            text="Startup announces updates to its mobile app widget"
        )
        self.assertLess(res.score, 6.0)
        self.assertIn(res.risk_level, ["LOW", "MEDIUM"])

    def test_score_bounds(self):
        res = self.scorer.score(
            event_type="Other",
            sentiment_score=0.0,
            entities=[],
            text="Market summary for the day."
        )
        self.assertTrue(1.0 <= res.score <= 10.0)


if __name__ == "__main__":
    unittest.main()
