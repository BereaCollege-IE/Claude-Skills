# CSV Insight Report Generator

A fully offline Python application that transforms CSV files into audience-aware insight reports with recommended visualizations and exports to Word, PDF, and Excel.

## Features

- **Automatic Insight Detection**: Identifies distributions, trends, group differences, and relationships
- **Audience-Aware Narratives**: Tailors language and technical depth to executive, practitioner, or technical audiences
- **Smart Chart Recommendations**: Suggests 3 visualization options per insight with accessibility checks
- **Multiple Export Formats**: Word (DOCX), PDF, and Excel bundles
- **Reproducibility Tracking**: Complete provenance with dataset hashing and recipe generation
- **Privacy-First**: Optional "Private Project" mode blocks all network calls
- **PII Detection**: Automatic scanning for emails, phone numbers, SSNs, and other sensitive data

## Tech Stack

- **Python 3.11+**
- **Data Processing**: Polars 1.x, DuckDB 1.x, PyArrow 16+
- **Visualization**: Vega-Lite via Altair 5.x
- **Export**: python-docx, WeasyPrint, XlsxWriter
- **Statistics**: SciPy, NumPy, statsmodels

## Installation

```bash
# Clone the repository
cd csv-insight-report

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Command Line Usage

```python
from core.ingest import load_csv
from core.profile import summarize
from core.insights.runner import run_all
from core.config import DEFAULT_SETTINGS

# Load CSV
df, schema = load_csv('your_data.csv')

# Profile data
profile = summarize(df, schema)

# Detect insights
settings = DEFAULT_SETTINGS.copy()
settings.update({
    'audience': 'Marketing Team',
    'expertise': 'practitioner',
    'purpose': 'Q4 Campaign Planning',
    'horizon': 'quarter'
})

insights = run_all(df, schema, profile, settings)

