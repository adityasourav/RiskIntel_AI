"""Standard library unittest tests for Portfolio and Stress Testing simulator."""

import unittest
from stress_testing.portfolio import Portfolio, Asset
from stress_testing.simulator import StressTestSimulator


class TestStressTesting(unittest.TestCase):
    def setUp(self):
        assets = [
            Asset("Corporate Loan A", "Loan", 2_000_000.0, "Financials"),
            Asset("Government Bond", "Bond", 2_000_000.0, "Government"),
            Asset("Corporate Bond", "Bond", 2_000_000.0, "Energy"),
            Asset("Equity Portfolio", "Equity", 2_000_000.0, "Diversified"),
            Asset("Derivative A", "Derivative", 2_000_000.0, "Financials"),
        ]
        self.portfolio = Portfolio(assets)
        self.sim = StressTestSimulator(portfolio=self.portfolio)

    def test_portfolio_total_value(self):
        self.assertEqual(self.portfolio.total_value, 10_000_000.0)

    def test_stress_test_trigger_high_impact(self):
        signal = {
            "event_type": "Geopolitical",
            "impact_score": 8.6,
            "risk_level": "HIGH"
        }
        result = self.sim.run_stress_test(signal)
        self.assertTrue(result.triggered)
        self.assertEqual(result.portfolio_before, 10_000_000.0)
        self.assertLess(result.portfolio_after, result.portfolio_before)
        self.assertGreater(result.total_loss, 0)
        self.assertGreater(result.loss_percentage, 0)
        self.assertEqual(len(result.asset_impacts), len(self.portfolio.assets))

    def test_stress_test_low_impact_not_triggered(self):
        signal = {
            "event_type": "Product Launch",
            "impact_score": 4.5,
            "risk_level": "LOW"
        }
        result = self.sim.run_stress_test(signal)
        self.assertFalse(result.triggered)
        self.assertEqual(result.total_loss, 0.0)
        self.assertEqual(result.portfolio_after, 10_000_000.0)


if __name__ == "__main__":
    unittest.main()
