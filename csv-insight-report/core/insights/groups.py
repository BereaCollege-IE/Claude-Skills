"""
Group Differences Insight Detector
Detects significant differences between groups using statistical tests.
"""

from typing import Dict, List, Any
import polars as pl
import numpy as np
from scipy import stats
from .base import BaseDetector, Insight


class GroupDetector(BaseDetector):
    """
    Detects significant differences between categorical groups.
    """

    def detect(self, df: pl.DataFrame, schema: Dict[str, Any], profile: Dict[str, Any]) -> List[Insight]:
        """
        Detect group difference insights.

        Args:
            df: Input DataFrame
            schema: Schema dict from ingest
            profile: Profile dict from profiling

        Returns:
            List of detected Insight objects
        """
        insights = []
        insight_counter = 0

        min_group_size = self.settings.get('min_sample_for_parametrics', 20)

        # Get categorical columns with reasonable cardinality
        categorical_cols = [
            col['normalized_name']
            for col in schema['columns']
            if col['type'] in ['categorical', 'string', 'bool']
            and col['unique_count'] >= 2
            and col['unique_count'] <= 10  # Reasonable number of groups
        ]

        # Get numeric columns
        numeric_cols = [
            col['normalized_name']
            for col in schema['columns']
            if col['type'] in ['int', 'float']
        ]

        # Test each combination
        for group_col in categorical_cols:
            for measure_col in numeric_cols:
                # Get groups
                groups_data = df.select([group_col, measure_col]).drop_nulls()

                if len(groups_data) < min_group_size:
                    continue

                # Get unique groups
                unique_groups = groups_data[group_col].unique().to_list()

                if len(unique_groups) < 2:
                    continue

                # Extract data for each group
                group_arrays = []
                group_stats = {}

                for group in unique_groups:
                    group_data = groups_data.filter(pl.col(group_col) == group)[measure_col].to_numpy()
                    if len(group_data) >= min_group_size:
                        group_arrays.append(group_data)
                        group_stats[str(group)] = {
                            'n': len(group_data),
                            'mean': float(np.mean(group_data)),
                            'std': float(np.std(group_data)),
                            'median': float(np.median(group_data)),
                        }

                if len(group_arrays) < 2:
                    continue

                # Perform appropriate test
                if len(group_arrays) == 2:
                    # Two groups: Welch's t-test
                    t_stat, p_value = stats.ttest_ind(group_arrays[0], group_arrays[1], equal_var=False)

                    # Compute Cohen's d
                    n1, n2 = len(group_arrays[0]), len(group_arrays[1])
                    s1, s2 = np.std(group_arrays[0]), np.std(group_arrays[1])
                    pooled_std = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
                    cohens_d = (np.mean(group_arrays[0]) - np.mean(group_arrays[1])) / pooled_std if pooled_std > 0 else 0

                    # Effect size interpretation
                    effect_size = abs(cohens_d)
                    effect_label = "large" if effect_size > 0.8 else ("medium" if effect_size > 0.5 else "small")

                    if p_value < 0.05 or effect_size > 0.5:
                        insight_counter += 1

                        group_names = list(group_stats.keys())
                        missingness = profile['missingness'][measure_col]['fraction']

                        insights.append(Insight(
                            id=f"G{insight_counter:03d}",
                            title=f"{measure_col} differs significantly between {group_col} groups",
                            rationale=f"Welch's t-test shows {effect_label} effect (d={cohens_d:.3f}, p={p_value:.4f}) between {group_names[0]} and {group_names[1]}.",
                            primary_columns=[group_col, measure_col],
                            statistics={
                                't_statistic': float(t_stat),
                                'p_value': float(p_value),
                                'cohens_d': float(cohens_d),
                                'effect_size_label': effect_label,
                                'groups': group_stats,
                                'n_total': sum(len(g) for g in group_arrays),
                            },
                            quality_score=self.compute_quality_score(
                                sum(len(g) for g in group_arrays),
                                effect_size,
                                missingness
                            ),
                            suggested_visuals=['grouped_bar', 'boxplot_by_group', 'violin_by_group'],
                            caveats=[
                                'Welch\'s t-test assumes approximately normal distributions.',
                                'Outliers may influence results significantly.',
                            ],
                            detector_type='group',
                        ))

                else:
                    # More than two groups: Brown-Forsythe ANOVA (more robust than standard ANOVA)
                    # Using Kruskal-Wallis as a simpler alternative
                    h_stat, p_value = stats.kruskal(*group_arrays)

                    # Compute eta-squared (effect size for ANOVA)
                    grand_mean = np.mean(np.concatenate(group_arrays))
                    ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in group_arrays)
                    ss_total = sum((x - grand_mean)**2 for g in group_arrays for x in g)
                    eta_squared = ss_between / ss_total if ss_total > 0 else 0

                    effect_size = eta_squared
                    effect_label = "large" if effect_size > 0.14 else ("medium" if effect_size > 0.06 else "small")

                    if p_value < 0.05 or effect_size > 0.06:
                        insight_counter += 1

                        missingness = profile['missingness'][measure_col]['fraction']

                        insights.append(Insight(
                            id=f"G{insight_counter:03d}",
                            title=f"{measure_col} varies significantly across {group_col} groups",
                            rationale=f"Kruskal-Wallis test shows {effect_label} effect (η²={eta_squared:.3f}, p={p_value:.4f}) across {len(group_arrays)} groups.",
                            primary_columns=[group_col, measure_col],
                            statistics={
                                'h_statistic': float(h_stat),
                                'p_value': float(p_value),
                                'eta_squared': float(eta_squared),
                                'effect_size_label': effect_label,
                                'groups': group_stats,
                                'n_total': sum(len(g) for g in group_arrays),
                                'n_groups': len(group_arrays),
                            },
                            quality_score=self.compute_quality_score(
                                sum(len(g) for g in group_arrays),
                                effect_size,
                                missingness
                            ),
                            suggested_visuals=['grouped_bar', 'boxplot_by_group', 'violin_by_group'],
                            caveats=[
                                'Kruskal-Wallis is a non-parametric test suitable for non-normal data.',
                                'Post-hoc tests needed to identify specific group differences.',
                            ],
                            detector_type='group',
                        ))

        return insights
