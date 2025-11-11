"""
Configuration Management Module
Handles loading and saving project settings.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from enum import Enum


class ExpertiseLevel(str, Enum):
    """Expertise level options"""
    EXECUTIVE = "executive"
    PRACTITIONER = "practitioner"
    TECHNICAL = "technical"


class DecisionHorizon(str, Enum):
    """Decision horizon options"""
    NOW = "now"
    QUARTER = "quarter"
    YEAR = "year"


# Default settings
DEFAULT_SETTINGS = {
    # Required fields
    'audience': '',
    'expertise': ExpertiseLevel.PRACTITIONER.value,
    'purpose': '',
    'horizon': DecisionHorizon.QUARTER.value,

    # Branding
    'organization_name': '',
    'logo_file': None,
    'palette_categorical': [
        '#0173B2', '#DE8F05', '#029E73', '#CC78BC',
        '#CA9161', '#ECE133', '#56B4E9', '#949494'
    ],
    'palette_sequential': [
        '#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1',
        '#6BAED6', '#4292C6', '#2171B5', '#08519C', '#08306B'
    ],
    'number_format': 'en_US',
    'date_locale': 'en_US',

    # Privacy
    'private_project': False,

    # Analysis parameters
    'max_categories_in_charts': 12,
    'min_sample_for_parametrics': 20,
    'trend_min_periods': 12,
    'correlation_min_abs': 0.3,
    'max_insights_to_surface': 8,

    # Optional features
    'enable_local_llm': False,
    'llm_model_path': None,
}


def load_settings(project_dir: str) -> Dict[str, Any]:
    """
    Load settings from project directory.

    Args:
        project_dir: Path to project directory

    Returns:
        Settings dictionary
    """
    settings_path = Path(project_dir) / 'settings.json'

    if settings_path.exists():
        with open(settings_path, 'r') as f:
            settings = json.load(f)

        # Merge with defaults (in case new settings were added)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(settings)
        return merged
    else:
        return DEFAULT_SETTINGS.copy()


def save_settings(project_dir: str, settings: Dict[str, Any]) -> str:
    """
    Save settings to project directory.

    Args:
        project_dir: Path to project directory
        settings: Settings dictionary

    Returns:
        Path to saved settings file
    """
    settings_path = Path(project_dir) / 'settings.json'
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)

    return str(settings_path)


def validate_settings(settings: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that required settings are present.

    Args:
        settings: Settings dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['audience', 'expertise', 'purpose', 'horizon']

    for field in required_fields:
        if not settings.get(field):
            return False, f"Required field '{field}' is missing or empty"

    # Validate expertise level
    if settings['expertise'] not in [e.value for e in ExpertiseLevel]:
        return False, f"Invalid expertise level: {settings['expertise']}"

    # Validate decision horizon
    if settings['horizon'] not in [h.value for h in DecisionHorizon]:
        return False, f"Invalid decision horizon: {settings['horizon']}"

    return True, None


def create_project_config(config_path: str) -> str:
    """
    Create a global config file for storing project references.

    Args:
        config_path: Path to config file

    Returns:
        Path to created config file
    """
    config = {
        'version': '1.0',
        'recent_projects': [],
        'default_settings': DEFAULT_SETTINGS,
    }

    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    return str(config_path)


if __name__ == '__main__':
    # Example usage
    print("Configuration module ready")
    print(f"Default expertise levels: {[e.value for e in ExpertiseLevel]}")
    print(f"Default decision horizons: {[h.value for h in DecisionHorizon]}")
