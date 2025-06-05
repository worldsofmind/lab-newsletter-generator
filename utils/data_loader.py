
import pandas as pd
import re
from utils.encoding import detect_encoding

def extract_dates_from_columns(columns):
    date_pattern = r"(\d{2}/\d{2}/\d{4})"
    found = re.findall(date_pattern, " ".join(columns))
    if len(found) >= 2:
        try:
            date_start = datetime.strptime(found[0], "%d/%m/%Y")
            date_end = datetime.strptime(found[1], "%d/%m/%Y")
            return {
                "date_start": found[0],
                "date_end": found[1],
                "date_start_verbose": date_start.strftime("%d %B %Y").upper(),
                "date_end_verbose": date_end.strftime("%d %B %Y").upper(),
                "month_start": date_start.strftime("%b").upper(),
                "month_end": date_end.strftime("%b").upper()
            }
        except Exception:
            pass
    raise ValueError("Could not extract two dates from column headers.")

def detect_header_and_load_csv(file):
    encoding = detect_encoding(file)
    file.seek(0)
    for skip in range(0, 15):
        try:
            df = pd.read_csv(file, skiprows=skip, encoding=encoding)
            if 'Name' in df.columns or 'name' in df.columns:
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

    period = extract_dates_from_columns(caseload_df.columns)
    return ratings_df, caseload_df, namelist_df, period
