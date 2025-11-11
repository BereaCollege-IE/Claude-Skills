"""
Narrative Generation Module
Generates audience-aware narratives for insights using rule-based templates.
"""

from typing import Dict, List, Any
from enum import Enum


class ExpertiseLevel(Enum):
    """Expertise level of the audience"""
    EXECUTIVE = "executive"
    PRACTITIONER = "practitioner"
    TECHNICAL = "technical"


def format_number(value: float, decimals: int = 1, expertise: ExpertiseLevel = ExpertiseLevel.EXECUTIVE) -> str:
    """
    Format number based on audience expertise.

    Args:
        value: Number to format
        decimals: Number of decimal places
        expertise: Audience expertise level

    Returns:
        Formatted string
    """
    if expertise == ExpertiseLevel.EXECUTIVE:
        # Round to 1-2 decimals for executives
        return f"{value:.{min(decimals, 2)}f}"
    elif expertise == ExpertiseLevel.PRACTITIONER:
        # Show 2-3 decimals for practitioners
        return f"{value:.{min(decimals + 1, 3)}f}"
    else:
        # Show full precision for technical audience
        return f"{value:.{decimals + 2}f}"


def render_distribution_narrative(
    insight: Dict[str, Any],
    settings: Dict[str, Any],
    profile: Dict[str, Any]
) -> str:
    """
    Generate narrative for distribution insight.

    Args:
        insight: Insight dictionary
        settings: Settings dict
        profile: Profile dict

    Returns:
        Narrative text
    """
    expertise = ExpertiseLevel(settings.get('expertise', 'executive'))
    column = insight['primary_columns'][0]
    stats = insight['statistics']

    if expertise == ExpertiseLevel.EXECUTIVE:
        # Concise, practical significance
        if 'skew' in stats:
            direction = "right" if stats['skew'] > 0 else "left"
            text = f"The {column} data is skewed to the {direction}, "
            text += f"with a typical value around {format_number(stats['median'], 1, expertise)}. "
            text += "This suggests the presence of outliers or a non-normal distribution."

        elif 'outlier_fraction' in stats:
            pct = stats['outlier_fraction'] * 100
            text = f"About {format_number(pct, 0, expertise)}% of {column} values are outliers. "
            text += "These may warrant further investigation."

        else:
            text = insight['rationale']

    elif expertise == ExpertiseLevel.PRACTITIONER:
        # Include statistics and actionable recommendations
        if 'skew' in stats:
            text = f"The {column} distribution shows a skewness of {format_number(stats['skew'], 2, expertise)}, "
            text += f"with median {format_number(stats['median'], 2, expertise)} "
            text += f"and mean {format_number(stats['mean'], 2, expertise)}. "
            text += "Consider applying a log transformation if using this variable in modeling. "
            text += f"The standard deviation is {format_number(stats['std'], 2, expertise)}."

        elif 'outlier_fraction' in stats:
            text = f"{column} contains {stats['outliers_low']} low outliers and {stats['outliers_high']} high outliers "
            text += f"(Tukey fences method, IQR={format_number(stats['iqr'], 2, expertise)}). "
            text += "Review these values for data quality issues or valid extreme cases."

        else:
            text = insight['rationale']

    else:  # TECHNICAL
        # Include test names, effect sizes, sampling details
        if 'skew' in stats:
            text = f"Distribution analysis of {column} (n={stats['n']}): "
            text += f"skewness={format_number(stats['skew'], 3, expertise)}, "
            text += f"kurtosis={format_number(stats['kurtosis'], 3, expertise)}, "
            text += f"μ={format_number(stats['mean'], 3, expertise)}, "
            text += f"median={format_number(stats['median'], 3, expertise)}, "
            text += f"σ={format_number(stats['std'], 3, expertise)}, "
            text += f"MAD={format_number(stats.get('mad', 0), 3, expertise)}. "
            text += "Shapiro-Wilk or Anderson-Darling tests recommended for formal normality testing."

        elif 'outlier_fraction' in stats:
            text = f"Outlier detection using Tukey fences (Q1-1.5×IQR, Q3+1.5×IQR): "
            text += f"n_low={stats['outliers_low']}, n_high={stats['outliers_high']}, "
            text += f"fraction={format_number(stats['outlier_fraction'], 4, expertise)} "
            text += f"(n={stats['n']}). "
            text += f"IQR={format_number(stats['iqr'], 3, expertise)}, "
            text += f"Q1={format_number(stats['q25'], 3, expertise)}, "
            text += f"Q3={format_number(stats['q75'], 3, expertise)}."

        else:
            text = insight['rationale']

    return text


