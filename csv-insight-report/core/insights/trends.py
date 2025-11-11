"""
Trend Insight Detector
Detects temporal trends in time series data.
"""

from typing import Dict, List, Any
import polars as pl
import numpy as np
from scipy import stats
from .base import BaseDetector, Insight


class TrendDetector(BaseDetector):
    """
    Detects trends over time using Spearman correlation and basic time series analysis.
    """

    def detect(self, df: pl.DataFrame, schema: Dict[str, Any], profile: Dict[str, Any]) -> List[Insight]:
        """
        Detect trend insights.

        Args:
            df: Input DataFrame
            schema: Schema dict from ingest
            profile: Profile dict from profiling

        Returns:
            List of detected Insight objects
        """
        insights = []
        insight_counter = 0

        # Get time index info
        time_index_info = profile.get('time_index')
        if not time_index_info:
            return insights  # No time index detected

        time_col = time_index_info['column']
        min_periods = self.settings.get('trend_min_periods', 12)

        # Get numeric columns
        numeric_cols = [
            col['normalized_name']
            for col in schema['columns']
            if col['type'] in ['int', 'float'] and col['normalized_name'] != time_col
        ]

        # Sort by time
        df_sorted = df.sort(time_col)

        for measure_col in numeric_cols:
            # Get clean time series
            ts_data = df_sorted.select([time_col, measure_col]).drop_nulls()

            if len(ts_data) < min_periods:
                continue

            # Extract values
            time_values = ts_data[time_col].to_numpy()
            measure_values = ts_data[measure_col].to_numpy()

            # Convert time to numeric (days since first observation)
            if hasattr(time_values[0], 'timestamp'):
                time_numeric = np.array([(t - time_values[0]).total_seconds() / 86400 for t in time_values])
            else:
                time_numeric = np.arange(len(time_values))

            # Compute Spearman correlation
            spearman_r, spearman_p = stats.spearmanr(time_numeric, measure_values)

            # Compute linear regression for slope
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_numeric, measure_values)

            # Compute confidence interval for slope (95%)
            conf_interval = 1.96 * std_err

            # Check if trend is significant
            min_abs_rho = self.settings.get('correlation_min_abs', 0.3)

            if abs(spearman_r) >= min_abs_rho or spearman_p < 0.05:
                insight_counter += 1

                direction = "increasing" if spearman_r > 0 else "decreasing"
                strength = "strong" if abs(spearman_r) > 0.7 else ("moderate" if abs(spearman_r) > 0.5 else "weak")

                missingness = profile['missingness'][measure_col]['fraction']

                insights.append(Insight(
                    id=f"T{insight_counter:03d}",
                    title=f"{measure_col} shows {strength} {direction} trend over time",
                    rationale=f"Spearman correlation of {spearman_r:.3f} (p={spearman_p:.4f}) indicates a {strength} {direction} trend.",
                    primary_columns=[time_col, measure_col],
                    statistics={
                        'spearman_r': float(spearman_r),
                        'spearman_p': float(spearman_p),
                        'slope': float(slope),
                        'slope_ci_lower': float(slope - conf_interval),
                        'slope_ci_upper': float(slope + conf_interval),
                        'r_squared': float(r_value ** 2),
                        'n_periods': len(ts_data),
                        'completeness': float(len(ts_data) / len(df)),
                    },
                    quality_score=self.compute_quality_score(
                        len(ts_data),
                        abs(spearman_r),
                        missingness
                    ),
                    suggested_visuals=['line', 'area', 'scatter_with_trend'],
                    caveats=[
                        'Correlation does not imply causation.',
                        'Trend may not be linear; consider visual inspection.',
                    ],
                    detector_type='trend',
                ))

        return insights
