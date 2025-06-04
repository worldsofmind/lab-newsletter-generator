import pandas as pd
from datetime import datetime
import chardet

def detect_header_and_load_excel(file):
    for header in range(10):
        df_try = pd.read_excel(file, skiprows=header)
        if any("Officer" in str(col) or "LO/LE" in str(col) for col in df_try.columns):
            file.seek(0)
            return pd.read_excel(file, skiprows=header)
    raise ValueError("Failed to find header row in case_load file.")

def detect_encoding(file):
    file.seek(0)
    raw_data = file.read(10000)
    file.seek(0)
    return chardet.detect(raw_data)['encoding']

def load_all_data(ratings_file, caseload_file, namelist_file):
    ratings_encoding = detect_encoding(ratings_file)
    namelist_encoding = detect_encoding(namelist_file)

    ratings_df = pd.read_csv(ratings_file, encoding=ratings_encoding)
    namelist_df = pd.read_csv(namelist_file, encoding=namelist_encoding)
    caseload_df = detect_header_and_load_excel(caseload_file)

    date_col = next((col for col in caseload_df.columns if 'Date' in col and 'Assigned' in col), None)
    if date_col is None:
        raise ValueError("Could not identify the 'Date Assigned' column in case_load.")

    caseload_df[date_col] = pd.to_datetime(caseload_df[date_col], errors='coerce')
    period_start = caseload_df[date_col].min().strftime("%d %b %Y")
    period_end = caseload_df[date_col].max().strftime("%d %b %Y")
    quarter = f"{caseload_df[date_col].min().strftime('%b')} - {caseload_df[date_col].max().strftime('%b')}"
    subject = f"Personal Statistics - {quarter} {caseload_df[date_col].max().year}"

    period = {
        "date_start": period_start,
        "date_end": period_end,
        "quarter": quarter,
        "email_subject": subject,
    }

    return ratings_df, caseload_df, namelist_df, period
