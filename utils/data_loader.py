import pandas as pd
import re
from utils.encoding import detect_encoding

def extract_dates_from_columns(columns):
    date_pattern = r"(\d{2}/\d{2}/\d{4})"
    extracted_dates = []
    for col in columns:
        matches = re.findall(date_pattern, str(col))
        if matches:
            extracted_dates.extend(matches)
    if len(extracted_dates) >= 2:
        # Return first and last detected dates in sorted order
        unique_dates = sorted(set(pd.to_datetime(extracted_dates, dayfirst=True)))
        return unique_dates[0].strftime('%d/%m/%Y'), unique_dates[-1].strftime('%d/%m/%Y')
    raise ValueError("❌ Could not infer start and end dates from column headers.")

def detect_header_and_load_csv(file):
    encoding = detect_encoding(file)
    file.seek(0)
    for skip in range(0, 15):
        try:
            df = pd.read_csv(file, skiprows=skip, encoding=encoding)
            if 'Name' in df.columns:
                return df
        except Exception:
            continue
    raise ValueError("Could not parse CSV file with known headers.")

def load_all_data(ratings_file, caseload_file, namelist_file):
    ratings_encoding = detect_encoding(ratings_file)
    ratings_df = pd.read_csv(ratings_file, encoding=ratings_encoding)

    namelist_encoding = detect_encoding(namelist_file)
    namelist_df = pd.read_csv(namelist_file, encoding=namelist_encoding)
    namelist_df.columns = namelist_df.columns.str.strip()

    caseload_df = detect_header_and_load_csv(caseload_file)
    caseload_df.columns = caseload_df.columns.map(str)

    date_start_raw, date_end_raw = extract_dates_from_columns(caseload_df.columns)
    return ratings_df, caseload_df, namelist_df, {
        "date_start": date_start_raw,
        "date_end": date_end_raw
    }
