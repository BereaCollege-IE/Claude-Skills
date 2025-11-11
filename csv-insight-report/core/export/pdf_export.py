"""
PDF Export Module
Exports reports to PDF format using WeasyPrint.
"""

from typing import Dict, List, Any
from pathlib import Path
from weasyprint import HTML, CSS
import sys
sys.path.append(str(Path(__file__).parent.parent))
from narrative import render, generate_limitations_section


def generate_html_report(project_data: Dict[str, Any], project_dir: str) -> str:
    """
    Generate HTML content for the report.

    Args:
        project_data: Dict containing all project data
        project_dir: Path to project directory

    Returns:
        HTML string
    """
    settings = project_data.get('settings', {})
    insights_data = project_data.get('insights', {})
    narratives = project_data.get('narratives', {})
    profile = project_data.get('profile', {})
    project_name = project_data.get('project_name', 'Untitled')

    # Build HTML
    html_parts = []

    # HTML header with CSS
    html_parts.append("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {
                size: letter;
                margin: 1in;
            }

            body {
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
            }

            h1 {
                color: #003366;
                font-size: 24pt;
                margin-top: 0.5in;
                margin-bottom: 0.25in;
                border-bottom: 2pt solid #003366;
                padding-bottom: 0.1in;
            }

            h2 {
                color: #0066CC;
                font-size: 16pt;
                margin-top: 0.3in;
                margin-bottom: 0.15in;
            }

            h3 {
                color: #0066CC;
                font-size: 13pt;
                margin-top: 0.2in;
                margin-bottom: 0.1in;
            }

            p {
                margin: 0.1in 0;
                text-align: justify;
            }

            .title-page {
                text-align: center;
                margin-top: 2in;
            }

            .title {
                font-size: 28pt;
                font-weight: bold;
                color: #003366;
                margin-bottom: 0.5in;
            }

            .metadata {
                font-size: 12pt;
                margin: 0.15in 0;
            }

            .figure {
                text-align: center;
                margin: 0.2in 0;
                page-break-inside: avoid;
            }

            .figure img {
                max-width: 6.5in;
                height: auto;
            }

            .caption {
                font-size: 10pt;
                font-style: italic;
                margin-top: 0.1in;
                text-align: center;
            }

            .caveat {
                background-color: #f5f5f5;
                border-left: 3pt solid #0066CC;
                padding: 0.1in;
                margin: 0.15in 0;
                font-size: 10pt;
            }

            .page-break {
                page-break-before: always;
            }

            .no-break {
                page-break-inside: avoid;
            }
        </style>
    </head>
    <body>
    """)

    # Title page
    from datetime import datetime
    org = settings.get('organization_name', 'Organization')
    purpose = settings.get('purpose', 'Data Analysis')
    horizon = settings.get('horizon', 'N/A')
    audience = settings.get('audience', 'Stakeholders')

    html_parts.append(f"""
    <div class="title-page">
        <div class="title">Data Insight Report:<br>{project_name}</div>
        <div class="metadata">Prepared for: {audience}</div>
        <div class="metadata">Organization: {org}</div>
        <div class="metadata">Purpose: {purpose}</div>
        <div class="metadata">Decision Horizon: {horizon}</div>
        <div class="metadata">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
    </div>

    <div class="page-break"></div>
    """)

    # Executive Summary
    html_parts.append("""
    <h1>Executive Summary</h1>
    <p>
    """)
    html_parts.append(
        f"This report presents {len(insights_data.get('top_insights', []))} key insights "
        f"from the analysis of {project_name}. Each insight is supported by statistical "
        "evidence and accompanied by recommended visualizations."
    )
    html_parts.append("</p>")

    # Key Insights
    html_parts.append("<h1>Key Insights</h1>")

    for insight in insights_data.get('top_insights', []):
        insight_id = insight['id']
        narrative_text = narratives.get(insight_id, insight['rationale'])

        html_parts.append(f'<div class="no-break">')
        html_parts.append(f"<h2>{insight['title']}</h2>")
        html_parts.append(f"<p>{narrative_text}</p>")

        # Add figure if exists
        figure_path = Path(project_dir) / 'figures' / f"{insight_id}.png"
        if figure_path.exists():
            html_parts.append('<div class="figure">')
            html_parts.append(f'<img src="{figure_path}" alt="{insight["title"]}" />')
            html_parts.append(f'<div class="caption">Figure {insight_id}: {insight["title"]}</div>')
            html_parts.append('</div>')

        # Add caveats
        if insight.get('caveats'):
            html_parts.append('<div class="caveat">')
            html_parts.append('<strong>Note:</strong> ')
            html_parts.append(' '.join(insight['caveats']))
            html_parts.append('</div>')

        html_parts.append('</div>')  # End no-break

    # Limitations
    html_parts.append('<div class="page-break"></div>')
    html_parts.append('<h1>Limitations and Assumptions</h1>')
    limitations_text = generate_limitations_section(profile, settings)
    html_parts.append(f'<p>{limitations_text}</p>')

    # Appendix
    appendix_insights = insights_data.get('appendix_insights', [])
    if appendix_insights:
        html_parts.append('<div class="page-break"></div>')
        html_parts.append('<h1>Appendix: Additional Insights</h1>')

        for insight in appendix_insights[:10]:
            html_parts.append(f'<h3>{insight["title"]}</h3>')
            html_parts.append(f'<p>{insight["rationale"]}</p>')

    # Close HTML
    html_parts.append("""
    </body>
    </html>
    """)

    return ''.join(html_parts)


def write_pdf(project_dir: str, project_data: Dict[str, Any]) -> str:
    """
    Write report to PDF format.

    Args:
        project_dir: Path to project directory
        project_data: Dict containing all project data

    Returns:
        Path to generated PDF file
    """
    # Generate HTML
    html_content = generate_html_report(project_data, project_dir)

    # Save HTML temporarily for debugging
    html_path = Path(project_dir) / 'exports' / 'report.html'
    html_path.parent.mkdir(parents=True, exist_ok=True)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Convert to PDF
    output_path = Path(project_dir) / 'exports' / 'report.pdf'

    HTML(string=html_content, base_url=str(Path(project_dir))).write_pdf(str(output_path))

    return str(output_path)


if __name__ == '__main__':
    # Example usage
    print("PDF export module ready")
