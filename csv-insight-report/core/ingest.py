"""
CSV Ingestion Module
Handles CSV loading, schema inference, type fixing, PII scanning, and dialect detection.
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import polars as pl
import chardet


# PII Detection Patterns
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'student_id': r'\b[A-Z]{1,3}\d{6,9}\b',
    'address': r'\b\d{1,5}\s+\w+\s+(street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|court|ct|boulevard|blvd)\b',
}


class CSVIngestError(Exception):
    """Custom exception for CSV ingestion errors"""
    pass


def detect_encoding(file_path: Path, sample_size: int = 100000) -> str:
    """
    Detect file encoding using chardet.

    Args:
        file_path: Path to CSV file
        sample_size: Number of bytes to sample

    Returns:
        Detected encoding string
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'


def detect_delimiter(file_path: Path, encoding: str, sample_lines: int = 10) -> str:
    """
    Detect CSV delimiter by analyzing first few lines.

    Args:
        file_path: Path to CSV file
        encoding: File encoding
        sample_lines: Number of lines to analyze

    Returns:
        Detected delimiter character
    """
    with open(file_path, 'r', encoding=encoding) as f:
        lines = [f.readline() for _ in range(sample_lines)]

    # Count occurrences of common delimiters
    delimiters = [',', '\t', ';', '|']
    counts = {d: sum(line.count(d) for line in lines) for d in delimiters}

    # Return delimiter with highest consistent count
    return max(counts, key=counts.get)


def normalize_column_name(name: str) -> str:
    """
    Normalize column names: strip whitespace, replace forbidden chars with underscore.

    Args:
        name: Original column name

    Returns:
        Normalized column name
    """
    # Strip and collapse whitespace
    name = ' '.join(name.strip().split())

    # Replace forbidden characters with underscore
    name = re.sub(r'[^\w\s-]', '_', name)
    name = re.sub(r'[\s-]+', '_', name)

    # Remove leading/trailing underscores
    name = name.strip('_')

    return name


def scan_column_for_pii(column: pl.Series) -> List[str]:
    """
    Scan a column for PII patterns.

    Args:
        column: Polars Series to scan

    Returns:
        List of detected PII types
    """
    detected = []

    # Convert to string and take sample
    sample = column.cast(pl.Utf8).drop_nulls().head(1000)

    if len(sample) == 0:
        return detected

    # Join sample values for pattern matching
    sample_text = ' '.join(sample.to_list())

    # Check each PII pattern
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, sample_text, re.IGNORECASE):
            detected.append(pii_type)

    return detected


def infer_column_type(column: pl.Series) -> str:
    """
    Infer semantic type for a column.

    Args:
        column: Polars Series

    Returns:
        Type string: int, float, bool, string, categorical, datetime, date, time, duration
    """
    dtype = column.dtype

    # Handle Polars native types
    if dtype == pl.Int64 or dtype == pl.Int32 or dtype == pl.Int16 or dtype == pl.Int8:
        return 'int'
    elif dtype == pl.Float64 or dtype == pl.Float32:
        return 'float'
    elif dtype == pl.Boolean:
        return 'bool'
    elif dtype == pl.Datetime:
        return 'datetime'
    elif dtype == pl.Date:
        return 'date'
    elif dtype == pl.Time:
        return 'time'
    elif dtype == pl.Duration:
        return 'duration'
    elif dtype == pl.Utf8:
        # Check if categorical
        unique_ratio = column.n_unique() / len(column) if len(column) > 0 else 0
        if unique_ratio < 0.05 and column.n_unique() < 50:
            return 'categorical'
        return 'string'
    else:
        return 'string'


def parse_dates(df: pl.DataFrame, date_formats: Optional[List[str]] = None) -> pl.DataFrame:
    """
    Attempt to parse string columns as dates.

    Args:
        df: Input DataFrame
        date_formats: List of date format strings to try

    Returns:
        DataFrame with parsed date columns
    """
    if date_formats is None:
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%m-%d-%Y',
            '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
        ]

    for col in df.columns:
        if df[col].dtype == pl.Utf8:
            # Try parsing as datetime
            for fmt in date_formats:
                try:
                    df = df.with_columns(
                        pl.col(col).str.strptime(pl.Datetime, fmt).alias(col)
                    )
                    break
                except:
                    continue

    return df


