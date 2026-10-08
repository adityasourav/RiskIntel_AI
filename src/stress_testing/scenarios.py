from dataclasses import dataclass
from typing import Dict

@dataclass
class StressScenario:
    """Represents a stress test scenario with associated asset shocks."""
    name: str
    event_type: str
    description: str
    shocks: Dict[str, float]

SCENARIOS = {
    'Geopolitical': StressScenario(
        name='Geopolitical Stress Scenario',
        event_type='Geopolitical',
        description='Shocks due to geopolitical tensions',
        shocks={'Equity': -0.10, 'Corp Bond': -0.08, 'Gov Bond': +0.02, 'Loan': -0.05, 'Derivative': -0.12}
    ),
    'Macroeconomic': StressScenario(
        name='Macroeconomic Stress Scenario',
        event_type='Macroeconomic',
        description='Shocks due to macroeconomic conditions',
        shocks={'Equity': -0.07, 'Corp Bond': -0.05, 'Gov Bond': -0.03, 'Loan': -0.04, 'Derivative': -0.08}
    ),
    'Credit Event': StressScenario(
        name='Credit Event Stress Scenario',
        event_type='Credit Event',
        description='Shocks due to credit defaults or rating downgrades',
        shocks={'Equity': -0.05, 'Corp Bond': -0.12, 'Gov Bond': +0.01, 'Loan': -0.15, 'Derivative': -0.10}
    ),
    'Regulatory': StressScenario(
        name='Regulatory Stress Scenario',
        event_type='Regulatory',
        description='Shocks due to regulatory changes',
        shocks={'Equity': -0.06, 'Corp Bond': -0.04, 'Gov Bond': 0.00, 'Loan': -0.03, 'Derivative': -0.07}
    ),
    'Merger and Acquisition': StressScenario(
        name='M&A Stress Scenario',
        event_type='Merger and Acquisition',
        description='Shocks due to M&A activities',
        shocks={'Equity': -0.03, 'Corp Bond': -0.02, 'Gov Bond': 0.00, 'Loan': -0.01, 'Derivative': -0.05}
    ),
    'Earnings and Financial Results': StressScenario(
        name='Earnings Stress Scenario',
        event_type='Earnings and Financial Results',
        description='Shocks due to earnings reports',
        shocks={'Equity': -0.04, 'Corp Bond': -0.03, 'Gov Bond': 0.00, 'Loan': -0.02, 'Derivative': -0.06}
    ),
    'Market and Financial': StressScenario(
        name='Market Stress Scenario',
        event_type='Market and Financial',
        description='Shocks due to market volatility',
        shocks={'Equity': -0.08, 'Corp Bond': -0.06, 'Gov Bond': +0.01, 'Loan': -0.03, 'Derivative': -0.09}
    ),
    'Product Launch': StressScenario(
        name='Product Launch Stress Scenario',
        event_type='Product Launch',
        description='Shocks due to product launches',
        shocks={'Equity': -0.02, 'Corp Bond': -0.01, 'Gov Bond': 0.00, 'Loan': -0.01, 'Derivative': -0.02}
    ),
    'Other': StressScenario(
        name='Other Stress Scenario',
        event_type='Other',
        description='General shocks for uncategorized events',
        shocks={'Equity': -0.02, 'Corp Bond': -0.01, 'Gov Bond': 0.00, 'Loan': -0.01, 'Derivative': -0.02}
    )
}

def get_scenario(event_type: str) -> StressScenario:
    """Retrieve a stress scenario by event type."""
    return SCENARIOS.get(event_type, get_default_scenario())

def get_default_scenario() -> StressScenario:
    """Retrieve the default stress scenario."""
    return SCENARIOS['Other']
