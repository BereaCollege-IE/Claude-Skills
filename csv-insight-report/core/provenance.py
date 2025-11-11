"""
Provenance Module
Tracks reproducibility information including dataset hash, settings, and library versions.
"""

import json
import hashlib
import sys
from typing import Dict, List, Any
from pathlib import Path
import polars as pl


def get_library_versions() -> Dict[str, str]:
    """
    Get versions of key libraries.

    Returns:
        Dict mapping library names to version strings
    """
    versions = {
        'python': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }

    # Try to import and get versions
    try:
        import polars
        versions['polars'] = polars.__version__
    except:
        versions['polars'] = 'unknown'

    try:
        import duckdb
        versions['duckdb'] = duckdb.__version__
    except:
        versions['duckdb'] = 'unknown'

    try:
        import altair
        versions['altair'] = altair.__version__
    except:
        versions['altair'] = 'unknown'

    try:
        import scipy
        versions['scipy'] = scipy.__version__
    except:
        versions['scipy'] = 'unknown'

    try:
        import numpy
        versions['numpy'] = numpy.__version__
    except:
        versions['numpy'] = 'unknown'

    return versions


def compute_dataset_hash(df: pl.DataFrame) -> str:
    """
    Compute SHA256 hash of dataset.

    Args:
        df: DataFrame

    Returns:
        Hex string of SHA256 hash
    """
    # Convert to CSV bytes and hash
    csv_bytes = df.write_csv().encode('utf-8')
    return hashlib.sha256(csv_bytes).hexdigest()


def write_recipe(project_dir: str, project_data: Dict[str, Any]) -> str:
    """
    Generate and write recipe.json for reproducibility.

    Args:
        project_dir: Path to project directory
        project_data: Dict containing all project information

    Returns:
        Path to written recipe.json
    """
    recipe = {
        'version': '1.0',
        'dataset': {
            'sha256': project_data.get('dataset_hash', ''),
            'rows': project_data.get('rows', 0),
            'columns': project_data.get('columns', 0),
            'schema_file': 'schema.json',
        },
        'settings': {
            'audience': project_data.get('audience', ''),
            'expertise': project_data.get('expertise', ''),
            'purpose': project_data.get('purpose', ''),
            'horizon': project_data.get('horizon', ''),
        },
        'transforms': project_data.get('transforms', []),
        'detectors': [
            {'name': 'distribution', 'params': {}},
            {'name': 'trend', 'params': {}},
            {'name': 'group', 'params': {}},
            {'name': 'relationship', 'params': {}},
        ],
        'accepted_insights': project_data.get('accepted_insights', []),
        'libraries': get_library_versions(),
        'seed': 42,
    }

    output_path = Path(project_dir) / 'recipe.json'

    with open(output_path, 'w') as f:
        json.dump(recipe, f, indent=2)

    return str(output_path)


def load_recipe(recipe_path: str) -> Dict[str, Any]:
    """
    Load recipe from JSON file.

    Args:
        recipe_path: Path to recipe.json

    Returns:
        Recipe dictionary
    """
    with open(recipe_path, 'r') as f:
        return json.load(f)


def verify_reproducibility(recipe_path: str, current_df: pl.DataFrame) -> Dict[str, Any]:
    """
    Verify that current data matches recipe.

    Args:
        recipe_path: Path to recipe.json
        current_df: Current DataFrame

    Returns:
        Dict with verification results
    """
    recipe = load_recipe(recipe_path)

    current_hash = compute_dataset_hash(current_df)
    expected_hash = recipe['dataset']['sha256']

    results = {
        'hash_match': current_hash == expected_hash,
        'expected_hash': expected_hash,
        'current_hash': current_hash,
        'expected_rows': recipe['dataset']['rows'],
        'current_rows': len(current_df),
        'expected_columns': recipe['dataset']['columns'],
        'current_columns': len(current_df.columns),
    }

    return results


if __name__ == '__main__':
    # Example usage
    print("Library versions:")
    for lib, ver in get_library_versions().items():
        print(f"  {lib}: {ver}")