def load_csv(
    file_path: str,
    overrides: Optional[Dict[str, Any]] = None
) -> Tuple[pl.DataFrame, Dict[str, Any]]:
    """
    Load CSV file with automatic detection and schema inference.

    Args:
        file_path: Path to CSV file
        overrides: Optional dict with delimiter, encoding, date_formats keys

    Returns:
        Tuple of (DataFrame, schema dict)

    Raises:
        CSVIngestError: If CSV cannot be loaded or parsed
    """
    path = Path(file_path)

    if not path.exists():
        raise CSVIngestError(f"File not found: {file_path}")

    # Get overrides
    overrides = overrides or {}

    # Detect encoding
    encoding = overrides.get('encoding', detect_encoding(path))

    # Detect delimiter
    delimiter = overrides.get('delimiter', detect_delimiter(path, encoding))

    # Date formats
    date_formats = overrides.get('date_formats', None)

    try:
        # Read CSV with Polars (sample first for inference)
        df = pl.read_csv(
            file_path,
            separator=delimiter,
            encoding=encoding,
            ignore_errors=True,
            truncate_ragged_lines=True,
            infer_schema_length=100000,
        )

        # Normalize column names
        original_columns = df.columns
        normalized_columns = [normalize_column_name(col) for col in original_columns]

        # Check for duplicate normalized names
        if len(set(normalized_columns)) < len(normalized_columns):
            raise CSVIngestError("Duplicate column names after normalization")

        df.columns = normalized_columns

        # Parse dates
        df = parse_dates(df, date_formats)

        # Build schema
        schema = {
            'version': '1.0',
            'file': {
                'path': str(path.absolute()),
                'size_bytes': path.stat().st_size,
                'encoding': encoding,
                'delimiter': delimiter,
                'rows': len(df),
                'columns': len(df.columns),
            },
            'columns': []
        }

        # Analyze each column
        for idx, (orig_name, norm_name) in enumerate(zip(original_columns, normalized_columns)):
            col_data = df[norm_name]

            col_info = {
                'index': idx,
                'original_name': orig_name,
                'normalized_name': norm_name,
                'type': infer_column_type(col_data),
                'nullable': col_data.null_count() > 0,
                'null_count': col_data.null_count(),
                'null_fraction': col_data.null_count() / len(col_data) if len(col_data) > 0 else 0,
                'unique_count': col_data.n_unique(),
                'pii_flags': scan_column_for_pii(col_data),
            }

            schema['columns'].append(col_info)

        return df, schema

    except Exception as e:
        raise CSVIngestError(f"Failed to load CSV: {str(e)}")


def save_schema(schema: Dict[str, Any], output_path: str) -> None:
    """
    Save schema to JSON file.

    Args:
        schema: Schema dictionary
        output_path: Path to output JSON file
    """
    with open(output_path, 'w') as f:
        json.dump(schema, f, indent=2)


def compute_dataset_hash(df: pl.DataFrame) -> str:
    """
    Compute SHA256 hash of dataset for provenance tracking.

    Args:
        df: DataFrame

    Returns:
        Hex string of SHA256 hash
    """
    # Convert to CSV bytes and hash
    csv_bytes = df.write_csv().encode('utf-8')
    return hashlib.sha256(csv_bytes).hexdigest()


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ingest.py <csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]

    try:
        df, schema = load_csv(csv_file)

        print(f"Loaded CSV: {csv_file}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"\nSchema:")

        for col in schema['columns']:
            pii_str = f" [PII: {', '.join(col['pii_flags'])}]" if col['pii_flags'] else ""
            print(f"  {col['normalized_name']}: {col['type']}{pii_str}")

        print(f"\nDataset hash: {compute_dataset_hash(df)}")

    except CSVIngestError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