def render_trend_narrative(
    insight: Dict[str, Any],
    settings: Dict[str, Any],
    profile: Dict[str, Any]
) -> str:
    """
    Generate narrative for trend insight.

    Args:
        insight: Insight dictionary
        settings: Settings dict
        profile: Profile dict

    Returns:
        Narrative text
    """
    expertise = ExpertiseLevel(settings.get('expertise', 'executive'))
    time_col, measure_col = insight['primary_columns']
    stats = insight['statistics']

    direction = "increasing" if stats['spearman_r'] > 0 else "decreasing"
    abs_r = abs(stats['spearman_r'])
    strength = "strong" if abs_r > 0.7 else ("moderate" if abs_r > 0.5 else "weak")

    if expertise == ExpertiseLevel.EXECUTIVE:
        text = f"{measure_col} shows a {strength} {direction} trend over time. "
        if 'slope' in stats:
            text += f"The rate of change is approximately {format_number(abs(stats['slope']), 1, expertise)} per period."

    elif expertise == ExpertiseLevel.PRACTITIONER:
        text = f"{measure_col} demonstrates a {strength} {direction} trend (Spearman ρ={format_number(stats['spearman_r'], 3, expertise)}, "
        text += f"p={format_number(stats['spearman_p'], 4, expertise)}) over {stats['n_periods']} time periods. "
        if 'slope' in stats:
            text += f"Linear regression slope: {format_number(stats['slope'], 3, expertise)} "
            text += f"(95% CI: [{format_number(stats.get('slope_ci_lower', 0), 3, expertise)}, "
            text += f"{format_number(stats.get('slope_ci_upper', 0), 3, expertise)}]). "
        text += "Consider investigating driving factors and forecasting future values."

    else:  # TECHNICAL
        text = f"Time series analysis of {measure_col} (n={stats['n_periods']} periods, "
        text += f"completeness={format_number(stats['completeness'], 3, expertise)}): "
        text += f"Spearman ρ={format_number(stats['spearman_r'], 4, expertise)} "
        text += f"(p={format_number(stats['spearman_p'], 6, expertise)}). "
        text += f"OLS regression: slope={format_number(stats['slope'], 4, expertise)}, "
        text += f"R²={format_number(stats['r_squared'], 4, expertise)}, "
        text += f"SE={format_number((stats.get('slope_ci_upper', 0) - stats['slope']) / 1.96, 4, expertise)}. "
        text += "Note: Autocorrelation not tested; consider ARIMA or seasonal decomposition for formal analysis."

    return text


