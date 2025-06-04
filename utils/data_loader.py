
import pandas as pd
import re
from datetime import datetime
from utils.encoding import detect_encoding

def extract_dates_from_columns(columns):
    # Look for patterns like "08/05/2024 to 02/08/2024"
    range_pattern = r"(\d{2}/\d{2}/\d{4}) to (\d{2}/\d{2}/\d{4})"
    for col in columns:
        match = re.search(range_pattern, str(col))
        if match:
            return match.group(1), match.group(2)
    raise ValueError("Could not infer date range from column headers.")

def detect_header_and_load_excel(file):
    for skip in range(15):
        df = pd.read_excel(file, skiprows=skip)
        df.columns = df.columns.map(str)
        if any(re.search(r"\d{2}/\d{2}/\d{4} to \d{2}/\d{2}/\d{4}", col) for col in df.columns):
            print(f"Successfully parsed Excel with skiprows={skip}")
            return df
    raise ValueError("Failed to detect correct header row for Excel.")

def load_all_data(ratings_file, caseload_file, namelist_file):
    ratings_encoding = detect_encoding(ratings_file)
    namelist_encoding = detect_encoding(namelist_file)

    ratings_df = pd.read_csv(ratings_file, encoding=ratings_encoding)
    namelist_df = pd.read_csv(namelist_file, encoding=namelist_encoding)
    caseload_df = detect_header_and_load_excel(caseload_file)

    date_start_raw, date_end_raw = extract_dates_from_columns(caseload_df.columns)
    date_start = datetime.strptime(date_start_raw, "%d/%m/%Y").strftime("%d %b %Y")
    date_end = datetime.strptime(date_end_raw, "%d/%m/%Y").strftime("%d %b %Y")
    quarter = f"{datetime.strptime(date_start_raw, '%d/%m/%Y').strftime('%b')}–{datetime.strptime(date_end_raw, '%d/%m/%Y').strftime('%b')}"
    subject = f"Personal Statistics - {quarter} {datetime.strptime(date_end_raw, '%d/%m/%Y').year}"

    period = {
        "date_start": date_start_raw,
        "date_end": date_end_raw,
        "quarter": quarter,
        "subject": subject,
        "date_range_text": f"{date_start} to {date_end}",
    }

    return ratings_df, caseload_df, namelist_df, period
