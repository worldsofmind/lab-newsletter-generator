import pandas as pd
import chardet
import re

from utils.encoding import detect_encoding

def extract_dates_from_columns(columns):
    date_pattern = r"(\d{2}/\d{2}/\d{4})"
    for col in columns:
        dates = re.findall(date_pattern, str(col))
        if dates:
            return dates[0], dates[-1]
    raise ValueError("Could not infer date range from column headers.")

def detect_header_and_load_excel(file):
    for skip in range(15):
        df = pd.read_excel(file, skiprows=skip)
        if 'LO/LE' in df.columns or any("Caseload" in str(col) for col in df.columns):
            return df
    raise ValueError("Could not find a valid header row in Excel file.")

def load_all_data(ratings_file, caseload_file, namelist_file):
    ratings_encoding = detect_encoding(ratings_file)
    namelist_encoding = detect_encoding(namelist_file)

    ratings_df = pd.read_csv(ratings_file, encoding=ratings_encoding)
    namelist_df = pd.read_csv(namelist_file, encoding=namelist_encoding)
    caseload_df = detect_header_and_load_excel(caseload_file)

    caseload_df.columns = caseload_df.columns.map(str)
    date_start_raw, date_end_raw = extract_dates_from_columns(caseload_df.columns)

    return ratings_df, caseload_df, namelist_df, {
        "date_start": pd.to_datetime(date_start_raw),
        "date_end": pd.to_datetime(date_end_raw)
    }