print(f"Found {len(insights['top_insights'])} key insights")
```

## Project Structure

```
csv-insight-report/
├── core/
│   ├── ingest.py              # CSV loading and schema inference
│   ├── profile.py             # Data profiling
│   ├── insights/              # Insight detectors
│   │   ├── base.py           # Base classes
│   │   ├── distributions.py  # Distribution analysis
│   │   ├── trends.py         # Time series trends
│   │   ├── groups.py         # Group comparisons
│   │   ├── relationships.py  # Correlations and associations
│   │   └── runner.py         # Orchestration
│   ├── recommend.py           # Chart recommendations
│   ├── narrative.py           # Audience-aware text generation
│   ├── provenance.py          # Reproducibility tracking
│   ├── config.py              # Configuration management
│   └── export/                # Export modules
│       ├── docx_export.py    # Word export
│       ├── pdf_export.py     # PDF export
│       └── excel_export.py   # Excel export
├── ui/                        # Flask web interface (coming soon)
├── assets/                    # Templates and palettes
├── plugins/                   # Custom detector plugins
├── tests/                     # Test suite
└── requirements.txt
```

## Configuration

### Required Settings (First Run Wizard)

```json
{
  "audience": "Executive Leadership",
  "expertise": "executive",
  "purpose": "Budget Planning",
  "horizon": "year",
  "organization_name": "Acme Corp",
  "private_project": false
}
```

### Expertise Levels

- **executive**: Concise (1 sentence), practical significance, rounded numbers
- **practitioner**: 2-3 sentences, include statistics and intervals, actionable recommendations
- **technical**: Full statistical details, test names, effect sizes with CIs, sampling caveats

### Decision Horizons

- **now**: Immediate decisions
- **quarter**: 3-month planning
- **year**: Annual strategy

## Insight Detectors

### Distribution Detector

Identifies:
- Strong skew (|skew| > 1.0)
- Heavy tails (|kurtosis| > 3)
- Outliers (>5% outside Tukey fences)
- Multimodality

**Acceptance**: N ≥ 50

### Trend Detector

Identifies:
- Monotonic trends over time
- Uses Spearman correlation and linear regression
- Provides slope with 95% confidence intervals

**Acceptance**: N periods ≥ 12, |ρ| ≥ 0.3 or p < 0.05

### Group Detector

Identifies:
- Differences between categorical groups
- Uses Welch's t-test (2 groups) or Kruskal-Wallis (k groups)
- Reports effect sizes (Cohen's d or η²)

**Acceptance**: Per-group N ≥ 20

### Relationship Detector

Identifies:
- Numeric-numeric correlations (Pearson, Spearman)
- Categorical associations (Chi-square, Cramér's V)
- Provides Theil-Sen robust regression

**Acceptance**: N ≥ 100, |r| ≥ 0.3 or p < 0.05

## Chart Recommendations

Each insight receives 3 prioritized chart options:

- **Color-blind safe palettes** (WCAG AA compliant)
- **Minimum 12px font size**
- **Accessibility checks** (axis origin warnings, log scale suggestions)
- **Category limiting** (top K with "Other" grouping)

## Export Formats

### Word (DOCX)

- Title page with metadata
- Executive summary
- Key insights with figures
- Limitations section
- Appendix for additional insights
- Figure numbering and captions
- Alt text for accessibility

### PDF

- Generated from HTML with embedded fonts
- Identical content to Word export
- Page breaks and styling for print

### Excel

- **Summary_Tables**: Key statistics per insight
- **Figures**: Figure metadata and paths
- **Data_Sample**: Head and tail (10k rows)
- **Data_Full**: Complete data (privacy controlled)
- **Metadata**: Project settings and dataset info

## Performance Budgets

- CSV up to **250 MB**
- Cold start under **8 seconds**
- Peak RAM under **6 GB**
- Correlation sampling at **10,000 rows**
- Profile sampling at **100,000 rows** for schema inference

## Privacy and Security

### Private Project Mode

When enabled:
- Blocks all network calls at process level
- No external fonts or resources
- Encrypted project folder (platform dependent)
- PII columns excluded from exports by default

### PII Detection

Automatically scans for:
- Email addresses
- Phone numbers
- SSN patterns
- Student IDs
- Address patterns

## Reproducibility

Every project generates `recipe.json` containing:

```json
{
  "version": "1.0",
  "dataset": {
    "sha256": "...",
    "rows": 123456,
    "schema": "schema.json"
  },
  "settings": {...},
  "transforms": [],
  "detectors": [...],
  "accepted_insights": [...],
  "libraries": {...},
  "seed": 42
}
```

## Limitations

- No multiuser collaboration
- No cloud storage integration
- No streaming dashboards
- No predictive modeling beyond basic trends
- Statistical tests assume random sampling and independence

## Testing

```bash
# Run test suite
pytest tests/

# Run with coverage
pytest --cov=core tests/
```

## Contributing

This is a specialized tool for offline, private data analysis. Contributions should maintain:

- Zero network dependencies in core functionality
- Performance within stated budgets
- Reproducibility guarantees
- Privacy-first design

## License

[Specify your license]

## Roadmap

### Completed (v0.1)

- ✅ CSV ingestion with schema inference
- ✅ Data profiling
- ✅ Four insight detector types
- ✅ Audience-aware narrative generation
- ✅ Chart recommendations with accessibility
- ✅ Export to Word, PDF, Excel
- ✅ Provenance tracking
- ✅ Configuration management

### Planned (v0.2)

- 🔲 Flask-based web UI
- 🔲 Interactive chart generation with Altair
- 🔲 Chart image rendering (SVG/PNG)
- 🔲 Plugin system for custom detectors
- 🔲 Glossary generation
- 🔲 DOCX and HTML templates

### Future (v1.0)

- 🔲 Partial correlation with covariate suggestion
- 🔲 Seasonal decomposition with uncertainty
- 🔲 Optional local LLM tone polish
- 🔲 Tauri desktop application wrapper

## Support

For issues, questions, or feature requests, please [create an issue](link-to-issues).

## Authors

Built for Berea College Institutional Effectiveness

## Acknowledgments

- Color-blind safe palettes from [Paul Tol's designs](https://personal.sron.nl/~pault/)
- Statistical methods follow best practices from ASA and APA guidelines
- Accessibility standards based on WCAG 2.1 AA
