"""
Insight Detection Runner
Coordinates all insight detectors and ranks results.
"""

import json
from typing import Dict, List, Any
import polars as pl
from .base import Insight
from .distributions import DistributionDetector
from .trends import TrendDetector
from .groups import GroupDetector
from .relationships import RelationshipDetector


def run_all(
    df: pl.DataFrame,
    schema: Dict[str, Any],
    profile: Dict[str, Any],
    settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run all insight detectors and rank results.

    Args:
        df: Input DataFrame
        schema: Schema dict from ingest
        profile: Profile dict from profiling
        settings: Settings dict from config

    Returns:
        Insights dict with all detected insights ranked by quality
    """
    all_insights = []

    # Initialize detectors
    detectors = [
        DistributionDetector(settings),
        TrendDetector(settings),
        GroupDetector(settings),
        RelationshipDetector(settings),
    ]

    # Run each detector
    for detector in detectors:
        detector_insights = detector.detect(df, schema, profile)
        all_insights.extend(detector_insights)

    # Sort by quality score descending
    all_insights.sort(key=lambda x: x.quality_score, reverse=True)

    # Limit to top candidates
    max_insights = settings.get('max_insights_to_surface', 8)
    top_insights = all_insights[:max_insights]
    appendix_insights = all_insights[max_insights:]

    # Build output structure
    insights_output = {
        'version': '1.0',
        'top_insights': [ins.to_dict() for ins in top_insights],
        'appendix_insights': [ins.to_dict() for ins in appendix_insights],
        'total_detected': len(all_insights),
        'settings': settings,
    }

    return insights_output


def save_insights(insights: Dict[str, Any], output_path: str) -> None:
    """
    Save insights to JSON file.

    Args:
        insights: Insights dictionary
        output_path: Path to output JSON file
    """
    with open(output_path, 'w') as f:
        json.dump(insights, f, indent=2)


def load_insights(input_path: str) -> Dict[str, Any]:
    """
    Load insights from JSON file.

    Args:
        input_path: Path to input JSON file

    Returns:
        Insights dictionary
    """
    with open(input_path, 'r') as f:
        return json.load(f)
