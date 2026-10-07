"""
RiskIntel AI — Risk Engine Orchestrator

Ties together text preprocessing, sentiment analysis, event classification,
and impact scoring into a single unified pipeline.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from preprocessing.text_cleaner import TextCleaner, CleanedText
from risk_engine.sentiment import SentimentAnalyzer, SentimentResult
from risk_engine.event_classifier import EventClassifier, EventResult
from risk_engine.impact_scorer import ImpactScorer, ImpactResult

logger = logging.getLogger(__name__)


@dataclass
class RiskSignal:
    """Structured risk signal — the primary output of the Risk Engine."""

    timestamp: str
    source: str
    entity: str
    original_text: str
    clean_text: str
    sentiment_score: float
    sentiment_label: str
    event_type: str
    event_confidence: float
    impact_score: float
    risk_level: str
    impact_components: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON output."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def summary(self) -> str:
        """Human-readable one-line summary."""
        return (
            f"[{self.risk_level}] {self.event_type} | "
            f"Sentiment: {self.sentiment_score:+.2f} | "
            f"Impact: {self.impact_score:.1f}/10 | "
            f"Entity: {self.entity}"
        )


class RiskEngine:
    """
    Core NLP Risk Engine.

    Takes unstructured financial text and produces structured RiskSignal objects
    containing sentiment score, event classification, and impact assessment.

    Usage:
        engine = RiskEngine()
        signal = engine.analyze("US announces new tariffs on Chinese imports")
        print(signal.to_json())
    """

    def __init__(self):
        """Initialize all sub-components with lazy loading."""
        self.cleaner = TextCleaner()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.event_classifier = EventClassifier()
        self.impact_scorer = ImpactScorer()
        logger.info("RiskEngine initialized (models will load on first use)")

    def analyze(
        self,
        text: str,
        source: str = "manual",
        timestamp: Optional[str] = None,
    ) -> RiskSignal:
        """
        Analyze a single text input and produce a RiskSignal.

        Args:
            text: Raw unstructured text to analyze.
            source: Data source identifier (e.g., 'news', 'social', 'manual').
            timestamp: Optional ISO 8601 timestamp. Defaults to current UTC time.

        Returns:
            RiskSignal with sentiment, event type, and impact assessment.
        """
        if not text or not text.strip():
            logger.warning("Empty text received, returning neutral signal")
            return self._empty_signal(source, timestamp)

        # Step 1: Clean text
        cleaned = self.cleaner.clean(text)
        logger.info(f"Cleaned text: '{cleaned.clean_text[:80]}...'")

        # Step 2: Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze(cleaned.clean_text)
        logger.info(
            f"Sentiment: {sentiment.label} ({sentiment.numerical_score:+.2f})"
        )

        # Step 3: Event classification
        event = self.event_classifier.classify(cleaned.clean_text)
        logger.info(
            f"Event: {event.event_type} (confidence: {event.confidence:.2f})"
        )

        # Step 4: Impact scoring
        entities = cleaned.extracted_entities or ["Unknown"]
        impact = self.impact_scorer.score(
            event_type=event.event_type,
            sentiment_score=sentiment.numerical_score,
            entities=entities,
            text=cleaned.clean_text,
        )
        logger.info(
            f"Impact: {impact.score:.1f}/10 ({impact.risk_level})"
        )

        # Step 5: Assemble RiskSignal
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        primary_entity = entities[0] if entities else "Unknown"

        signal = RiskSignal(
            timestamp=ts,
            source=source,
            entity=primary_entity,
            original_text=text,
            clean_text=cleaned.clean_text,
            sentiment_score=round(sentiment.numerical_score, 4),
            sentiment_label=sentiment.label,
            event_type=event.event_type,
            event_confidence=round(event.confidence, 4),
            impact_score=round(impact.score, 2),
            risk_level=impact.risk_level,
            impact_components=impact.components,
        )

        logger.info(f"Signal produced: {signal.summary()}")
        return signal

    def analyze_batch(
        self,
        texts: List[str],
        source: str = "batch",
        deduplicate: bool = True,
    ) -> List[RiskSignal]:
        """
        Analyze multiple texts and return list of RiskSignals.

        Args:
            texts: List of raw text strings.
            source: Source identifier applied to all signals.
            deduplicate: If True, remove duplicate texts before processing.

        Returns:
            List of RiskSignal objects.
        """
        if not texts:
            return []

        # Clean all texts
        cleaned_list = [self.cleaner.clean(t) for t in texts]

        if deduplicate:
            cleaned_list = TextCleaner.deduplicate(cleaned_list)
            logger.info(
                f"After dedup: {len(cleaned_list)} unique texts "
                f"(from {len(texts)} original)"
            )

        signals = []
        for i, cleaned in enumerate(cleaned_list):
            logger.info(f"Processing {i + 1}/{len(cleaned_list)}...")
            try:
                signal = self.analyze(
                    cleaned.original_text, source=source
                )
                signals.append(signal)
            except Exception as e:
                logger.error(
                    f"Error processing text {i + 1}: {e}", exc_info=True
                )
                continue

        logger.info(f"Batch complete: {len(signals)} signals produced")
        return signals

    def analyze_from_records(
        self, records: list
    ) -> List[RiskSignal]:
        """
        Analyze DataRecord objects from the ingestion layer.

        Args:
            records: List of DataRecord objects (from ingestion.base).

        Returns:
            List of RiskSignal objects.
        """
        signals = []
        for record in records:
            try:
                # Use title + text for richer context
                full_text = record.text
                if hasattr(record, "title") and record.title:
                    full_text = f"{record.title}. {record.text}"

                signal = self.analyze(
                    text=full_text,
                    source=record.source,
                    timestamp=getattr(record, "timestamp", None),
                )
                # Override entity if record has one
                if hasattr(record, "entity") and record.entity:
                    signal.entity = record.entity

                signals.append(signal)
            except Exception as e:
                logger.error(f"Error processing record: {e}", exc_info=True)
                continue

        return signals

    def save_signals(
        self,
        signals: List[RiskSignal],
        filepath: str = "data/processed/risk_signals.json",
    ) -> str:
        """
        Save risk signals to a JSON file.

        Args:
            signals: List of RiskSignal objects.
            filepath: Output file path.

        Returns:
            Absolute path to saved file.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = [s.to_dict() for s in signals]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(signals)} signals to {path.absolute()}")
        return str(path.absolute())

    @staticmethod
    def load_signals(filepath: str) -> List[RiskSignal]:
        """Load previously saved risk signals from JSON."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [RiskSignal(**item) for item in data]

    def _empty_signal(
        self, source: str, timestamp: Optional[str]
    ) -> RiskSignal:
        """Return a neutral signal for empty/invalid input."""
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        return RiskSignal(
            timestamp=ts,
            source=source,
            entity="Unknown",
            original_text="",
            clean_text="",
            sentiment_score=0.0,
            sentiment_label="neutral",
            event_type="Other",
            event_confidence=0.0,
            impact_score=1.0,
            risk_level="LOW",
            impact_components={},
        )
