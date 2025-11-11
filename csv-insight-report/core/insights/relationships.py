"""
Relationship Insight Detector
Detects correlations and associations between variables.
"""

from typing import Dict, List, Any
import polars as pl
import numpy as np
from scipy import stats
from .base import BaseDetector, Insight


class RelationshipDetector(BaseDetector):
    """
    Detects relationships between numeric and categorical variables.
    """

    def detect(self, df: pl.DataFrame, schema: Dict[str, Any], profile: Dict[str, Any]) -> List[Insight]:
        """
        Detect relationship insights.

        Args:
            df: Input DataFrame
            schema: Schema dict from ingest
            profile: Profile dict from profiling

        Returns:
            List of detected Insight objects
        """
        insights = []
        insight_counter = 0

        min_n = 100
        min_abs_r = self.settings.get('correlation_min_abs', 0.3)

        # Process numeric-numeric correlations
        corr_data = profile.get('correlations', {})
        significant_pairs = corr_data.get('significant_pairs', [])

        for pair_key in significant_pairs:
            corr_info = corr_data['correlations'][pair_key]

            if corr_info['n_pairs'] < min_n:
                continue

            col1 = corr_info['col1']
            col2 = corr_info['col2']

            pearson_r = corr_info['pearson_r']
            pearson_p = corr_info['pearson_p']
            spearman_r = corr_info['spearman_r']

            # Determine strength
            abs_r = abs(pearson_r)
            strength = "strong" if abs_r > 0.7 else ("moderate" if abs_r > 0.5 else "weak")
            direction = "positive" if pearson_r > 0 else "negative"

            if abs_r >= min_abs_r or pearson_p < 0.05:
                insight_counter += 1

                # Get missingness for quality score
                miss1 = profile['missingness'][col1]['fraction']
                miss2 = profile['missingness'][col2]['fraction']
                avg_missingness = (miss1 + miss2) / 2

                # Compute Theil-Sen slope for robust regression
                pairs_df = df.select([col1, col2]).drop_nulls()
                x = pairs_df[col1].to_numpy()
                y = pairs_df[col2].to_numpy()

                # Theil-Sen estimator
                try:
                    ts_slope, ts_intercept = stats.theilslopes(y, x)[:2]
                except:
                    ts_slope, ts_intercept = np.nan, np.nan

                insights.append(Insight(
                    id=f"R{insight_counter:03d}",
                    title=f"{strength.capitalize()} {direction} correlation between {col1} and {col2}",
                    rationale=f"Pearson r={pearson_r:.3f} (p={pearson_p:.4f}) indicates a {strength} {direction} linear relationship.",
                    primary_columns=[col1, col2],
                    statistics={
                        'pearson_r': float(pearson_r),
                        'pearson_p': float(pearson_p),
                        'spearman_r': float(spearman_r),
                        'r_squared': float(pearson_r ** 2),
                        'theil_sen_slope': float(ts_slope) if not np.isnan(ts_slope) else None,
                        'theil_sen_intercept': float(ts_intercept) if not np.isnan(ts_intercept) else None,
                        'n': corr_info['n_pairs'],
                    },
                    quality_score=self.compute_quality_score(
                        corr_info['n_pairs'],
                        abs_r,
                        avg_missingness
                    ),
                    suggested_visuals=['scatter_with_regression', 'hexbin', 'scatter_with_theilsen'],
                    caveats=[
                        'Correlation does not imply causation.',
                        'Outliers can strongly influence Pearson correlation.',
                        'Relationship may be non-linear; inspect scatter plot.',
                    ],
                    detector_type='relationship',
                ))

        # Process categorical-categorical associations
        chi2_data = profile.get('chi_square', {})
        chi2_significant = chi2_data.get('significant_pairs', [])

        for pair_key in chi2_significant:
            test_info = chi2_data['tests'][pair_key]

            if test_info['n'] < min_n:
                continue

            col1 = test_info['col1']
            col2 = test_info['col2']

            cramers_v = test_info['cramers_v']
            p_value = test_info['p_value']

            # Strength interpretation for Cramér's V
            strength = "strong" if cramers_v > 0.5 else ("moderate" if cramers_v > 0.3 else "weak")

            if p_value < 0.05 and cramers_v > 0.3:
                insight_counter += 1

                miss1 = profile['missingness'][col1]['fraction']
                miss2 = profile['missingness'][col2]['fraction']
                avg_missingness = (miss1 + miss2) / 2

                insights.append(Insight(
                    id=f"R{insight_counter:03d}",
                    title=f"{strength.capitalize()} association between {col1} and {col2}",
                    rationale=f"Chi-square test shows {strength} association (Cramér's V={cramers_v:.3f}, p={p_value:.4f}).",
                    primary_columns=[col1, col2],
                    statistics={
                        'chi2': float(test_info['chi2']),
                        'p_value': float(p_value),
                        'cramers_v': float(cramers_v),
                        'n': test_info['n'],
                    },
                    quality_score=self.compute_quality_score(
                        test_info['n'],
                        cramers_v,
                        avg_missingness
                    ),
                    suggested_visuals=['grouped_bar', 'heatmap', 'mosaic'],
                    caveats=[
                        'Association does not imply causation.',
                        'Chi-square test assumes sufficient cell counts.',
                    ],
                    detector_type='relationship',
                ))

        return insights
