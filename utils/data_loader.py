import pandas as pd
import re
from datetime import datetime
from utils.encoding import detect_encoding  # Assuming this import path is correct

def extract_dates_from_columns(columns):
    start_date = end_date = None
    for col in columns:
        matches = re.findall(
            r"Total\s+Caseload\s+as\s+at\s+(\d{2}/\d{2}/\d{4})",
            col,
            flags=re.IGNORECASE
        )
        if matches:
            if not start_date:
                start_date = matches[0]
            else:
                end_date = matches[0]
                break

    if not (start_date and end_date):
        raise ValueError(
            "Could not find two 'Total Caseload as at DD/MM/YYYY' columns."
        )

    start_obj = datetime.strptime(start_date, "%d/%m/%Y")
    end_obj   = datetime.strptime(end_date,   "%d/%m/%Y")
    return {
        "date_start":          start_date,
        "date_end":            end_date,
        "date_start_verbose":  start_obj.strftime("%d %B %Y").upper(),
        "date_end_verbose":    end_obj.strftime("%d %B %Y").upper(),
        "month_start":         start_obj.strftime("%b").upper(),
        "month_end":           end_obj.strftime("%b").upper()
    }

def _read_csv_fallback(file_obj, **read_csv_kwargs):
    """
    Try to read with detected encoding; if that raises a UnicodeDecodeError,
    retry with cp1252. Returns a DataFrame.
    """
    enc = detect_encoding(file_obj)
    for encoding in (enc, "cp1252"):
        try:
            file_obj.seek(0)
            return pd.read_csv(file_obj, encoding=encoding, **read_csv_kwargs)
        except UnicodeDecodeError:
            continue
    file_obj.seek(0)
    raise UnicodeDecodeError(
        f"Unable to decode file with {enc!r} or cp1252."
    )

def detect_header_and_load_csv(file_obj):
    """
    Attempts to read a CSV with up to 15 different skiprows offsets,
    first with the detected encoding, then falling back to cp1252.
    Returns the DataFrame with lowercase, stripped column names.
    """
    for skip in range(15):
        try:
            df = _read_csv_fallback(file_obj, skiprows=skip)
            df.columns = (
                df.columns
                  .map(str)
                  .str.lower()
                  .str.replace(r"\s+", " ", regex=True)
                  .str.strip()
            )
            if "name" in df.columns:
                return df
        except Exception:
            continue
    raise ValueError("Could not parse CSV file with known headers.")

def load_all_data(ratings_file, caseload_file, namelist_file):
    # — Ratings
    ratings_df = _read_csv_fallback(ratings_file)
    ratings_df.columns = (
        ratings_df.columns
                  .map(str)
                  .str.lower()
                  .str.replace(r"\s+", " ", regex=True)
                  .str.strip()
    )

    # — Namelist
    namelist_df = _read_csv_fallback(namelist_file)
    namelist_df.columns = (
        namelist_df.columns
                    .map(str)
                    .str.lower()
                    .str.replace(r"\s+", " ", regex=True)
                    .str.strip()
    )

    # — Caseload
    caseload_df = detect_header_and_load_csv(caseload_file)

    # — Extract the period from the column names
    period = extract_dates_from_columns(caseload_df.columns)

    return ratings_df, caseload_df, namelist_df, period
