import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

from .portfolio import Portfolio
from .scenarios import get_scenario

@dataclass
class AssetImpact:
    """Represents the impact of a stress test on a single asset."""
    asset_name: str
    asset_type: str
    value_before: float
    value_after: float
    change: float
    change_pct: float

@dataclass
class StressTestResult:
    """Represents the complete result of a portfolio stress test."""
    triggered: bool
    event_type: str
    impact_score: float
    risk_level: str
    scenario_name: str
    portfolio_before: float
    portfolio_after: float
    total_loss: float
    loss_percentage: float
    asset_impacts: List[AssetImpact]
    timestamp: str

    def to_dict(self) -> Dict:
        """Convert the result to a dictionary for JSON serialization."""
        return {
            "triggered": self.triggered,
            "event_type": self.event_type,
            "impact_score": self.impact_score,
            "risk_level": self.risk_level,
            "scenario_name": self.scenario_name,
            "portfolio_before": self.portfolio_before,
            "portfolio_after": self.portfolio_after,
            "total_loss": self.total_loss,
            "loss_percentage": self.loss_percentage,
            "asset_impacts": [vars(a) for a in self.asset_impacts],
            "timestamp": self.timestamp
        }

    def to_summary_string(self) -> str:
        """Format the result as a text summary for display."""
        lines = [
            "=== STRESS TEST RESULT ===",
            f"Event Type: {self.event_type}",
            f"Impact Score: {self.impact_score}",
            f"Risk Level: {self.risk_level}",
            f"Scenario: {self.scenario_name}",
            "",
            f"Portfolio Before: ${self.portfolio_before:,.2f}",
            f"Portfolio After:  ${self.portfolio_after:,.2f}",
            f"Total Loss:       ${self.total_loss:,.2f}",
            f"Loss Percentage:  {self.loss_percentage:.2f}%",
            "",
            "Asset Impacts:"
        ]
        
        for imp in self.asset_impacts:
            lines.append(
                f"  {imp.asset_name} ({imp.asset_type}):       ${imp.value_before:,.0f} → ${imp.value_after:,.0f} ({imp.change_pct:.2f}%)"
            )
            
        return "\n".join(lines)

class StressTestSimulator:
    """Simulates stress tests on a portfolio based on risk signals."""
    def __init__(self, portfolio: Optional[Portfolio] = None, base_dir: str = "."):
        if portfolio is None:
            self.portfolio = Portfolio.load_default(base_dir=base_dir)
        else:
            self.portfolio = portfolio

    def run_stress_test(self, risk_signal_dict: dict) -> StressTestResult:
        """Run a stress test based on an extracted risk signal dictionary."""
        event_type = risk_signal_dict.get('event_type', 'Other')
        impact_score = float(risk_signal_dict.get('impact_score', 0.0))
        risk_level = risk_signal_dict.get('risk_level', 'LOW')
        timestamp = datetime.datetime.now().isoformat()
        
        if impact_score < 7.0:
            return StressTestResult(
                triggered=False,
                event_type=event_type,
                impact_score=impact_score,
                risk_level=risk_level,
                scenario_name="None",
                portfolio_before=self.portfolio.total_value,
                portfolio_after=self.portfolio.total_value,
                total_loss=0.0,
                loss_percentage=0.0,
                asset_impacts=[],
                timestamp=timestamp
            )
            
        scenario = get_scenario(event_type)
        scale = impact_score / 10.0
        
        shocked_portfolio = self.portfolio.apply_shocks(scenario.shocks, scale=scale)
        
        asset_impacts = []
        for orig_asset, new_asset in zip(self.portfolio.assets, shocked_portfolio.assets):
            change = new_asset.value - orig_asset.value
            change_pct = (change / orig_asset.value) * 100 if orig_asset.value else 0.0
            
            asset_impacts.append(AssetImpact(
                asset_name=orig_asset.name,
                asset_type=orig_asset.asset_type,
                value_before=orig_asset.value,
                value_after=new_asset.value,
                change=change,
                change_pct=change_pct
            ))
            
        portfolio_before = self.portfolio.total_value
        portfolio_after = shocked_portfolio.total_value
        total_loss = portfolio_before - portfolio_after
        loss_percentage = (total_loss / portfolio_before) * 100 if portfolio_before else 0.0
        
        return StressTestResult(
            triggered=True,
            event_type=event_type,
            impact_score=impact_score,
            risk_level=risk_level,
            scenario_name=scenario.name,
            portfolio_before=portfolio_before,
            portfolio_after=portfolio_after,
            total_loss=total_loss,
            loss_percentage=loss_percentage,
            asset_impacts=asset_impacts,
            timestamp=timestamp
        )

    def run_custom_stress_test(self, event_type: str, impact_score: float) -> StressTestResult:
        """Convenience method to run a custom stress test without a full signal dict."""
        risk_signal_dict = {
            'event_type': event_type,
            'impact_score': impact_score,
            'risk_level': 'HIGH' if impact_score >= 7.0 else 'LOW'
        }
        return self.run_stress_test(risk_signal_dict)
