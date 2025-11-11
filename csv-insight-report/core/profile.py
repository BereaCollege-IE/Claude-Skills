"""
Data Profiling Module
Computes missingness, cardinality, distributions, time index detection, and pairwise screening.
"""

import json
from typing import Dict, List, Any, Optional
import numpy as np
import polars as pl
from scipy import stats


def compute_missingness(df: pl.DataFrame) -> Dict[str, Any]:
    """
    Compute missingness statistics for each column.

    Args:
        df: Input DataFrame

    Returns:
        Dict with column-level missingness info
    """
    missingness = {}

    for col in df.columns:
        null_count = df[col].null_count()
        total_count = len(df)

        missingness[col] = {
            'null_count': null_count,
            'fraction': null_count / total_count if total_count > 0 else 0,
        }

        # For time series, compute run lengths of missing values
        if df[col].dtype in [pl.Datetime, pl.Date]:
            is_null = df[col].is_null().to_numpy()
            if np.any(is_null):
                # Find runs of consecutive nulls
                runs = []
                current_run = 0
                for val in is_null:
                    if val:
                        current_run += 1
                    else:
                        if current_run > 0:
                            runs.append(current_run)
                        current_run = 0
                if current_run > 0:
                    runs.append(current_run)

                missingness[col]['max_consecutive_nulls'] = max(runs) if runs else 0
                missingness[col]['mean_run_length'] = np.mean(runs) if runs else 0

    return missingness


def compute_cardinality(df: pl.DataFrame, schema: Dict[str, Any], top_k: int = 20) -> Dict[str, Any]:
    """
    Compute cardinality statistics for each column.

    Args:
        df: Input DataFrame
        schema: Schema dict from ingest
        top_k: Number of top categories to track

    Returns:
        Dict with column-level cardinality info
    """
    cardinality = {}

    for col_info in schema['columns']:
        col = col_info['normalized_name']
        col_type = col_info['type']

        unique_count = df[col].n_unique()
        total_count = len(df)

        card_info = {
            'unique_count': unique_count,
            'unique_fraction': unique_count / total_count if total_count > 0 else 0,
        }

        # For categorical or low-cardinality columns, get top values
        if col_type in ['categorical', 'string', 'bool'] or unique_count < 50:
            value_counts = df[col].value_counts().head(top_k)
            top_values = []

            for row in value_counts.iter_rows():
                value, count = row
                top_values.append({
                    'value': str(value),
                    'count': count,
                    'fraction': count / total_count if total_count > 0 else 0,
                })

            card_info['top_values'] = top_values

            # Compute coverage of top K
            if top_values:
                coverage = sum(v['fraction'] for v in top_values)
                card_info['top_k_coverage'] = coverage

        cardinality[col] = card_info

    return cardinality


def compute_numeric_distribution(series: pl.Series) -> Dict[str, Any]:
    """
    Compute distribution statistics for a numeric column.

    Args:
        series: Numeric Polars Series

    Returns:
        Dict with distribution stats
    """
    # Drop nulls
    clean = series.drop_nulls()

    if len(clean) == 0:
        return {'error': 'No non-null values'}

    values = clean.to_numpy()

    dist_stats = {
        'count': len(values),
        'mean': float(np.mean(values)),
        'median': float(np.median(values)),
        'std': float(np.std(values)),
        'mad': float(stats.median_abs_deviation(values)),
        'min': float(np.min(values)),
        'max': float(np.max(values)),
        'q25': float(np.percentile(values, 25)),
        'q75': float(np.percentile(values, 75)),
        'skew': float(stats.skew(values)),
        'kurtosis': float(stats.kurtosis(values)),
    }

    # Compute IQR and outliers (Tukey fences)
    iqr = dist_stats['q75'] - dist_stats['q25']
    lower_fence = dist_stats['q25'] - 1.5 * iqr
    upper_fence = dist_stats['q75'] + 1.5 * iqr

    outliers_low = np.sum(values < lower_fence)
    outliers_high = np.sum(values > upper_fence)

    dist_stats['iqr'] = iqr
    dist_stats['outliers_low'] = int(outliers_low)
    dist_stats['outliers_high'] = int(outliers_high)
    dist_stats['outlier_fraction'] = (outliers_low + outliers_high) / len(values)

    # Check for heavy tails
    dist_stats['heavy_tailed'] = abs(dist_stats['kurtosis']) > 3

    # Check for multimodality using Hartigan's dip test (simplified check)
    # For simplicity, we'll skip complex dip test and use kurtosis as proxy
    dist_stats['potentially_multimodal'] = dist_stats['kurtosis'] < -1

    return dist_stats


