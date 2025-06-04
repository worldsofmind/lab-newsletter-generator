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

    range_pattern = r"(\d{2}/\d{2}/\d{4}) to (\d{2}/\d{2}/\d{4})"
    date_pattern = r"(\d{2}/\d{2}/\d{4})"

    for col in columns:
        if match := re.search(range_pattern, str(col)):
            return match.group(1), match.group(2)

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

    for skip in range(6, 21):
        print(f"Trying skiprows={skip}:")
        try:
            df_try = pd.read_excel(caseload_file, skiprows=skip)
            print("Columns seen:", list(df_try.columns))
            if any("Assigned" in str(col) and "to" in str(col) for col in df_try.columns):
                caseload_df = df_try
                break
        except Exception as e:
            print(f"Error reading with skiprows={skip}: {e}")
    else:
        raise ValueError("Could not locate the correct header row in case_load.xlsx")

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
