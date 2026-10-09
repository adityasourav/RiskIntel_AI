"""
Generates high-resolution architecture.png diagram and presentation.pdf
using matplotlib.backends.backend_pdf for the standardized docs/ directory.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Arrow
from matplotlib.backends.backend_pdf import PdfPages

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_architecture_png():
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
    ax.set_facecolor('#0d1117')
    fig.patch.set_facecolor('#0d1117')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, "RiskIntel AI — System Architecture", 
            ha='center', va='center', color='#ffffff', fontsize=20, weight='bold')
    ax.text(7, 9.1, "Real-Time NLP Financial Risk Intelligence & Strategic Portfolio Stress Testing", 
            ha='center', va='center', color='#8b949e', fontsize=12)

    boxes = [
        # Data Sources
        {"xy": (1.5, 7.5), "w": 3.2, "h": 1.0, "title": "Source 1: Financial News", "sub": "GDELT API v2 / News feeds", "c": "#1f6feb"},
        {"xy": (9.3, 7.5), "w": 3.2, "h": 1.0, "title": "Source 2: Social Media", "sub": "Twitter/Financial Tweets", "c": "#1f6feb"},
        # Data Ingestion
        {"xy": (4.5, 6.2), "w": 5.0, "h": 0.8, "title": "Data Ingestion Layer", "sub": "Standardized DataRecord (JSON)", "c": "#238636"},
        # Preprocessing
        {"xy": (4.5, 5.0), "w": 5.0, "h": 0.8, "title": "Text Preprocessing & NER", "sub": "URL cleanup, regex, entity & ticker extraction", "c": "#238636"},
        # Core NLP Engine
        {"xy": (1.0, 3.4), "w": 3.6, "h": 1.1, "title": "FinBERT Sentiment", "sub": "Numerical score: -1.0 to +1.0", "c": "#8957e5"},
        {"xy": (5.2, 3.4), "w": 3.6, "h": 1.1, "title": "Event Classification", "sub": "Zero-shot taxonomy (9 categories)", "c": "#8957e5"},
        {"xy": (9.4, 3.4), "w": 3.6, "h": 1.1, "title": "Impact Scorer", "sub": "Composite framework (1 to 10)", "c": "#8957e5"},
        # Structured Risk Signal
        {"xy": (3.5, 2.1), "w": 7.0, "h": 0.7, "title": "Structured Risk Signal Bus", "sub": "Event + Impact (Trigger threshold >= 7.0)", "c": "#d29922"},
        # Downstream Stress Testing & Dashboard
        {"xy": (1.5, 0.6), "w": 4.8, "h": 1.0, "title": "Module B: Portfolio Stress Simulator", "sub": "$10M synthetic portfolio revaluation & shocks", "c": "#da3633"},
        {"xy": (7.7, 0.6), "w": 4.8, "h": 1.0, "title": "Streamlit Dashboard & FastAPI", "sub": "Live metrics, Plotly shock charts, timeline, REST", "c": "#da3633"},
    ]

    for b in boxes:
        rect = FancyBboxPatch(b["xy"], b["w"], b["h"],
                              boxstyle="round,pad=0.1,rounding_size=0.15",
                              ec=b["c"], fc='#161b22', lw=2)
        ax.add_patch(rect)
        cx = b["xy"][0] + b["w"] / 2.0
        cy = b["xy"][1] + b["h"] / 2.0
        ax.text(cx, cy + 0.16, b["title"], ha='center', va='center', color='#f0f6fc', fontsize=11, weight='bold')
        ax.text(cx, cy - 0.20, b["sub"], ha='center', va='center', color='#8b949e', fontsize=9)

    # Connections
    arrows = [
        ((3.1, 7.5), (6.0, 7.0)),
        ((10.9, 7.5), (8.0, 7.0)),
        ((7.0, 6.2), (7.0, 5.8)),
        ((7.0, 5.0), (7.0, 4.6)),
        ((6.0, 4.6), (2.8, 4.5)),
        ((7.0, 4.6), (7.0, 4.5)),
        ((8.0, 4.6), (11.2, 4.5)),
        ((2.8, 3.4), (5.5, 2.8)),
        ((7.0, 3.4), (7.0, 2.8)),
        ((11.2, 3.4), (8.5, 2.8)),
        ((5.5, 2.1), (3.9, 1.6)),
        ((8.5, 2.1), (10.1, 1.6)),
    ]

    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", color='#58a6ff', lw=1.8, shrinkA=3, shrinkB=3))

    out_png = os.path.join(DOCS_DIR, "architecture.png")
    plt.tight_layout()
    plt.savefig(out_png, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Created {out_png}")


def generate_presentation_pdf():
    out_pdf = os.path.join(DOCS_DIR, "presentation.pdf")
    
    slides = [
        {
            "num": "Slide 1 / 7",
            "title": "RiskIntel AI",
            "subtitle": "Real-Time AI/NLP Financial Risk Intelligence & Strategic Portfolio Stress Testing",
            "bullets": [
                "The Problem: Unstructured information in financial news and social media causes delayed risk detection.",
                "The Solution: Automated NLP extracts structured risk signals (Sentiment, Event Type, Impact Score).",
                "Financial Bridge: Translates high-impact events directly into simulated portfolio stress scenarios.",
                "Candidate: Aditya Saurav | Hackathon Track: Strategic Financial Risk Management"
            ]
        },
        {
            "num": "Slide 2 / 7",
            "title": "System Architecture & Data Flow",
            "subtitle": "End-to-end modular pipeline from unstructured inputs to executive dashboard",
            "bullets": [
                "Two Distinct Data Sources: Global News (GDELT API v2) & Social Discussion (Financial Tweets).",
                "Unified Ingestion Schema: Standardized DataRecord abstraction regardless of origin.",
                "NLP Pipeline: FinBERT Sentiment (-1.0 to +1.0) + Zero-Shot Event Classifier (9 categories).",
                "Decision Core: Composite Impact Scorer (1-10) with automatic stress test trigger threshold >= 7.0.",
                "Dual Consumption: Executive Streamlit Dashboard + Production-grade FastAPI REST endpoints."
            ]
        },
        {
            "num": "Slide 3 / 7",
            "title": "Core NLP Risk Engine",
            "subtitle": "Transforming unstructured text into machine-readable risk signals",
            "bullets": [
                "Sentiment Analysis: ProsusAI/FinBERT tailored to financial jargon (positive, negative, neutral).",
                "Event Classification: 9-class financial taxonomy (Geopolitical, Macroeconomic, Credit, Regulatory, etc.).",
                "Impact Score (1-10): Transparent multi-factor model (Severity, Sentiment Magnitude, Entity, Urgency).",
                "Explainable Formulation: Impact = 0.35 x Severity + 0.20 x |Sentiment| + 0.25 x Entity + 0.20 x Urgency.",
                "Standard Output: Structured RiskSignal JSON contract consumable by downstream systems."
            ]
        },
        {
            "num": "Slide 4 / 7",
            "title": "Module B: Strategic Portfolio Stress Testing",
            "subtitle": "Connecting qualitative textual intelligence directly to capital preservation",
            "bullets": [
                "Synthetic $10.0M Portfolio: 6 assets spanning Corporate Loans, Govt/Corp Bonds, Equities, & Derivatives.",
                "Event-Scenario Shock Matrix: Pre-calibrated macro shock profiles for each event classification.",
                "Dynamic Shock Scaling: Severity scales with textual impact (Shock% = Base Shock x Impact / 10).",
                "Asset-Level Revaluation: Granular tracking of safe-haven flows (Govt Bonds +) vs vulnerable assets (-)."
            ]
        },
        {
            "num": "Slide 5 / 7",
            "title": "Live Demonstration & Results",
            "subtitle": "Real-world test case evaluation: US-China tariff escalation",
            "bullets": [
                "Input Headline: 'US announces new tariffs on Chinese imports, raising concerns about global trade.'",
                "Signal Detected: Entity: US | Sentiment: -0.85 | Event: Geopolitical | Impact: 7.9/10 | Risk: HIGH.",
                "Automated Action: Stress test triggered automatically (Threshold >= 7.0 satisfied).",
                "Portfolio Before: $10,000,000  -->  Portfolio After: $9,545,750.",
                "Simulated Loss: $454,250 (-4.54%) | Derivative shock -9.48%, Equity shock -7.90%."
            ]
        },
        {
            "num": "Slide 6 / 7",
            "title": "Technology Stack & Engineering Highlights",
            "subtitle": "Production-ready engineering designed for reliability and zero downtime",
            "bullets": [
                "Core Engine: Python 3.10+, Pandas, NumPy, Hugging Face Transformers, PyTorch.",
                "APIs & Services: FastAPI with Swagger UI, Uvicorn asynchronous server, CORS enabled.",
                "Visual Analytics: Streamlit with dark theme, responsive Plotly interactive shock charts.",
                "Testing & Resilience: 12/12 automated unit tests passing, zero-dependency offline domain fallbacks."
            ]
        },
        {
            "num": "Slide 7 / 7",
            "title": "Conclusion & Roadmap",
            "subtitle": "Bridging NLP intelligence and quantitative risk engineering",
            "bullets": [
                "Key Achievement: Fully functioning end-to-end prototype delivered within strict constraints.",
                "Explainability: Clear mathematical audit trail from textual keyword to dollar portfolio loss.",
                "Future Roadmap: Kafka streaming ingestion, fine-tuned transformer event classifiers,",
                "Markowitz portfolio rebalancing, and historical backtesting against past crises."
            ]
        }
    ]

    with PdfPages(out_pdf) as pdf:
        for slide in slides:
            fig, ax = plt.subplots(figsize=(11, 6.5), dpi=150)
            fig.patch.set_facecolor('#0d1117')
            ax.set_facecolor('#0d1117')
            ax.set_xlim(0, 11)
            ax.set_ylim(0, 6.5)
            ax.axis('off')

            # Header
            ax.text(0.8, 5.8, slide["num"], color='#58a6ff', fontsize=11, weight='bold')
            ax.text(0.8, 5.2, slide["title"], color='#ffffff', fontsize=22, weight='bold')
            ax.text(0.8, 4.7, slide["subtitle"], color='#8b949e', fontsize=12)

            # Divider
            ax.plot([0.8, 10.2], [4.4, 4.4], color='#30363d', lw=1.5)

            # Bullets
            y = 3.8
            for bullet in slide["bullets"]:
                ax.plot([0.9], [y], marker='s', color='#238636', markersize=6)
                ax.text(1.2, y - 0.08, bullet, color='#e6edf3', fontsize=11, wrap=True)
                y -= 0.65

            # Footer
            ax.text(0.8, 0.4, "RiskIntel AI — Hackathon Submission", color='#8b949e', fontsize=9)
            ax.text(10.2, 0.4, "Aditya Saurav", color='#8b949e', fontsize=9, ha='right')

            plt.tight_layout()
            pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close()

    print(f"Created {out_pdf}")

if __name__ == "__main__":
    generate_architecture_png()
    generate_presentation_pdf()
