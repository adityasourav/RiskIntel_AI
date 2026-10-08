import json
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional
import os

@dataclass
class Asset:
    """Represents a financial asset in a portfolio."""
    name: str
    asset_type: str
    value: float
    sector: str

class Portfolio:
    """Represents a financial portfolio containing multiple assets."""
    def __init__(self, assets: List[Asset]):
        self.assets = assets

    @property
    def total_value(self) -> float:
        """Calculate the total value of all assets in the portfolio."""
        return sum(asset.value for asset in self.assets)

    @classmethod
    def load_from_json(cls, filepath: str) -> 'Portfolio':
        """Load portfolio data from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        # Handle both list of assets and a dictionary with 'assets' key
        assets_data = data.get('assets', data) if isinstance(data, dict) else data
        assets = []
        for item in assets_data:
            item_copy = dict(item)
            if 'type' in item_copy and 'asset_type' not in item_copy:
                item_copy['asset_type'] = item_copy.pop('type')
            assets.append(Asset(**item_copy))
        return cls(assets)

    @classmethod
    def load_default(cls, base_dir: str = ".") -> 'Portfolio':
        """Load the default synthetic portfolio."""
        candidate_paths = [
            os.path.join(base_dir, "data", "portfolio", "synthetic_portfolio.json"),
            os.path.join(base_dir, "..", "data", "portfolio", "synthetic_portfolio.json"),
            os.path.join(os.path.dirname(__file__), "..", "data", "portfolio", "synthetic_portfolio.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "portfolio", "synthetic_portfolio.json"),
            os.path.join(os.path.expanduser("~"), "Desktop", "college-aditya-saurav-hackathon", "data", "portfolio", "synthetic_portfolio.json"),
            "/Users/adityasaurav/.gemini/antigravity/scratch/RiskIntel_AI/data/portfolio/synthetic_portfolio.json",
            "/Users/adityasaurav/.gemini/antigravity/scratch/college-aditya-saurav-hackathon/data/portfolio/synthetic_portfolio.json"
        ]
        for path in candidate_paths:
            if os.path.exists(path):
                try:
                    return cls.load_from_json(path)
                except Exception:
                    continue

        # In-memory full $10M synthetic portfolio fallback
        default_assets = [
            Asset("Corporate Loan A", "Loan", 2000000.0, "Financial Services"),
            Asset("Corporate Loan B", "Loan", 1500000.0, "Technology"),
            Asset("Government Bond", "Bond", 2000000.0, "Government"),
            Asset("Corporate Bond", "Bond", 1500000.0, "Energy"),
            Asset("Equity Portfolio", "Equity", 2000000.0, "Diversified"),
            Asset("Derivative A", "Derivative", 1000000.0, "Financial Services")
        ]
        return cls(default_assets)

    def apply_shocks(self, shocks: Dict[str, float], scale: float = 1.0) -> 'Portfolio':
        """Apply percentage shocks to asset values and return a new Portfolio."""
        new_assets = []
        for asset in self.assets:
            shock_key = asset.asset_type
            if shock_key == 'Bond':
                if 'Government' in asset.name or 'Gov' in asset.name:
                    shock_key = 'Gov Bond'
                else:
                    shock_key = 'Corp Bond'
            
            shock_pct = shocks.get(shock_key, shocks.get(asset.asset_type, 0.0))
            new_value = asset.value * (1 + shock_pct * scale)
            new_assets.append(Asset(asset.name, asset.asset_type, new_value, asset.sector))
            
        return Portfolio(new_assets)

    def to_dataframe(self) -> pd.DataFrame:
        """Return the portfolio as a pandas DataFrame."""
        return pd.DataFrame([vars(a) for a in self.assets])

    def get_asset_breakdown(self) -> Dict[str, float]:
        """Return a breakdown of portfolio value by asset type."""
        breakdown = {}
        for asset in self.assets:
            breakdown[asset.asset_type] = breakdown.get(asset.asset_type, 0.0) + asset.value
        return breakdown
