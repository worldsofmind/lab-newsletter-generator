import pandas as pd
from datetime import datetime
import chardet
import re

def detect_encoding(file):
    file.seek(0)
    raw_data = file.read(10000)
    file.seek(0)
    return chardet.detect(raw_data)['encoding']

def extract_dates_from_columns(columns):
    print("DEBUG: Column headers seen after header row:")
    for col in columns:
        print(f"- {repr(col)}")

    # Try to find a range "dd/mm/yyyy to dd/mm/yyyy"
    range_pattern = r"(\d{2}/\d{2}/\d{4}) to (\d{2}/\d{2}/\d{4})"
    for col in columns:
        if match := re.search(range_pattern, str(col)):
            return match.group(1), match.group(2)

    # Try to find individual dates
    date_pattern = r"(\d{2}/\d{2}/\d{4})"
    for col in columns:
        dates = re.findall(date_pattern, str(col))
        if len(dates) >= 2:
            return dates[0], dates[-1]

    raise ValueError("Could not infer date range from column headers.")

def load_all_data(ratings_file, caseload_file, namelist_file):
    ratings_encoding = detect_encoding(ratings_file)
    namelist_encoding = detect_encoding(namelist_file)

    ratings_df = pd.read_csv(ratings_file, encoding=ratings_encoding)
    namelist_df = pd.read_csv(namelist_file, encoding=namelist_encoding)
    caseload_df = pd.read_excel(caseload_file, skiprows=6)  # forced to correct header row

    caseload_df.columns = caseload_df.columns.map(str)
    date_start_raw, date_end_raw = extract_dates_from_columns(caseload_df.columns)

    date_start = datetime.strptime(date_start_raw, "%d/%m/%Y").strftime("%d %b %Y")
    date_end = datetime.strptime(date_end_raw, "%d/%m/%Y").strftime("%d %b %Y")
    quarter = f"{datetime.strptime(date_start_raw, '%d/%m/%Y').strftime('%b')} - {datetime.strptime(date_end_raw, '%d/%m/%Y').strftime('%b')}"
    subject = f"Personal Statistics - {quarter} {datetime.strptime(date_end_raw, '%d/%m/%Y').year}"

    period = {
        "date_start": date_start,
        "date_end": date_end,
        "quarter": quarter,
        "email_subject": subject,
    }

    return ratings_df, caseload_df, namelist_df, period
