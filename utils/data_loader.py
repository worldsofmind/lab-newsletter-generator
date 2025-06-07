import pandas as pd
import re
from datetime import datetime
from utils.encoding import detect_encoding  # Retain for case_load detection

def clean_apostrophes(x):
    """
    Replace common mojibake smart quotes and control characters with a standard apostrophe.
    """
    if isinstance(x, str):
        return (
            x.replace("\u0092", "'")
             .replace("\u0091", "'")
             .replace("â€™", "'")
        )
    return x

def extract_dates_from_columns(columns):
    start_date, end_date = None, None
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

    if start_date and end_date:
        start_obj = datetime.strptime(start_date, "%d/%m/%Y")
        end_obj   = datetime.strptime(end_date,   "%d/%m/%Y")
        return {
            "date_start":         start_date,
            "date_end":           end_date,
            "date_start_verbose": start_obj.strftime("%d %B %Y").upper(),
            "date_end_verbose":   end_obj.strftime("%d %B %Y").upper(),
            "month_start":        start_obj.strftime("%b").upper(),
            "month_end":          end_obj.strftime("%b").upper(),
        }

    raise ValueError(
        "Could not find the two required 'Total Caseload as at DD/MM/YYYY' columns."
    )

def detect_header_and_load_csv(file):
    encoding = detect_encoding(file)
    file.seek(0)
    for skip in range(0, 15):
        try:
            df = pd.read_csv(file, skiprows=skip, encoding=encoding)
            # Normalize header
            df.columns = (
                df.columns.map(str)
                          .str.lower()
                          .str.replace(r'\s+', ' ', regex=True)
                          .str.strip()
            )
            if 'name' in df.columns:
                return df
        except Exception:
            continue

    raise ValueError("Could not parse CSV file with known headers.")

def load_all_data(ratings_file, caseload_file, namelist_file):
    # --- Load ratings.csv with cp1252 encoding to preserve smart quotes ---
    ratings_df = pd.read_csv(ratings_file, encoding="cp1252")
    # Normalize header
    ratings_df.columns = (
        ratings_df.columns.map(str)
                      .str.lower()
                      .str.replace(r'\s+', ' ', regex=True)
                      .str.strip()
    )
    # Clean apostrophes in headers and cells
    ratings_df.columns = [clean_apostrophes(col) for col in ratings_df.columns]
    for col in ratings_df.select_dtypes(include=["object"]):
        ratings_df[col] = ratings_df[col].apply(clean_apostrophes)

    # --- Load namelist.csv with cp1252 encoding ---
    namelist_df = pd.read_csv(namelist_file, encoding="cp1252")
    namelist_df.columns = (
        namelist_df.columns.str.lower()
                            .str.replace(r'\s+', ' ', regex=True)
                            .str.strip()
    )
    namelist_df.columns = [clean_apostrophes(col) for col in namelist_df.columns]
    for col in namelist_df.select_dtypes(include=["object"]):
        namelist_df[col] = namelist_df[col].apply(clean_apostrophes)

    # --- Load case_load.csv using header detection ---
    caseload_df = detect_header_and_load_csv(caseload_file)

    # Extract reporting period
    period = extract_dates_from_columns(caseload_df.columns)

    return ratings_df, caseload_df, namelist_df, period
