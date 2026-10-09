"""
RiskIntel AI — FastAPI REST API

Exposes the NLP Risk Engine and Portfolio Stress Testing as REST endpoints.

Usage:
    uvicorn api.main:app --reload
    # Then visit http://localhost:8000/docs for Swagger UI
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from risk_engine.engine import RiskEngine
from stress_testing.portfolio import Portfolio
from stress_testing.simulator import StressTestSimulator
from stress_testing.scenarios import SCENARIOS


# ── Pydantic Models ─────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    """Request model for single text analysis."""
    text: str
    source: str = "api"

class BatchAnalyzeRequest(BaseModel):
    """Request model for batch text analysis."""
    texts: List[str] = Field(..., min_length=1, max_length=50)
    source: str = "api_batch"

class StressTestRequest(BaseModel):
    """Request model for combined analysis + stress test."""
    text: str
    source: str = "api"


# ── App Lifecycle ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize heavy resources on startup."""
    app.state.engine = RiskEngine()
    app.state.portfolio = Portfolio.load_default(base_dir=str(PROJECT_ROOT))
    app.state.simulator = StressTestSimulator(portfolio=app.state.portfolio)
    yield


app = FastAPI(
    title="RiskIntel AI API",
    description=(
        "NLP Financial Risk Intelligence & Portfolio Stress Testing API.\n\n"
        "Analyzes unstructured financial text and produces structured risk signals "
        "with optional portfolio stress testing."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS (allow all for demo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ───────────────────────────────────────────────────
@app.get("/")
async def root():
    """Root endpoint with API navigation links."""
    return {
        "service": "RiskIntel AI",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "analyze": "POST /analyze",
            "batch": "POST /analyze/batch",
            "stress_test": "POST /stress-test",
            "portfolio": "GET /portfolio",
            "scenarios": "GET /scenarios",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RiskIntel AI", "version": "1.0.0"}


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Analyze a single text and return a structured RiskSignal.

    The engine runs FinBERT sentiment analysis, zero-shot event classification,
    and composite impact scoring on the input text.
    """
    try:
        engine: RiskEngine = app.state.engine
        signal = engine.analyze(text=request.text, source=request.source)
        return signal.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch")
async def analyze_batch(request: BatchAnalyzeRequest):
    """
    Analyze multiple texts and return a list of RiskSignals.

    Returns all signals along with summary counts.
    """
    try:
        engine: RiskEngine = app.state.engine
        signals = engine.analyze_batch(texts=request.texts, source=request.source)
        signal_dicts = [s.to_dict() for s in signals]
        high_risk_count = sum(1 for s in signals if s.risk_level == "HIGH")
        return {
            "signals": signal_dicts,
            "count": len(signal_dicts),
            "high_risk_count": high_risk_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stress-test")
async def stress_test(request: StressTestRequest):
    """
    Analyze text and run portfolio stress test if impact is HIGH.

    First runs NLP analysis, then triggers a stress test simulation
    if the impact score >= 7.0.
    """
    try:
        engine: RiskEngine = app.state.engine
        simulator: StressTestSimulator = app.state.simulator

        signal = engine.analyze(text=request.text, source=request.source)
        result = simulator.run_stress_test(signal.to_dict())

        return {
            "risk_signal": signal.to_dict(),
            "stress_test": result.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio")
async def get_portfolio():
    """Returns the current synthetic portfolio composition."""
    try:
        portfolio: Portfolio = app.state.portfolio
        assets = [
            {
                "name": a.name,
                "type": a.asset_type,
                "value": a.value,
                "sector": a.sector,
            }
            for a in portfolio.assets
        ]
        return {
            "portfolio_name": "RiskIntel Synthetic Portfolio",
            "total_value": portfolio.total_value,
            "currency": "USD",
            "assets": assets,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenarios")
async def get_scenarios():
    """Returns all available stress test scenarios with their shock values."""
    try:
        result = {}
        for name, scenario in SCENARIOS.items():
            result[name] = {
                "name": scenario.name,
                "event_type": scenario.event_type,
                "description": scenario.description,
                "shocks": scenario.shocks,
            }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
