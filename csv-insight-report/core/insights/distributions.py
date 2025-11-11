"""
Distribution Insight Detector
Detects interesting distribution patterns in numeric columns.
"""

from typing import Dict, List, Any
import polars as pl
from .base import BaseDetector, Insight


class DistributionDetector(BaseDetector):
    """
    Detects distribution patterns: skew, heavy tails, multimodality, outliers.
    """

    def detect(self, df: pl.DataFrame, schema: Dict[str, Any], profile: Dict[str, Any]) -> List[Insight]:
        """
        Detect distribution insights.

        Args:
            df: Input DataFrame
            schema: Schema dict from ingest
            profile: Profile dict from profiling

        Returns:
            List of detected Insight objects
        """
        insights = []
        insight_counter = 0

        # Get numeric columns
        numeric_cols = [
            col['normalized_name']
            for col in schema['columns']
            if col['type'] in ['int', 'float']
        ]

        for col in numeric_cols:
            dist = profile['distributions'].get(col, {})

            if 'error' in dist:
                continue

            count = dist['count']

            # Skip if sample size too small
            if count < 50:
                continue

            missingness = profile['missingness'][col]['fraction']

            # Check for strong skew
            if abs(dist['skew']) > 1.0:
                insight_counter += 1
                direction = "right" if dist['skew'] > 0 else "left"

                insights.append(Insight(
                    id=f"D{insight_counter:03d}",
                    title=f"{col} shows {direction}-skewed distribution",
                    rationale=f"The distribution has a skewness of {dist['skew']:.2f}, indicating a long tail to the {direction}.",
                    primary_columns=[col],
                    statistics={
                        'skew': dist['skew'],
                        'mean': dist['mean'],
                        'median': dist['median'],
                        'std': dist['std'],
                        'n': count,
                    },
                    quality_score=self.compute_quality_score(count, abs(dist['skew']) / 2, missingness),
                    suggested_visuals=['histogram', 'boxplot', 'violin'],
                    caveats=['Skewed distributions may benefit from log transformation for modeling.'],
                    detector_type='distribution',
                ))

            # Check for heavy tails
            if dist.get('heavy_tailed', False):
                insight_counter += 1

                insights.append(Insight(
                    id=f"D{insight_counter:03d}",
                    title=f"{col} has heavy-tailed distribution",
                    rationale=f"Kurtosis of {dist['kurtosis']:.2f} indicates presence of extreme values beyond normal distribution.",
                    primary_columns=[col],
                    statistics={
                        'kurtosis': dist['kurtosis'],
                        'mean': dist['mean'],
                        'median': dist['median'],
                        'iqr': dist['iqr'],
                        'n': count,
                    },
                    quality_score=self.compute_quality_score(count, abs(dist['kurtosis']) / 5, missingness),
                    suggested_visuals=['histogram', 'boxplot', 'violin'],
                    caveats=['Heavy tails suggest presence of outliers or rare events.'],
                    detector_type='distribution',
                ))

            # Check for significant outliers
            outlier_frac = dist.get('outlier_fraction', 0)
            if outlier_frac > 0.05:  # More than 5% outliers
                insight_counter += 1

                insights.append(Insight(
                    id=f"D{insight_counter:03d}",
                    title=f"{col} contains {outlier_frac*100:.1f}% outliers",
                    rationale=f"Using Tukey fences (1.5×IQR), {dist['outliers_low']} low and {dist['outliers_high']} high outliers detected.",
                    primary_columns=[col],
                    statistics={
                        'outliers_low': dist['outliers_low'],
                        'outliers_high': dist['outliers_high'],
                        'outlier_fraction': outlier_frac,
                        'q25': dist['q25'],
                        'q75': dist['q75'],
                        'iqr': dist['iqr'],
                        'n': count,
                    },
                    quality_score=self.compute_quality_score(count, outlier_frac, missingness),
                    suggested_visuals=['boxplot', 'histogram', 'violin'],
                    caveats=['Outliers may represent data quality issues or rare but valid events.'],
                    detector_type='distribution',
                ))

            # Check for potential multimodality
            if dist.get('potentially_multimodal', False):
                insight_counter += 1

                insights.append(Insight(
                    id=f"D{insight_counter:03d}",
                    title=f"{col} may have multiple modes",
                    rationale=f"Negative kurtosis ({dist['kurtosis']:.2f}) suggests a flatter distribution with potential multiple peaks.",
                    primary_columns=[col],
                    statistics={
                        'kurtosis': dist['kurtosis'],
                        'mean': dist['mean'],
                        'median': dist['median'],
                        'std': dist['std'],
                        'n': count,
                    },
                    quality_score=self.compute_quality_score(count, abs(dist['kurtosis']) / 2, missingness),
                    suggested_visuals=['histogram', 'violin', 'kde'],
                    caveats=['Multimodal distributions may indicate distinct subpopulations in the data.'],
                    detector_type='distribution',
                ))

        return insights