def render_group_narrative(
    insight: Dict[str, Any],
    settings: Dict[str, Any],
    profile: Dict[str, Any]
) -> str:
    """
    Generate narrative for group difference insight.

    Args:
        insight: Insight dictionary
        settings: Settings dict
        profile: Profile dict

    Returns:
        Narrative text
    """
    expertise = ExpertiseLevel(settings.get('expertise', 'executive'))
    group_col, measure_col = insight['primary_columns']
    stats = insight['statistics']

    if 'cohens_d' in stats:
        # Two-group comparison
        groups = list(stats['groups'].keys())
        effect = stats['cohens_d']
        effect_label = stats['effect_size_label']

        if expertise == ExpertiseLevel.EXECUTIVE:
            group1_mean = stats['groups'][groups[0]]['mean']
            group2_mean = stats['groups'][groups[1]]['mean']

            higher_group = groups[0] if group1_mean > group2_mean else groups[1]
            lower_group = groups[1] if group1_mean > group2_mean else groups[0]

            text = f"{measure_col} is notably different between {group_col} groups: "
            text += f"{higher_group} averages {format_number(max(group1_mean, group2_mean), 1, expertise)} "
            text += f"compared to {format_number(min(group1_mean, group2_mean), 1, expertise)} for {lower_group}."

        elif expertise == ExpertiseLevel.PRACTITIONER:
            text = f"{measure_col} differs significantly between {groups[0]} and {groups[1]} "
            text += f"(Welch's t-test, Cohen's d={format_number(abs(effect), 3, expertise)}, "
            text += f"p={format_number(stats['p_value'], 4, expertise)}). "
            text += f"Effect size is {effect_label}. "

            for group, gstats in stats['groups'].items():
                text += f"{group}: M={format_number(gstats['mean'], 2, expertise)}, "
                text += f"SD={format_number(gstats['std'], 2, expertise)}, "
                text += f"n={gstats['n']}. "

        else:  # TECHNICAL
            text = f"Two-sample comparison of {measure_col} by {group_col}: "
            text += f"Welch's t-test t={format_number(stats['t_statistic'], 4, expertise)}, "
            text += f"p={format_number(stats['p_value'], 6, expertise)}; "
            text += f"Cohen's d={format_number(stats['cohens_d'], 4, expertise)} ({effect_label} effect). "

            for group, gstats in stats['groups'].items():
                text += f"{group}: μ={format_number(gstats['mean'], 4, expertise)}, "
                text += f"σ={format_number(gstats['std'], 4, expertise)}, "
                text += f"median={format_number(gstats['median'], 4, expertise)}, "
                text += f"n={gstats['n']}. "

            text += "Assumptions: approximately normal distributions, unequal variances allowed."

    else:
        # Multi-group comparison
        effect = stats.get('eta_squared', 0)
        effect_label = stats['effect_size_label']

        if expertise == ExpertiseLevel.EXECUTIVE:
            text = f"{measure_col} varies across {stats['n_groups']} {group_col} groups. "
            text += "Differences are statistically significant."

        elif expertise == ExpertiseLevel.PRACTITIONER:
            text = f"{measure_col} shows {effect_label} variation across {group_col} groups "
            text += f"(Kruskal-Wallis H={format_number(stats['h_statistic'], 3, expertise)}, "
            text += f"p={format_number(stats['p_value'], 4, expertise)}, "
            text += f"η²={format_number(effect, 3, expertise)}). "
            text += "Post-hoc pairwise tests recommended to identify specific group differences."

        else:  # TECHNICAL
            text = f"Multi-group comparison of {measure_col} across {stats['n_groups']} {group_col} levels: "
            text += f"Kruskal-Wallis H={format_number(stats['h_statistic'], 4, expertise)} "
            text += f"(p={format_number(stats['p_value'], 6, expertise)}), "
            text += f"η²={format_number(effect, 4, expertise)}. "
            text += f"Total n={stats['n_total']}. "
            text += "Non-parametric test used; suitable for non-normal data or ordinal scales."

    return text


