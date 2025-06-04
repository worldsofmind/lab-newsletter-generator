import pandas as pd
import chardet
import re

def detect_encoding(file):
    rawdata = file.read()
    result = chardet.detect(rawdata)
    file.seek(0)
    return result["encoding"]

def detect_header_and_load_excel(file):
    for skiprows in range(0, 15):
        try:
            df = pd.read_excel(file, skiprows=skiprows)
            if df.shape[1] > 5 and "LO/LE" in df.columns:
                print(f"Successfully parsed Excel with skiprows={skiprows}")
                return df
        except Exception:
            continue
    raise ValueError("Failed to find correct header in Excel file.")

def extract_dates_from_columns(columns):
    date_pattern = r"(\d{2}/\d{2}/\d{4})"
    dates = []
    for col in columns:
        found = re.findall(date_pattern, str(col))
        if found:
            dates.extend(found)
    if dates:
        return dates[0], dates[-1]
    raise ValueError("Could not infer date range from column headers.")

def load_all_data(ratings_file, caseload_file, namelist_file):
    ratings_encoding = detect_encoding(ratings_file)
    namelist_encoding = detect_encoding(namelist_file)

    ratings_df = pd.read_csv(ratings_file, encoding=ratings_encoding)
    namelist_df = pd.read_csv(namelist_file, encoding=namelist_encoding)
    caseload_df = detect_header_and_load_excel(caseload_file)

    caseload_df.columns = caseload_df.columns.map(str)
    date_start_raw, date_end_raw = extract_dates_from_columns(caseload_df.columns)

    period = {
        "date_start": pd.to_datetime(date_start_raw, errors='coerce'),
        "date_end": pd.to_datetime(date_end_raw, errors='coerce'),
    }

    return ratings_df, caseload_df, namelist_df, period
