"""
Chart Recommendation Module
Recommends appropriate visualizations for each insight with accessibility checks.
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class ChartSpec:
    """
    Specification for a recommended chart.
    """
    chart_type: str
    title: str
    rationale: str
    accessibility_checks: List[str]
    implementation_params: Dict[str, Any]
    priority: int  # 1 = highest priority


# Color-blind safe palettes
COLORBLIND_CATEGORICAL = [
    '#0173B2',  # Blue
    '#DE8F05',  # Orange
    '#029E73',  # Green
    '#CC78BC',  # Purple
    '#CA9161',  # Brown
    '#ECE133',  # Yellow
    '#56B4E9',  # Sky blue
    '#949494',  # Gray
]

COLORBLIND_SEQUENTIAL = [
    '#F7FBFF',
    '#DEEBF7',
    '#C6DBEF',
    '#9ECAE1',
    '#6BAED6',
    '#4292C6',
    '#2171B5',
    '#08519C',
    '#08306B',
]


def check_accessibility(chart_type: str, params: Dict[str, Any]) -> List[str]:
    """
    Perform accessibility checks for a chart.

    Args:
        chart_type: Type of chart
        params: Chart parameters

    Returns:
        List of accessibility recommendations/warnings
    """
    checks = []

    # Font size check
    min_font_size = 12
    checks.append(f"Ensure minimum font size of {min_font_size}px for all text")

    # Color palette check
    checks.append("Using color-blind safe palette")

    # Axis origin check
    if chart_type in ['bar', 'column']:
        checks.append("Bar charts should start at zero to avoid visual distortion")

    # Log scale suggestion
    if params.get('heavy_tailed', False):
        checks.append("Consider log scale for heavy-tailed data")

    # Category limiting
    max_categories = params.get('max_categories', 12)
    if params.get('n_categories', 0) > max_categories:
        checks.append(f"Limiting to top {max_categories} categories; others grouped as 'Other'")

    # Alt text reminder
    checks.append("Provide descriptive alt text for accessibility")

    return checks


def recommend_for_distribution(insight: Dict[str, Any], settings: Dict[str, Any]) -> List[ChartSpec]:
    """
    Recommend charts for distribution insights.

    Args:
        insight: Insight dictionary
        settings: Settings dict

    Returns:
        List of up to 3 ChartSpec objects, ordered by priority
    """
    specs = []
    stats = insight['statistics']
    column = insight['primary_columns'][0]

    # Histogram with adaptive binning
    specs.append(ChartSpec(
        chart_type='histogram',
        title=f"Distribution of {column}",
        rationale="Histogram shows the shape of the distribution with appropriate bin width",
        accessibility_checks=check_accessibility('histogram', stats),
        implementation_params={
            'x': column,
            'bins': 'auto',
            'color': COLORBLIND_CATEGORICAL[0],
        },
        priority=1,
    ))

    # Box plot with notches
    specs.append(ChartSpec(
        chart_type='boxplot',
        title=f"Box plot of {column}",
        rationale="Box plot reveals median, quartiles, and outliers clearly",
        accessibility_checks=check_accessibility('boxplot', stats),
        implementation_params={
            'y': column,
            'notch': True,
            'color': COLORBLIND_CATEGORICAL[1],
        },
        priority=2,
    ))

    # Violin plot
    specs.append(ChartSpec(
        chart_type='violin',
        title=f"Violin plot of {column}",
        rationale="Violin plot shows full distribution shape with kernel density estimate",
        accessibility_checks=check_accessibility('violin', stats),
        implementation_params={
            'y': column,
            'inner': 'box',
            'color': COLORBLIND_CATEGORICAL[2],
        },
        priority=3,
    ))

    return specs


def recommend_for_trend(insight: Dict[str, Any], settings: Dict[str, Any]) -> List[ChartSpec]:
    """
    Recommend charts for trend insights.

    Args:
        insight: Insight dictionary
        settings: Settings dict

    Returns:
        List of up to 3 ChartSpec objects, ordered by priority
    """
    specs = []
    stats = insight['statistics']
    time_col = insight['primary_columns'][0]
    measure_col = insight['primary_columns'][1]

    # Line chart with markers
    specs.append(ChartSpec(
        chart_type='line',
        title=f"{measure_col} over time",
        rationale="Line chart clearly shows temporal trend and variation",
        accessibility_checks=check_accessibility('line', stats),
        implementation_params={
            'x': time_col,
            'y': measure_col,
            'markers': True,
            'color': COLORBLIND_CATEGORICAL[0],
        },
        priority=1,
    ))

    # Scatter with trend line
    specs.append(ChartSpec(
        chart_type='scatter_with_trend',
        title=f"{measure_col} trend over time",
        rationale="Scatter plot with regression line shows individual points and overall trend",
        accessibility_checks=check_accessibility('scatter', stats),
        implementation_params={
            'x': time_col,
            'y': measure_col,
            'regression': True,
            'color': COLORBLIND_CATEGORICAL[1],
        },
        priority=2,
    ))

    # Area chart (only for additive metrics)
    specs.append(ChartSpec(
        chart_type='area',
        title=f"{measure_col} over time (area)",
        rationale="Area chart emphasizes magnitude and cumulative nature",
        accessibility_checks=check_accessibility('area', stats) + ["Use only for additive metrics"],
        implementation_params={
            'x': time_col,
            'y': measure_col,
            'baseline': 'zero',
            'color': COLORBLIND_CATEGORICAL[2],
        },
        priority=3,
    ))

    return specs


def recommend_for_group(insight: Dict[str, Any], settings: Dict[str, Any]) -> List[ChartSpec]:
    """
    Recommend charts for group difference insights.

    Args:
        insight: Insight dictionary
        settings: Settings dict

    Returns:
        List of up to 3 ChartSpec objects, ordered by priority
    """
    specs = []
    stats = insight['statistics']
    group_col = insight['primary_columns'][0]
    measure_col = insight['primary_columns'][1]

    n_groups = stats.get('n_groups', len(stats.get('groups', {})))

    # Grouped bar chart with confidence intervals
    specs.append(ChartSpec(
        chart_type='grouped_bar',
        title=f"{measure_col} by {group_col}",
        rationale="Bar chart facilitates direct comparison between groups",
        accessibility_checks=check_accessibility('bar', {'n_categories': n_groups}),
        implementation_params={
            'x': group_col,
            'y': measure_col,
            'error_bars': True,
            'palette': COLORBLIND_CATEGORICAL,
        },
        priority=1,
    ))

    # Box plot by category
    specs.append(ChartSpec(
        chart_type='boxplot_by_group',
        title=f"{measure_col} distribution by {group_col}",
        rationale="Box plots show distributions and reveal outliers within each group",
        accessibility_checks=check_accessibility('boxplot', {'n_categories': n_groups}),
        implementation_params={
            'x': group_col,
            'y': measure_col,
            'palette': COLORBLIND_CATEGORICAL,
        },
        priority=2,
    ))

    # Violin plot by category
    specs.append(ChartSpec(
        chart_type='violin_by_group',
        title=f"{measure_col} density by {group_col}",
        rationale="Violin plots reveal full distribution shape for each group",
        accessibility_checks=check_accessibility('violin', {'n_categories': n_groups}),
        implementation_params={
            'x': group_col,
            'y': measure_col,
            'inner': 'box',
            'palette': COLORBLIND_CATEGORICAL,
        },
        priority=3,
    ))

    return specs


def recommend_for_relationship(insight: Dict[str, Any], settings: Dict[str, Any]) -> List[ChartSpec]:
    """
    Recommend charts for relationship insights.

    Args:
        insight: Insight dictionary
        settings: Settings dict

    Returns:
        List of up to 3 ChartSpec objects, ordered by priority
    """
    specs = []
    stats = insight['statistics']
    col1 = insight['primary_columns'][0]
    col2 = insight['primary_columns'][1]

    n = stats.get('n', 0)

    # Scatter with regression line
    specs.append(ChartSpec(
        chart_type='scatter_with_regression',
        title=f"{col2} vs {col1}",
        rationale="Scatter plot with regression line shows relationship and spread",
        accessibility_checks=check_accessibility('scatter', stats),
        implementation_params={
            'x': col1,
            'y': col2,
            'regression': True,
            'confidence_band': True,
            'color': COLORBLIND_CATEGORICAL[0],
        },
        priority=1,
    ))

    # Hexbin for large datasets
    if n > 1000:
        specs.append(ChartSpec(
            chart_type='hexbin',
            title=f"{col2} vs {col1} (density)",
            rationale="Hexbin plot handles large datasets by showing point density",
            accessibility_checks=check_accessibility('hexbin', stats),
            implementation_params={
                'x': col1,
                'y': col2,
                'gridsize': 20,
                'cmap': COLORBLIND_SEQUENTIAL,
            },
            priority=2,
        ))
    else:
        # Regular scatter for smaller datasets
        specs.append(ChartSpec(
            chart_type='scatter',
            title=f"{col2} vs {col1}",
            rationale="Scatter plot shows individual data points clearly",
            accessibility_checks=check_accessibility('scatter', stats),
            implementation_params={
                'x': col1,
                'y': col2,
                'color': COLORBLIND_CATEGORICAL[1],
            },
            priority=2,
        ))

    # Scatter with Theil-Sen robust regression
    if stats.get('theil_sen_slope') is not None:
        specs.append(ChartSpec(
            chart_type='scatter_with_theilsen',
            title=f"{col2} vs {col1} (robust fit)",
            rationale="Theil-Sen regression is robust to outliers",
            accessibility_checks=check_accessibility('scatter', stats),
            implementation_params={
                'x': col1,
                'y': col2,
                'regression_type': 'theil_sen',
                'color': COLORBLIND_CATEGORICAL[2],
            },
            priority=3,
        ))

    return specs[:3]  # Limit to 3


def for_insight(insight: Dict[str, Any], df, settings: Dict[str, Any]) -> Tuple[List[ChartSpec], List[str]]:
    """
    Main recommendation function for a single insight.

    Args:
        insight: Insight dictionary
        df: DataFrame (for context)
        settings: Settings dict

    Returns:
        Tuple of (list of ChartSpec objects, list of accessibility checks)
    """
    detector_type = insight.get('detector_type', '')

    if detector_type == 'distribution':
        specs = recommend_for_distribution(insight, settings)
    elif detector_type == 'trend':
        specs = recommend_for_trend(insight, settings)
    elif detector_type == 'group':
        specs = recommend_for_group(insight, settings)
    elif detector_type == 'relationship':
        specs = recommend_for_relationship(insight, settings)
    else:
        # Fallback: generic recommendations
        specs = []

    # Collect all accessibility checks
    all_checks = []
    for spec in specs:
        all_checks.extend(spec.accessibility_checks)

    # Deduplicate checks
    all_checks = list(set(all_checks))

    return specs, all_checks


if __name__ == '__main__':
    # Example usage
    example_insight = {
        'id': 'D001',
        'detector_type': 'distribution',
        'primary_columns': ['age'],
        'statistics': {'mean': 35, 'std': 10, 'skew': 0.5},
    }

    settings = {'max_categories_in_charts': 12}

    specs, checks = for_insight(example_insight, None, settings)

    print("Recommended charts:")
    for spec in specs:
        print(f"\n{spec.priority}. {spec.chart_type}: {spec.title}")
        print(f"   Rationale: {spec.rationale}")
