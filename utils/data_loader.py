import pandas as pd
import re
from datetime import datetime
from utils.encoding import detect_encoding

def detect_header_and_load_csv(file_path):
    """
    Reads a CSV/XLS(X) file, lowercases & trims its column headers,
    and returns a DataFrame.
    """
    # detect file encoding
    with open(file_path, 'rb') as f:
        enc = detect_encoding(f)
    # load into pandas
    df = pd.read_csv(file_path, encoding=enc, dtype=str)
    # normalize column names
    df.columns = (
        df.columns
          .map(str)
          .str.lower()
          .str.replace(r'\s+', ' ', regex=True)
          .str.strip()
    )
    return df

def extract_dates_from_columns(columns):
    """
    Scans the list of column names for two headers matching
      "Total Caseload as at DD/MM/YYYY"
    and returns a dict with the raw dd/mm/YYYY strings.
    """
    start_date = end_date = None
    for col in columns:
        m = re.findall(
            r"total\s+caseload\s+as\s+at\s+(\d{2}/\d{2}/\d{4})",
            col,
            flags=re.IGNORECASE
        )
        if m:
            if not start_date:
                start_date = m[0]
            else:
                end_date = m[0]
                break

    if not (start_date and end_date):
        raise ValueError(
            f"Could not find both start and end dates in columns: {columns}"
        )

    return {
        "date_start": start_date,
        "date_end":   end_date
    }

def load_all_data(ratings_file, caseload_file, namelist_file):
    """
    Loads the three inputs and extracts the reporting period
    from the caseload column headers.
    Returns: (ratings_df, caseload_df, namelist_df, period_dict)
    """
    # — Ratings —
    with open(ratings_file, 'rb') as f:
        enc = detect_encoding(f)
    ratings_df = pd.read_csv(ratings_file, encoding=enc, dtype=str)
    ratings_df.columns = (
        ratings_df.columns
          .str.lower()
          .str.replace(r'\s+', ' ', regex=True)
          .str.strip()
    )

    # — Namelist —
    with open(namelist_file, 'rb') as f:
        enc = detect_encoding(f)
    namelist_df = pd.read_csv(namelist_file, encoding=enc, dtype=str)
    namelist_df.columns = (
        namelist_df.columns
          .str.lower()
          .str.replace(r'\s+', ' ', regex=True)
          .str.strip()
    )

    # — Caseload —
    caseload_df = detect_header_and_load_csv(caseload_file)

    # — Extract period from caseload headers —
    period = extract_dates_from_columns(caseload_df.columns)

    return ratings_df, caseload_df, namelist_df, period
