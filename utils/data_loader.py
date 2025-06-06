import pandas as pd
import re
from datetime import datetime
from utils.encoding import detect_encoding # Assuming this import path is correct

def extract_dates_from_columns(columns):
    start_date, end_date = None, None
    for col in columns:
        matches = re.findall(r"Total\s+Caseload\s+as\s+at\s+(\d{2}/\d{2}/\d{4})", col, flags=re.IGNORECASE)
        if matches:
            if not start_date:
                start_date = matches[0]
            else:
                end_date = matches[0]
                break
    if start_date and end_date:
        start_obj = datetime.strptime(start_date, "%d/%m/%Y")
        end_obj = datetime.strptime(end_date, "%d/%m/%Y")
        return {
            "date_start": start_date,
            "date_end": end_date,
            "date_start_verbose": start_obj.strftime("%d %B %Y").upper(),
            "date_end_verbose": end_obj.strftime("%d %B %Y").upper(),
            "month_start": start_obj.strftime("%b").upper(),
            "month_end": end_obj.strftime("%b").upper()
        }
    raise ValueError("Could not find the two required 'Total Caseload as at DD/MM/YYYY' columns.")


def detect_header_and_load_csv(file):
    encoding = detect_encoding(file)
    file.seek(0)
    for skip in range(0, 15):
        try:
            df = pd.read_csv(file, skiprows=skip, encoding=encoding)
            # IMPORTANT CHANGE: Convert columns to lowercase and strip whitespace
            df.columns = df.columns.map(str).str.lower().str.strip()
            if 'name' in df.columns: # Check for lowercase 'name' now
                return df
        except Exception:
            continue
    raise ValueError("Could not parse CSV file with known headers.")


def load_all_data(ratings_file, caseload_file, namelist_file):
    # Load ratings.csv
    ratings_encoding = detect_encoding(ratings_file)
    ratings_df = pd.read_csv(ratings_file, encoding=ratings_encoding)
    # IMPORTANT CHANGE: Convert columns to lowercase and strip whitespace for ratings_df
    ratings_df.columns = ratings_df.columns.map(str).str.lower().str.strip()

    # Load namelist.csv
    namelist_encoding = detect_encoding(namelist_file)
    namelist_df = pd.read_csv(namelist_file, encoding=namelist_encoding)
    # IMPORTANT CHANGE: Convert columns to lowercase and strip whitespace for namelist_df
    namelist_df.columns = namelist_df.columns.str.lower().str.strip()

    # Load case_load.csv using the helper function
    caseload_df = detect_header_and_load_csv(caseload_file)
    # The detect_header_and_load_csv function now handles lowercasing and stripping for caseload_df

    period = extract_dates_from_columns(caseload_df.columns)

    return ratings_df, caseload_df, namelist_df, period
