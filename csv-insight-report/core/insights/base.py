"""
Base classes for insight detectors.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Insight:
    """
    Represents a single insight detected from the data.
    """
    id: str
    title: str
    rationale: str
    primary_columns: List[str]
    secondary_columns: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    suggested_visuals: List[str] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)
    query: Optional[str] = None
    detector_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'rationale': self.rationale,
            'primary_columns': self.primary_columns,
            'secondary_columns': self.secondary_columns,
            'statistics': self.statistics,
            'quality_score': self.quality_score,
            'suggested_visuals': self.suggested_visuals,
            'caveats': self.caveats,
            'query': self.query,
            'detector_type': self.detector_type,
        }


class BaseDetector:
    """
    Base class for all insight detectors.
    """

    def __init__(self, settings: Dict[str, Any]):
        """
        Initialize detector with settings.

        Args:
            settings: Configuration dict from settings.json
        """
        self.settings = settings

    def detect(self, df, schema: Dict[str, Any], profile: Dict[str, Any]) -> List[Insight]:
        """
        Detect insights from the data.

        Args:
            df: Input DataFrame
            schema: Schema dict from ingest
            profile: Profile dict from profiling

        Returns:
            List of detected Insight objects
        """
        raise NotImplementedError("Subclasses must implement detect()")

    def compute_quality_score(
        self,
        n: int,
        effect_magnitude: float,
        missingness: float,
        **kwargs
    ) -> float:
        """
        Compute quality score for an insight.

        Args:
            n: Sample size
            effect_magnitude: Magnitude of the effect (correlation, effect size, etc.)
            missingness: Fraction of missing data
            **kwargs: Additional factors

        Returns:
            Quality score between 0 and 1
        """
        # Base score from sample size (diminishing returns)
        n_score = min(n / 1000, 1.0) * 0.3

        # Effect magnitude score
        effect_score = min(abs(effect_magnitude), 1.0) * 0.5

        # Penalize for missingness
        missingness_penalty = (1 - missingness) * 0.2

        return n_score + effect_score + missingness_penalty
