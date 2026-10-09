"""
RiskIntel AI - Streamlit Dashboard

Interactive dashboard for financial risk intelligence and portfolio stress testing.
Provides real-time NLP analysis of financial text with portfolio stress simulation.

Usage:
    streamlit run src/dashboard/app.py
    # or
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path
import json
import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -- Path Resolution -----------------------------------------------------------
FILE_PATH = Path(__file__).resolve()
DASHBOARD_DIR = FILE_PATH.parent

possible_roots = [
    DASHBOARD_DIR.parent,         # Repo root if dashboard/ is at root, or src/ if in src/dashboard
    DASHBOARD_DIR.parent.parent,  # Repo root if in src/dashboard
    Path.cwd(),
    Path.home() / "Desktop" / "college-aditya-saurav-hackathon",
    Path("/Users/adityasaurav/.gemini/antigravity/scratch/RiskIntel_AI"),
]

REPO_ROOT = DASHBOARD_DIR.parent
for root in possible_roots:
    if (root / "data" / "sample").exists() or (root / "data" / "portfolio").exists():
        REPO_ROOT = root
        break

DATA_DIR = REPO_ROOT / "data"

for candidate in [
    REPO_ROOT,
    REPO_ROOT / "src",
    DASHBOARD_DIR.parent,
    DASHBOARD_DIR.parent / "src",
]:
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

# Attempt to load backend modules
try:
    from risk_engine.engine import RiskEngine
    from stress_testing.portfolio import Portfolio
    from stress_testing.simulator import StressTestSimulator
    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    _IMPORT_ERROR = str(e)


# -- Fallback Sample Data ------------------------------------------------------
SAMPLE_NEWS_FALLBACK = [
    {
        "source": "news",
        "timestamp": "2026-10-01T10:00:00Z",
        "title": "US announces new tariffs on Chinese imports",
        "text": "US announces new tariffs on Chinese imports. Markets react negatively.",
        "entity": "US",
        "url": "http://example.com/news/1"
    },
    {
        "source": "news",
        "timestamp": "2026-10-02T11:00:00Z",
        "title": "Federal Reserve raises interest rates by 50 basis points",
        "text": "Federal Reserve raises interest rates by 50 basis points to combat inflation.",
        "entity": "Federal Reserve",
        "url": "http://example.com/news/2"
    },
    {
        "source": "news",
        "timestamp": "2026-10-03T09:30:00Z",
        "title": "Apple reports stronger-than-expected Q3 earnings",
        "text": "Apple reports stronger-than-expected Q3 earnings, sending stock soaring.",
        "entity": "Apple",
        "url": "http://example.com/news/3"
    },
    {
        "source": "news",
        "timestamp": "2026-10-04T14:15:00Z",
        "title": "Major bank faces regulatory investigation",
        "text": "Major bank faces regulatory investigation over mortgage lending practices.",
        "entity": "Major Bank",
        "url": "http://example.com/news/4"
    },
    {
        "source": "news",
        "timestamp": "2026-10-05T08:45:00Z",
        "title": "Oil prices surge amid Middle East tensions",
        "text": "Oil prices surge amid Middle East tensions, causing concern for global supply.",
        "entity": "Oil",
        "url": "http://example.com/news/5"
    },
    {
        "source": "news",
        "timestamp": "2026-10-06T13:00:00Z",
        "title": "European Central Bank signals rate cut",
        "text": "European Central Bank signals rate cut as economic growth slows.",
        "entity": "European Central Bank",
        "url": "http://example.com/news/6"
    },
    {
        "source": "news",
        "timestamp": "2026-10-07T16:20:00Z",
        "title": "Tech giant announces $10B acquisition",
        "text": "Tech giant announces $10B acquisition of AI startup.",
        "entity": "Tech Giant",
        "url": "http://example.com/news/7"
    },
    {
        "source": "news",
        "timestamp": "2026-10-08T09:10:00Z",
        "title": "Credit rating agency downgrades major corporation",
        "text": "Credit rating agency downgrades major corporation due to debt levels.",
        "entity": "Major Corporation",
        "url": "http://example.com/news/8"
    },
    {
        "source": "news",
        "timestamp": "2026-10-08T11:40:00Z",
        "title": "New trade agreement signed between US and EU",
        "text": "New trade agreement signed between US and EU, boosting cross-border commerce.",
        "entity": "US",
        "url": "http://example.com/news/9"
    },
    {
        "source": "news",
        "timestamp": "2026-10-08T15:55:00Z",
        "title": "Company announces major product recall",
        "text": "Company announces major product recall following safety concerns.",
        "entity": "Company",
        "url": "http://example.com/news/10"
    }
]

SAMPLE_SOCIAL_FALLBACK = [
    {
        "source": "social",
        "timestamp": "2026-10-01T09:00:00Z",
        "title": "$AAPL earnings crushed expectations!",
        "text": "$AAPL earnings crushed expectations!",
        "entity": "AAPL"
    },
    {
        "source": "social",
        "timestamp": "2026-10-02T10:30:00Z",
        "title": "Fed rate hike is going to destroy the housing market",
        "text": "Fed rate hike is going to destroy the housing market",
        "entity": "Fed"
    },
    {
        "source": "social",
        "timestamp": "2026-10-03T12:15:00Z",
        "title": "Just sold all my $TSLA shares",
        "text": "Just sold all my $TSLA shares, this company is done",
        "entity": "TSLA"
    },
    {
        "source": "social",
        "timestamp": "2026-10-04T14:45:00Z",
        "title": "China retaliates with tariffs on US goods",
        "text": "Breaking: China retaliates with tariffs on US goods",
        "entity": "China"
    },
    {
        "source": "social",
        "timestamp": "2026-10-05T08:20:00Z",
        "title": "$SPY hitting all-time highs",
        "text": "$SPY hitting all-time highs, bears in shambles",
        "entity": "SPY"
    },
    {
        "source": "social",
        "timestamp": "2026-10-06T16:50:00Z",
        "title": "Massive insider selling at $META",
        "text": "Massive insider selling at $META, something is wrong",
        "entity": "META"
    },
    {
        "source": "social",
        "timestamp": "2026-10-07T11:10:00Z",
        "title": "Gold surging as geopolitical tensions rise",
        "text": "Gold surging as geopolitical tensions rise",
        "entity": "Gold"
    },
    {
        "source": "social",
        "timestamp": "2026-10-08T09:30:00Z",
        "title": "Banking crisis fears spreading to European markets",
        "text": "Banking crisis fears spreading to European markets",
        "entity": "Banking"
    },
    {
        "source": "social",
        "timestamp": "2026-10-08T13:45:00Z",
        "title": "$NVDA AI hype is real",
        "text": "$NVDA AI hype is real, revenue up 200%",
        "entity": "NVDA"
    },
    {
        "source": "social",
        "timestamp": "2026-10-08T15:20:00Z",
        "title": "Credit default swaps widening",
        "text": "Credit default swaps widening, recession incoming",
        "entity": "Credit default swaps"
    }
]


# -- Caching Helpers -----------------------------------------------------------
@st.cache_data
def load_sample_news_data() -> list:
    """Load sample news data with multi-path resolution and reliable fallback."""
    candidate_paths = [
        DATA_DIR / "sample" / "sample_news.json",
        REPO_ROOT / "data" / "sample" / "sample_news.json",
        Path.cwd() / "data" / "sample" / "sample_news.json",
        Path.home() / "Desktop" / "college-aditya-saurav-hackathon" / "data" / "sample" / "sample_news.json",
        Path("/Users/adityasaurav/.gemini/antigravity/scratch/RiskIntel_AI/data/sample/sample_news.json"),
    ]
    for p in candidate_paths:
        if p and p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data and isinstance(data, list):
                    return data
            except Exception:
                continue
    return SAMPLE_NEWS_FALLBACK


@st.cache_data
def load_sample_social_data() -> list:
    """Load sample social data with multi-path resolution and reliable fallback."""
    candidate_paths = [
        DATA_DIR / "sample" / "sample_social.json",
        REPO_ROOT / "data" / "sample" / "sample_social.json",
        Path.cwd() / "data" / "sample" / "sample_social.json",
        Path.home() / "Desktop" / "college-aditya-saurav-hackathon" / "data" / "sample" / "sample_social.json",
        Path("/Users/adityasaurav/.gemini/antigravity/scratch/RiskIntel_AI/data/sample/sample_social.json"),
    ]
    for p in candidate_paths:
        if p and p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data and isinstance(data, list):
                    return data
            except Exception:
                continue
    return SAMPLE_SOCIAL_FALLBACK


@st.cache_resource
def load_engine():
    return RiskEngine()


@st.cache_resource
def load_portfolio():
    return Portfolio.load_default(base_dir=str(REPO_ROOT))


# -- UI Helper Functions -------------------------------------------------------
def get_risk_badge(level: str) -> str:
    level = level.upper()
    css_map = {"HIGH": "risk-high", "MEDIUM": "risk-medium", "LOW": "risk-low"}
    css_class = css_map.get(level, "risk-low")
    return f"<span class='risk-badge {css_class}'>{level}</span>"


# -- Page Config & CSS ---------------------------------------------------------
st.set_page_config(
    page_title="RiskIntel AI",
    layout="wide",
)

st.markdown("""
<style>
    .risk-badge {
        display: inline-block;
        padding: 0.35em 0.8em;
        font-size: 18px;
        font-weight: 700;
        color: white;
        text-align: center;
        border-radius: 0.3rem;
        letter-spacing: 0.5px;
    }
    .risk-high   { background-color: #dc3545; }
    .risk-medium { background-color: #ffc107; color: #212529; }
    .risk-low    { background-color: #28a745; }
    .kpi-box {
        background: #1e1e2f;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 1px solid #333;
    }
    .kpi-label { font-size: 14px; color: #aaa; margin-bottom: 4px; }
    .kpi-value { font-size: 28px; font-weight: bold; }
    div[data-testid="stMetric"] { background: #0e1117; border: 1px solid #333; border-radius: 8px; padding: 12px; }
</style>
""", unsafe_allow_html=True)


# -- Session State -------------------------------------------------------------
if "signals" not in st.session_state:
    st.session_state["signals"] = []
if "stress_results" not in st.session_state:
    st.session_state["stress_results"] = []
if "latest_signals" not in st.session_state:
    st.session_state["latest_signals"] = []


def main():
    # -- Sidebar Controls ------------------------------------------------------
    st.sidebar.markdown("# RiskIntel AI")
    st.sidebar.markdown("*NLP Financial Risk Intelligence*")
    st.sidebar.markdown("---")

    data_source = st.sidebar.radio(
        "Data Source",
        ["Manual Input", "Sample News Data", "Sample Social Data", "GDELT Live Feed"],
    )

    texts_to_analyze = []
    analysis_source = "manual"

    if data_source == "Manual Input":
        manual_text = st.sidebar.text_area(
            "Enter Financial Text",
            "US announces new tariffs on Chinese imports, raising concerns about global trade disruption and potential retaliatory measures.",
            height=120,
        )
        if manual_text.strip():
            texts_to_analyze = [manual_text.strip()]
        analysis_source = "manual"

    elif data_source == "Sample News Data":
        news_items = load_sample_news_data()
        options = ["Analyze All 10 Articles"] + [
            f"{i+1}. {item.get('title') or item.get('text', '')[:45]}"
            for i, item in enumerate(news_items)
        ]
        selected_news = st.sidebar.selectbox("Select Sample News Article", options)
        analysis_source = "news"

        if selected_news == "Analyze All 10 Articles":
            texts_to_analyze = [item.get("text", "") for item in news_items if item.get("text")]
            st.sidebar.info(f"Loaded {len(texts_to_analyze)} sample news articles for batch analysis.")
        else:
            idx = int(selected_news.split(".")[0]) - 1
            item = news_items[idx]
            texts_to_analyze = [item.get("text", "")]
            st.sidebar.text_area("Selected Article Preview", item.get("text", ""), height=100, disabled=True)

    elif data_source == "Sample Social Data":
        social_items = load_sample_social_data()
        options = ["Analyze All 10 Posts"] + [
            f"{i+1}. {item.get('text', '')[:45]}"
            for i, item in enumerate(social_items)
        ]
        selected_social = st.sidebar.selectbox("Select Sample Social Post", options)
        analysis_source = "social"

        if selected_social == "Analyze All 10 Posts":
            texts_to_analyze = [item.get("text", "") for item in social_items if item.get("text")]
            st.sidebar.info(f"Loaded {len(texts_to_analyze)} sample social posts for batch analysis.")
        else:
            idx = int(selected_social.split(".")[0]) - 1
            item = social_items[idx]
            texts_to_analyze = [item.get("text", "")]
            st.sidebar.text_area("Selected Post Preview", item.get("text", ""), height=100, disabled=True)

    elif data_source == "GDELT Live Feed":
        gdelt_keyword = st.sidebar.text_input("Search Keyword", "tariffs")
        analysis_source = "GDELT"

    st.sidebar.markdown("---")
    run_btn = st.sidebar.button("Run Risk Analysis", type="primary", use_container_width=True)

    st.sidebar.markdown("---")
    if st.sidebar.button("Clear History", use_container_width=True):
        st.session_state["signals"] = []
        st.session_state["stress_results"] = []
        st.session_state["latest_signals"] = []
        st.rerun()

    # -- Main Header -----------------------------------------------------------
    st.title("RiskIntel AI Dashboard")
    st.caption("Real-Time AI/NLP Financial Risk Intelligence & Portfolio Stress Testing")

    if not BACKEND_AVAILABLE:
        st.error(
            f"Backend modules not available. Please install dependencies: pip install -r requirements.txt\n\n"
            f"Error: {_IMPORT_ERROR}"
        )
        return

    # -- Run Analysis ----------------------------------------------------------
    if run_btn:
        progress = st.progress(0)
        status = st.empty()

        # Step 1: Load models
        status.text("Loading NLP models...")
        progress.progress(10)
        engine = load_engine()
        portfolio = load_portfolio()
        simulator = StressTestSimulator(portfolio=portfolio)
        progress.progress(25)

        # Step 2: Handle live fetch if applicable
        if data_source == "GDELT Live Feed":
            status.text("Fetching from GDELT...")
            try:
                from ingestion.gdelt_source import GdeltSource
                gdelt = GdeltSource()
                records = gdelt.fetch(keyword=gdelt_keyword or "finance", max_results=10)
                texts_to_analyze = [r.text for r in records if r.text]
            except Exception as e:
                st.warning(f"GDELT fetch failed: {e}. Using sample news data.")
                news_items = load_sample_news_data()
                texts_to_analyze = [item.get("text", "") for item in news_items if item.get("text")]

        progress.progress(40)

        if not texts_to_analyze:
            st.error("No text to analyze. Please enter text or select a valid data source.")
            progress.empty()
            status.empty()
            return

        # Step 3: Run NLP analysis
        status.text(f"Running NLP Risk Engine on {len(texts_to_analyze)} text(s)...")
        new_signals = []
        try:
            for i, text in enumerate(texts_to_analyze):
                signal = engine.analyze(text=text, source=analysis_source)
                new_signals.append(signal)
                pct = 40 + int(50 * (i + 1) / len(texts_to_analyze))
                progress.progress(min(pct, 90))
        except Exception as e:
            st.error(f"Analysis error: {e}\n\nPlease verify model dependencies.")
            progress.empty()
            status.empty()
            return

        # Store signals in session state
        for sig in new_signals:
            st.session_state["signals"].append({
                "Timestamp": sig.timestamp[:19],
                "Source": sig.source,
                "Entity": sig.entity,
                "Sentiment": round(sig.sentiment_score, 2),
                "Event": sig.event_type,
                "Impact": round(sig.impact_score, 1),
                "Risk Level": sig.risk_level,
            })
        st.session_state["latest_signals"] = new_signals

        progress.progress(100)
        status.text("Analysis complete.")
        time.sleep(0.4)
        progress.empty()
        status.empty()

    # -- Display Results -------------------------------------------------------
    latest = st.session_state.get("latest_signals", [])

    if latest:
        # Sort by impact score descending
        latest_sorted = sorted(latest, key=lambda s: s.impact_score, reverse=True)
        top = latest_sorted[0]

        # Section 0: KPI Cards
        st.markdown("---")
        k1, k2, k3, k4 = st.columns(4)

        with k1:
            delta_color = "normal" if top.sentiment_score >= 0 else "inverse"
            st.metric("Sentiment Score", f"{top.sentiment_score:+.2f}", delta=top.sentiment_label, delta_color=delta_color)
        with k2:
            st.metric("Event Type", top.event_type)
        with k3:
            st.metric("Impact Score", f"{top.impact_score:.1f} / 10")
        with k4:
            st.markdown(f"**Risk Level**<br>{get_risk_badge(top.risk_level)}", unsafe_allow_html=True)

        # Section 1: Analysis Details
        st.markdown("---")
        st.subheader("Analysis Results")

        if len(latest_sorted) == 1:
            st.info(f'**Analyzed Text:** "{top.original_text}"')
        else:
            st.info(f"Analyzed **{len(latest_sorted)}** texts. Showing highest-impact result below.")

        with st.expander("Detailed Breakdown", expanded=True):
            d1, d2, d3 = st.columns(3)
            with d1:
                st.markdown("**Sentiment**")
                st.json({
                    "label": top.sentiment_label,
                    "score": top.sentiment_score,
                })
            with d2:
                st.markdown("**Event Classification**")
                st.json({
                    "event_type": top.event_type,
                    "confidence": round(top.event_confidence, 3),
                })
            with d3:
                st.markdown("**Impact Scoring**")
                st.json({
                    "score": top.impact_score,
                    "risk_level": top.risk_level,
                    "components": {k: round(v, 2) for k, v in top.impact_components.items()} if top.impact_components else {},
                })

        with st.expander("Full Risk Signal JSON"):
            st.json(top.to_dict())

        # Show all results if multiple
        if len(latest_sorted) > 1:
            with st.expander(f"All {len(latest_sorted)} Analyzed Signals"):
                for i, sig in enumerate(latest_sorted):
                    st.markdown(
                        f"**[{sig.risk_level}] {sig.event_type}** | "
                        f"Sentiment: `{sig.sentiment_score:+.2f}` | "
                        f"Impact: `{sig.impact_score:.1f}` | "
                        f"Entity: `{sig.entity}`"
                    )
                    st.caption(f'"{sig.original_text[:110]}..."' if len(sig.original_text) > 110 else f'"{sig.original_text}"')
                    if i < len(latest_sorted) - 1:
                        st.markdown("---")

        # Section 2: Portfolio Stress Test
        high_risk = [s for s in latest_sorted if s.risk_level == "HIGH"]

        if high_risk:
            st.markdown("---")
            st.subheader("Portfolio Stress Test")
            st.error("HIGH IMPACT EVENT DETECTED - Stress Test Triggered")

            worst = high_risk[0]
            portfolio = load_portfolio()
            simulator = StressTestSimulator(portfolio=portfolio)
            stress_result = simulator.run_stress_test(worst.to_dict())

            if stress_result.triggered:
                # Key stress metrics
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Portfolio Before", f"${stress_result.portfolio_before:,.0f}")
                with m2:
                    st.metric("Portfolio After", f"${stress_result.portfolio_after:,.0f}")
                with m3:
                    st.metric("Total Loss", f"${stress_result.total_loss:,.0f}", delta=f"-{stress_result.loss_percentage:.1f}%", delta_color="inverse")
                with m4:
                    st.metric("Scenario", stress_result.scenario_name.split(" Stress")[0])

                # Two columns: composition table + impact bar chart
                tc1, tc2 = st.columns([1, 2])

                with tc1:
                    st.markdown("**Portfolio Composition**")
                    portfolio_df = portfolio.to_dataframe()
                    portfolio_df["value"] = portfolio_df["value"].apply(lambda x: f"${x:,.0f}")
                    st.dataframe(portfolio_df, use_container_width=True, hide_index=True)

                with tc2:
                    st.markdown("**Asset Impact Under Stress**")
                    fig = go.Figure(go.Bar(
                        x=[imp.change_pct for imp in stress_result.asset_impacts],
                        y=[f"{imp.asset_name}" for imp in stress_result.asset_impacts],
                        orientation="h",
                        marker_color=[
                            "#dc3545" if imp.change_pct < 0 else "#28a745"
                            for imp in stress_result.asset_impacts
                        ],
                        text=[f"{imp.change_pct:+.1f}%" for imp in stress_result.asset_impacts],
                        textposition="auto",
                    ))
                    fig.update_layout(
                        xaxis_title="Change (%)",
                        yaxis_title="",
                        height=350,
                        margin=dict(l=10, r=10, t=10, b=40),
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="white"),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.session_state["stress_results"].append(stress_result.to_dict())
        else:
            st.markdown("---")
            st.success("No HIGH risk events detected. Stress test not triggered.")

    # Section 3: Risk Signal History
    if st.session_state["signals"]:
        st.markdown("---")
        st.subheader("Risk Signal History")

        df_history = pd.DataFrame(st.session_state["signals"])
        st.dataframe(df_history, use_container_width=True, hide_index=True)

        col_dl1, col_dl2, _ = st.columns([1, 1, 3])
        with col_dl1:
            csv = df_history.to_csv(index=False).encode("utf-8")
            st.download_button("Export CSV", data=csv, file_name="risk_signals.csv", mime="text/csv")
        with col_dl2:
            json_str = json.dumps(st.session_state["signals"], indent=2)
            st.download_button("Export JSON", data=json_str, file_name="risk_signals.json", mime="application/json")

        # Section 4: Risk Timeline & Charts
        st.markdown("---")
        st.subheader("Risk Analytics")

        df_chart = df_history.copy()
        df_chart["Impact"] = pd.to_numeric(df_chart["Impact"])
        df_chart["Sentiment"] = pd.to_numeric(df_chart["Sentiment"])
        df_chart["idx"] = range(1, len(df_chart) + 1)

        ch1, ch2 = st.columns(2)
        with ch1:
            fig_line = px.line(
                df_chart, x="idx", y="Impact",
                title="Impact Scores Over Time",
                markers=True,
                labels={"idx": "Signal Index", "Impact": "Impact Score"},
            )
            fig_line.update_layout(
                height=350,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
            )
            fig_line.add_hline(y=7.0, line_dash="dash", line_color="red", annotation_text="HIGH threshold (7.0)")
            st.plotly_chart(fig_line, use_container_width=True)

        with ch2:
            fig_scatter = px.scatter(
                df_chart, x="Sentiment", y="Impact",
                color="Event",
                size="Impact",
                title="Sentiment vs Impact by Event Type",
                labels={"Sentiment": "Sentiment Score", "Impact": "Impact Score"},
                hover_data=["Entity", "Risk Level"],
            )
            fig_scatter.update_layout(
                height=350,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
            )
            fig_scatter.add_hline(y=7.0, line_dash="dash", line_color="red")
            fig_scatter.add_vline(x=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_scatter, use_container_width=True)

    elif not latest:
        # Initial Landing State
        st.markdown("---")
        st.markdown(
            """
            ### Welcome to RiskIntel AI

            **Getting Started:**
            1. Select a **Data Source** from the sidebar (*Manual Input*, *Sample News Data*, *Sample Social Data*, or *GDELT Live Feed*).
            2. Choose a headline or post from the dropdown (or select *Analyze All 10* for batch analysis).
            3. Click **Run Risk Analysis** to execute the pipeline.

            **What happens under the hood:**
            - **FinBERT Sentiment Analysis:** Extracts financial sentiment (-1.0 to +1.0) and direction.
            - **Zero-Shot Event Classification:** Categorizes events into Macro, Geopolitical, Credit, Regulatory, etc.
            - **Composite Impact Scoring:** Calculates an impact score from 1.0 to 10.0 with transparent component weights.
            - **Portfolio Stress Testing:** If impact >= 7.0, triggers stress testing against a $10M multi-asset portfolio.
            """
        )


if __name__ == "__main__":
    main()