def render_relationship_narrative(
    insight: Dict[str, Any],
    settings: Dict[str, Any],
    profile: Dict[str, Any]
) -> str:
    """
    Generate narrative for relationship insight.

    Args:
        insight: Insight dictionary
        settings: Settings dict
        profile: Profile dict

    Returns:
        Narrative text
    """
    expertise = ExpertiseLevel(settings.get('expertise', 'executive'))
    col1, col2 = insight['primary_columns']
    stats = insight['statistics']

    if 'pearson_r' in stats:
        # Numeric-numeric correlation
        r = stats['pearson_r']
        abs_r = abs(r)
        direction = "positive" if r > 0 else "negative"
        strength = "strong" if abs_r > 0.7 else ("moderate" if abs_r > 0.5 else "weak")

        if expertise == ExpertiseLevel.EXECUTIVE:
            text = f"{col1} and {col2} show a {strength} {direction} relationship. "
            text += f"About {format_number(stats['r_squared'] * 100, 0, expertise)}% of the variation is explained."

        elif expertise == ExpertiseLevel.PRACTITIONER:
            text = f"{col1} and {col2} are {strength}ly {direction}ly correlated "
            text += f"(Pearson r={format_number(r, 3, expertise)}, "
            text += f"p={format_number(stats['pearson_p'], 4, expertise)}, "
            text += f"R²={format_number(stats['r_squared'], 3, expertise)}, "
            text += f"n={stats['n']}). "
            if stats.get('theil_sen_slope'):
                text += f"Robust regression slope: {format_number(stats['theil_sen_slope'], 3, expertise)}. "

        else:  # TECHNICAL
            text = f"Correlation analysis ({col1}, {col2}): "
            text += f"Pearson r={format_number(r, 4, expertise)} "
            text += f"(p={format_number(stats['pearson_p'], 6, expertise)}), "
            text += f"Spearman ρ={format_number(stats['spearman_r'], 4, expertise)}, "
            text += f"R²={format_number(stats['r_squared'], 4, expertise)}, "
            text += f"n={stats['n']}. "
            if stats.get('theil_sen_slope'):
                text += f"Theil-Sen slope={format_number(stats['theil_sen_slope'], 4, expertise)}, "
                text += f"intercept={format_number(stats.get('theil_sen_intercept', 0), 4, expertise)}. "

    elif 'cramers_v' in stats:
        # Categorical-categorical association
        v = stats['cramers_v']
        strength = "strong" if v > 0.5 else ("moderate" if v > 0.3 else "weak")

        if expertise == ExpertiseLevel.EXECUTIVE:
            text = f"{col1} and {col2} are associated. "
            text += "Values of one variable tend to vary with the other."

        elif expertise == ExpertiseLevel.PRACTITIONER:
            text = f"{col1} and {col2} show {strength} association "
            text += f"(χ²={format_number(stats['chi2'], 2, expertise)}, "
            text += f"p={format_number(stats['p_value'], 4, expertise)}, "
            text += f"Cramér's V={format_number(v, 3, expertise)}, "
            text += f"n={stats['n']}). "

        else:  # TECHNICAL
            text = f"Chi-square test of independence ({col1} × {col2}): "
            text += f"χ²={format_number(stats['chi2'], 4, expertise)}, "
            text += f"p={format_number(stats['p_value'], 6, expertise)}, "
            text += f"Cramér's V={format_number(v, 4, expertise)}, "
            text += f"n={stats['n']}. "
            text += "Assumption: sufficient expected counts in contingency table cells."

    else:
        text = insight['rationale']

    return text


def render(insight: Dict[str, Any], settings: Dict[str, Any], profile: Dict[str, Any]) -> str:
    """
    Main narrative rendering function.

    Args:
        insight: Insight dictionary
        settings: Settings dict
        profile: Profile dict

    Returns:
        Generated narrative text
    """
    detector_type = insight.get('detector_type', '')

    if detector_type == 'distribution':
        return render_distribution_narrative(insight, settings, profile)
    elif detector_type == 'trend':
        return render_trend_narrative(insight, settings, profile)
    elif detector_type == 'group':
        return render_group_narrative(insight, settings, profile)
    elif detector_type == 'relationship':
        return render_relationship_narrative(insight, settings, profile)
    else:
        return insight.get('rationale', 'No narrative available.')


def generate_limitations_section(profile: Dict[str, Any], settings: Dict[str, Any]) -> str:
    """
    Generate limitations and assumptions section.

    Args:
        profile: Profile dict
        settings: Settings dict

    Returns:
        Limitations text
    """
    limitations = []

    # Check for high missingness
    high_miss_cols = [
        col for col, info in profile['missingness'].items()
        if info['fraction'] > 0.1
    ]

    if high_miss_cols:
        limitations.append(
            f"Some columns have substantial missing data (>10%): {', '.join(high_miss_cols[:5])}. "
            "Insights involving these variables should be interpreted with caution."
        )

    # Sampling note
    limitations.append(
        "Statistical tests assume random sampling and independence of observations. "
        "Violations may affect validity of results."
    )

    # Outliers note
    limitations.append(
        "Outliers were identified using standard methods (Tukey fences) but not automatically removed. "
        "Results may be sensitive to extreme values."
    )

    # Multiple testing
    limitations.append(
        "Multiple statistical tests were performed without adjustment for multiple comparisons. "
        "Some statistically significant results may be due to chance."
    )

    return " ".join(limitations)


if __name__ == '__main__':
    # Example usage
    example_insight = {
        'detector_type': 'distribution',
        'primary_columns': ['age'],
        'statistics': {
            'mean': 35.5,
            'median': 34.0,
            'std': 12.3,
            'skew': 0.7,
            'kurtosis': 0.2,
            'n': 500,
        },
    }

    settings = {'expertise': 'practitioner'}
    profile = {'missingness': {'age': {'fraction': 0.02}}}

    narrative = render(example_insight, settings, profile)
    print(narrative)
