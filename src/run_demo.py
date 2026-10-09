#!/usr/bin/env python3
"""
RiskIntel AI — End-to-End Demo Script

Demonstrates the complete pipeline:
  Unstructured text → NLP Risk Engine → Structured signals → Stress test → Results

Usage:
    python run_demo.py
"""

import json
import sys
import os
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def print_header(text: str, char: str = "=") -> None:
    """Print a formatted header."""
    width = 70
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}\n")


def print_step(step: int, text: str) -> None:
    """Print a step indicator."""
    print(f"  [{step}] {text}")


def print_signal(signal) -> None:
    """Pretty-print a RiskSignal."""
    print(f"    ┌{'─' * 60}┐")
    print(f"    │ {'Entity:':<18} {signal.entity:<40} │")
    print(f"    │ {'Sentiment:':<18} {signal.sentiment_score:>+.2f} ({signal.sentiment_label}){' ' * (28 - len(signal.sentiment_label))}│")
    print(f"    │ {'Event Type:':<18} {signal.event_type:<40} │")
    print(f"    │ {'Impact Score:':<18} {signal.impact_score:.1f}/10{' ' * 35}│")
    print(f"    │ {'Risk Level:':<18} {signal.risk_level:<40} │")
    print(f"    └{'─' * 60}┘")


def run_demo():
    """Run the complete RiskIntel AI demo."""
    print_header("RiskIntel AI — NLP Financial Risk Intelligence Platform", "━")
    print("  Real-Time AI/NLP Financial Risk Intelligence & Stress Testing")
    print("  " + "─" * 60)

    # ── Demo texts ──────────────────────────────────────────────
    demo_texts = [
        {
            "text": "US announces new tariffs on Chinese imports, raising concerns about global trade disruption and potential retaliatory measures.",
            "source": "news",
        },
        {
            "text": "Federal Reserve raises interest rates by 50 basis points amid persistent inflation concerns.",
            "source": "news",
        },
        {
            "text": "Apple reports stronger-than-expected Q3 earnings, revenue up 12% year-over-year.",
            "source": "news",
        },
        {
            "text": "$TSLA stock crashing after massive recall announcement, investors fleeing",
            "source": "social",
        },
        {
            "text": "Major credit rating agency downgrades three large European banks citing liquidity concerns.",
            "source": "news",
        },
    ]

    # ── Phase 1: Initialize Engine ──────────────────────────────
    print_header("Phase 1: Initializing NLP Risk Engine")
    print_step(1, "Loading text preprocessor...")
    print_step(2, "Loading FinBERT sentiment model...")
    print_step(3, "Loading zero-shot event classifier...")
    print_step(4, "Loading impact scoring framework...")
    print()

    from risk_engine.engine import RiskEngine
    engine = RiskEngine()
    print("  [OK] Risk Engine initialized successfully\n")

    # ── Phase 2: Process Texts ──────────────────────────────────
    print_header("Phase 2: Processing Financial Texts")

    signals = []
    for i, item in enumerate(demo_texts, 1):
        print(f"\n  Text {i}/{len(demo_texts)}:")
        print(f"     \"{item['text'][:80]}...\"" if len(item['text']) > 80 else f"     \"{item['text']}\"")
        print(f"     Source: {item['source']}")
        print()

        start = time.time()
        signal = engine.analyze(text=item["text"], source=item["source"])
        elapsed = time.time() - start

        print_signal(signal)
        print(f"    Processed in {elapsed:.2f}s\n")
        signals.append(signal)

    # ── Phase 3: Risk Summary ───────────────────────────────────
    print_header("Phase 3: Risk Signal Summary")

    high_risk = [s for s in signals if s.risk_level == "HIGH"]
    medium_risk = [s for s in signals if s.risk_level == "MEDIUM"]
    low_risk = [s for s in signals if s.risk_level == "LOW"]

    print(f"  Total Signals:  {len(signals)}")
    print(f"  [HIGH Risk]:    {len(high_risk)}")
    print(f"  [MEDIUM Risk]:  {len(medium_risk)}")
    print(f"  [LOW Risk]:     {len(low_risk)}")

    # ── Phase 4: Stress Testing ─────────────────────────────────
    print_header("Phase 4: Portfolio Stress Testing")

    from stress_testing.portfolio import Portfolio
    from stress_testing.simulator import StressTestSimulator

    portfolio = Portfolio.load_default(base_dir=str(PROJECT_ROOT))
    simulator = StressTestSimulator(portfolio=portfolio)

    print(f"  Portfolio: {portfolio.total_value:,.0f} USD")
    print(f"  Assets: {len(portfolio.assets)}")
    print()

    # Find highest impact signal for stress test
    if high_risk:
        worst_signal = max(high_risk, key=lambda s: s.impact_score)
        print(f"  [ALERT] HIGH IMPACT EVENT DETECTED:")
        print(f"     Event: {worst_signal.event_type}")
        print(f"     Impact: {worst_signal.impact_score:.1f}/10")
        print(f"     Triggering stress test...\n")

        result = simulator.run_stress_test(worst_signal.to_dict())

        print(result.to_summary_string())

        # Save result
        results_path = PROJECT_ROOT / "data" / "processed"
        results_path.mkdir(parents=True, exist_ok=True)
        with open(results_path / "stress_test_result.json", "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"\n  Stress test result saved to data/processed/stress_test_result.json")
    else:
        print("  [OK] No HIGH risk events detected. No stress test triggered.")

    # ── Phase 5: Save Signals ───────────────────────────────────
    print_header("Phase 5: Saving Results")

    output_path = engine.save_signals(signals)
    print(f"  Risk signals saved to: {output_path}")

    # Print sample JSON output
    print("\n  Sample Risk Signal (JSON):")
    if signals:
        sample = signals[0]
        print(json.dumps({
            "timestamp": sample.timestamp,
            "source": sample.source,
            "entity": sample.entity,
            "sentiment_score": sample.sentiment_score,
            "event_type": sample.event_type,
            "impact_score": sample.impact_score,
            "risk_level": sample.risk_level,
        }, indent=4))

    # ── Done ────────────────────────────────────────────────────
    print_header("Demo Complete!", "━")
    print("  Next steps:")
    print("    - Run the dashboard:  streamlit run dashboard/app.py")
    print("    - Run the API:        uvicorn api.main:app --reload")
    print("    - Run tests:          python -m pytest tests/ -v")
    print()


if __name__ == "__main__":
    run_demo()
