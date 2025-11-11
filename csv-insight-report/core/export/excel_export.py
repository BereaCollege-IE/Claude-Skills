"""
Excel Export Module
Exports data bundle to Excel format using XlsxWriter.
"""

from typing import Dict, List, Any
from pathlib import Path
import xlsxwriter
import polars as pl


def write_excel(project_dir: str, project_data: Dict[str, Any]) -> str:
    """
    Write data bundle to Excel format.

    Args:
        project_dir: Path to project directory
        project_data: Dict containing all project data including:
            - settings: Settings dict
            - insights: Insights dict
            - df: DataFrame with data
            - schema: Schema dict
            - profile: Profile dict

    Returns:
        Path to generated Excel file
    """
    settings = project_data.get('settings', {})
    insights_data = project_data.get('insights', {})
    df = project_data.get('df')
    schema = project_data.get('schema', {})
    profile = project_data.get('profile', {})

    output_path = Path(project_dir) / 'exports' / 'bundle.xlsx'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create workbook
    workbook = xlsxwriter.Workbook(str(output_path))

    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#003366',
        'font_color': 'white',
        'border': 1,
    })

    cell_format = workbook.add_format({
        'border': 1,
    })

    number_format = workbook.add_format({
        'border': 1,
        'num_format': '0.00',
    })

    # Tab 1: Summary Tables
    summary_sheet = workbook.add_worksheet('Summary_Tables')

    row = 0

    # Write each insight as a summary table
    for insight in insights_data.get('top_insights', []):
        # Write insight title
        summary_sheet.write(row, 0, insight['title'], header_format)
        row += 1

        # Write statistics
        stats = insight.get('statistics', {})
        for key, value in stats.items():
            summary_sheet.write(row, 0, key, cell_format)

            if isinstance(value, (int, float)):
                summary_sheet.write(row, 1, value, number_format)
            elif isinstance(value, dict):
                summary_sheet.write(row, 1, str(value), cell_format)
            elif isinstance(value, list):
                summary_sheet.write(row, 1, ', '.join(map(str, value)), cell_format)
            else:
                summary_sheet.write(row, 1, str(value), cell_format)

            row += 1

        row += 2  # Spacing

    # Adjust column widths
    summary_sheet.set_column(0, 0, 30)
    summary_sheet.set_column(1, 1, 40)

    # Tab 2: Figures (metadata)
    figures_sheet = workbook.add_worksheet('Figures')

    # Write header
    figures_sheet.write(0, 0, 'Insight ID', header_format)
    figures_sheet.write(0, 1, 'Title', header_format)
    figures_sheet.write(0, 2, 'Figure Path', header_format)

    row = 1
    for insight in insights_data.get('top_insights', []):
        insight_id = insight['id']
        figures_sheet.write(row, 0, insight_id, cell_format)
        figures_sheet.write(row, 1, insight['title'], cell_format)

        figure_path = Path(project_dir) / 'figures' / f"{insight_id}.png"
        if figure_path.exists():
            figures_sheet.write(row, 2, str(figure_path), cell_format)
        else:
            figures_sheet.write(row, 2, 'Not generated', cell_format)

        row += 1

    figures_sheet.set_column(0, 0, 15)
    figures_sheet.set_column(1, 1, 50)
    figures_sheet.set_column(2, 2, 60)

    # Tab 3: Data Sample (head and tail)
    if df is not None:
        sample_sheet = workbook.add_worksheet('Data_Sample')

        # Write column headers
        for col_idx, col_name in enumerate(df.columns):
            sample_sheet.write(0, col_idx, col_name, header_format)

        # Write first 5000 rows (head)
        head_data = df.head(5000)
        for row_idx, row_data in enumerate(head_data.iter_rows()):
            for col_idx, value in enumerate(row_data):
                if value is None:
                    sample_sheet.write(row_idx + 1, col_idx, '', cell_format)
                elif isinstance(value, (int, float)):
                    sample_sheet.write(row_idx + 1, col_idx, value, number_format)
                else:
                    sample_sheet.write(row_idx + 1, col_idx, str(value), cell_format)

        # Adjust column widths
        for col_idx in range(len(df.columns)):
            sample_sheet.set_column(col_idx, col_idx, 15)

    # Tab 4: Data Full (optional, privacy controlled)
    privacy_mode = settings.get('private_project', False)

    if df is not None and not privacy_mode:
        full_sheet = workbook.add_worksheet('Data_Full')

        # Write column headers
        for col_idx, col_name in enumerate(df.columns):
            full_sheet.write(0, col_idx, col_name, header_format)

        # Write all rows (with limit to avoid Excel row limit)
        max_rows = min(len(df), 1048575)  # Excel row limit
        for row_idx, row_data in enumerate(df.head(max_rows).iter_rows()):
            for col_idx, value in enumerate(row_data):
                if value is None:
                    full_sheet.write(row_idx + 1, col_idx, '', cell_format)
                elif isinstance(value, (int, float)):
                    full_sheet.write(row_idx + 1, col_idx, value, number_format)
                else:
                    full_sheet.write(row_idx + 1, col_idx, str(value), cell_format)

        # Adjust column widths
        for col_idx in range(len(df.columns)):
            full_sheet.set_column(col_idx, col_idx, 15)

    # Tab 5: Metadata
    meta_sheet = workbook.add_worksheet('Metadata')

    row = 0

    # Project settings
    meta_sheet.write(row, 0, 'Project Settings', header_format)
    row += 1

    for key, value in settings.items():
        meta_sheet.write(row, 0, key, cell_format)
        meta_sheet.write(row, 1, str(value), cell_format)
        row += 1

    row += 2

    # Dataset info
    meta_sheet.write(row, 0, 'Dataset Information', header_format)
    row += 1

    if schema:
        file_info = schema.get('file', {})
        for key, value in file_info.items():
            meta_sheet.write(row, 0, key, cell_format)
            meta_sheet.write(row, 1, str(value), cell_format)
            row += 1

    meta_sheet.set_column(0, 0, 30)
    meta_sheet.set_column(1, 1, 50)

    # Close workbook
    workbook.close()

    return str(output_path)


if __name__ == '__main__':
    # Example usage
    print("Excel export module ready")
