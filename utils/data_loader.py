import pandas as pd
from datetime import datetime
import chardet
import re

def detect_header_and_load_excel(file):
    for header in range(25):
        df_try = pd.read_excel(file, skiprows=header)
        print(f"Trying skiprows={header}:")
        print("Columns seen:", [str(col) for col in df_try.columns])
        if any("Officer" in str(col) or "LO/LE" in str(col) or "In-house" in str(col) or "Assigned Cases" in str(col) for col in df_try.columns):
            file.seek(0)
            final_df = pd.read_excel(file, skiprows=header)
            print("✅ Final selected header (columns):", final_df.columns.tolist())
            return final_df
    raise ValueError("Failed to find header row in case_load file.")

def detect_encoding(file):
    file.seek(0)
    raw_data = file.read(10000)
    file.seek(0)
    return chardet.detect(raw_data)['encoding']

def extract_dates_from_columns(columns):
    print("DEBUG: Column headers seen after header row:")
    for col in columns:
        print(f"- {repr(col)}")

    date_pattern = r"(\d{2}/\d{2}/\d{4})"
    range_pattern = r"(\d{2}/\d{2}/\d{4}) to (\d{2}/\d{2}/\d{4})"

    for col in columns:
        if match := re.search(range_pattern, str(col)):
            return match.group(1), match.group(2)

    for col in columns:
        dates = re.findall(date_pattern, str(col))
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