def detect_time_index(df: pl.DataFrame, schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Detect if there's a suitable time index column.

    Args:
        df: Input DataFrame
        schema: Schema dict from ingest

    Returns:
        Dict with time index info, or None if not detected
    """
    datetime_cols = [
        col['normalized_name']
        for col in schema['columns']
        if col['type'] in ['datetime', 'date']
    ]

    if not datetime_cols:
        return None

    # Check each datetime column
    for col in datetime_cols:
        # Check for monotonicity
        sorted_count = df[col].drop_nulls().is_sorted()

        if sorted_count:
            # Detect cadence
            diffs = df[col].diff().drop_nulls()

            if len(diffs) > 0:
                # Get most common difference
                mode_diff = diffs.mode().to_list()

                if mode_diff:
                    return {
                        'column': col,
                        'is_monotonic': True,
                        'typical_cadence': str(mode_diff[0]),
                        'completeness': 1.0 - (df[col].null_count() / len(df)),
                    }

    return None


def compute_correlations(df: pl.DataFrame, schema: Dict[str, Any], sample_size: int = 10000) -> Dict[str, Any]:
    """
    Compute pairwise correlations for numeric columns.

    Args:
        df: Input DataFrame
        schema: Schema dict from ingest
        sample_size: Max rows to use for correlation computation

    Returns:
        Dict with correlation matrix and significant pairs
    """
    numeric_cols = [
        col['normalized_name']
        for col in schema['columns']
        if col['type'] in ['int', 'float']
    ]

    if len(numeric_cols) < 2:
        return {'correlations': {}, 'significant_pairs': []}

    # Sample if needed
    sample_df = df if len(df) <= sample_size else df.sample(n=sample_size, seed=42)

    # Compute correlation matrix using Polars
    correlations = {}
    significant_pairs = []

    for i, col1 in enumerate(numeric_cols):
        for col2 in numeric_cols[i+1:]:
            # Get non-null pairs
            pairs = sample_df.select([col1, col2]).drop_nulls()

            if len(pairs) < 20:
                continue

            x = pairs[col1].to_numpy()
            y = pairs[col2].to_numpy()

            # Compute Pearson and Spearman
            pearson_r, pearson_p = stats.pearsonr(x, y)
            spearman_r, spearman_p = stats.spearmanr(x, y)

            pair_key = f"{col1}___{col2}"
            correlations[pair_key] = {
                'col1': col1,
                'col2': col2,
                'pearson_r': float(pearson_r),
                'pearson_p': float(pearson_p),
                'spearman_r': float(spearman_r),
                'spearman_p': float(spearman_p),
                'n_pairs': len(pairs),
            }

            # Track significant pairs
            if abs(pearson_r) >= 0.3 or pearson_p < 0.05:
                significant_pairs.append(pair_key)

    return {
        'correlations': correlations,
        'significant_pairs': significant_pairs,
    }


def compute_chi_square(df: pl.DataFrame, schema: Dict[str, Any], sample_size: int = 10000) -> Dict[str, Any]:
    """
    Compute chi-square tests for categorical pairs.

    Args:
        df: Input DataFrame
        schema: Schema dict from ingest
        sample_size: Max rows to use

    Returns:
        Dict with chi-square test results
    """
    categorical_cols = [
        col['normalized_name']
        for col in schema['columns']
        if col['type'] in ['categorical', 'string', 'bool']
        and col['unique_count'] < 50  # Limit to reasonable cardinality
    ]

    if len(categorical_cols) < 2:
        return {'tests': {}, 'significant_pairs': []}

    # Sample if needed
    sample_df = df if len(df) <= sample_size else df.sample(n=sample_size, seed=42)

    tests = {}
    significant_pairs = []

    for i, col1 in enumerate(categorical_cols):
        for col2 in categorical_cols[i+1:]:
            # Create contingency table
            try:
                crosstab = sample_df.group_by([col1, col2]).count()

                # Convert to pivot table
                pivot = crosstab.pivot(values='count', index=col1, columns=col2)

                # Fill nulls with 0
                pivot_np = pivot.select(pl.all().exclude(col1)).fill_null(0).to_numpy()

                # Perform chi-square test
                chi2, p_value, dof, expected = stats.chi2_contingency(pivot_np)

                # Compute Cramér's V
                n = pivot_np.sum()
                min_dim = min(pivot_np.shape[0], pivot_np.shape[1])
                cramers_v = np.sqrt(chi2 / (n * (min_dim - 1))) if min_dim > 1 else 0

                pair_key = f"{col1}___{col2}"
                tests[pair_key] = {
                    'col1': col1,
                    'col2': col2,
                    'chi2': float(chi2),
                    'p_value': float(p_value),
                    'cramers_v': float(cramers_v),
                    'n': int(n),
                }

                if p_value < 0.05 and cramers_v > 0.3:
                    significant_pairs.append(pair_key)

            except Exception:
                continue

    return {
        'tests': tests,
        'significant_pairs': significant_pairs,
    }


def summarize(df: pl.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main profiling function that computes all statistics.

    Args:
        df: Input DataFrame
        schema: Schema dict from ingest

    Returns:
        Complete profile dict
    """
    profile = {
        'version': '1.0',
        'timestamp': pl.datetime('now').to_list()[0].isoformat(),
        'missingness': compute_missingness(df),
        'cardinality': compute_cardinality(df, schema),
        'distributions': {},
        'time_index': detect_time_index(df, schema),
        'correlations': compute_correlations(df, schema),
        'chi_square': compute_chi_square(df, schema),
    }

    # Compute distributions for numeric columns
    for col_info in schema['columns']:
        col = col_info['normalized_name']
        col_type = col_info['type']

        if col_type in ['int', 'float']:
            profile['distributions'][col] = compute_numeric_distribution(df[col])

    return profile


def save_profile(profile: Dict[str, Any], output_path: str) -> None:
    """
    Save profile to JSON file.

    Args:
        profile: Profile dictionary
        output_path: Path to output JSON file
    """
    with open(output_path, 'w') as f:
        json.dump(profile, f, indent=2)


if __name__ == '__main__':
    # Example usage
    import sys
    from .ingest import load_csv

    if len(sys.argv) < 2:
        print("Usage: python profile.py <csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]

    try:
        df, schema = load_csv(csv_file)
        profile = summarize(df, schema)

        print(f"Profiled: {csv_file}")
        print(f"\nTime index: {profile['time_index']}")
        print(f"\nSignificant correlations: {len(profile['correlations']['significant_pairs'])}")
        print(f"Significant chi-square pairs: {len(profile['chi_square']['significant_pairs'])}")

        # Show distributions
        print(f"\nDistributions:")
        for col, dist in profile['distributions'].items():
            if 'error' not in dist:
                print(f"  {col}: mean={dist['mean']:.2f}, std={dist['std']:.2f}, skew={dist['skew']:.2f}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
