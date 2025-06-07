import pandas as pd
import io
import re
from datetime import datetime
from encoding import detect_encoding  # your existing helper

def extract_dates_from_columns(columns):
    """
    Scan column names for two occurrences of
    'Total Caseload as at DD/MM/YYYY' and return both dates.
    """
    start_date, end_date = None, None
    for col in columns:
        matches = re.findall(
            r"Total\s+Caseload\s+as\s+at\s+(\d{2}/\d{2}/\d{4})",
            col,
            flags=re.IGNORECASE
        )
        if matches:
            if not start_date:
                start_date = matches[0]
            else:
                end_date = matches[0]
                break

    if start_date and end_date:
        start_obj = datetime.strptime(start_date, "%d/%m/%Y")
        end_obj   = datetime.strptime(end_date,   "%d/%m/%Y")
        return {
            "date_start":         start_date,
            "date_end":           end_date,
            "date_start_verbose": start_obj.strftime("%d %B %Y").upper(),
            "date_end_verbose":   end_obj.strftime("%d %B %Y").upper(),
            "month_start":        start_obj.strftime("%b").upper(),
            "month_end":          end_obj.strftime("%b").upper(),
        }

    raise ValueError(
        "Could not find the two required "
        "'Total Caseload as at DD/MM/YYYY' columns."
    )

def detect_header_and_load_csv(file):
    """
    Try reading the CSV with skiprows=0..14 until we find
    a header row that yields a 'name' column.
    """
    encoding = detect_encoding(file)
    for skip in range(0, 15):
        file.seek(0)
        try:
            df = pd.read_csv(file, skiprows=skip, encoding=encoding)
            df.columns = (
                df.columns
                  .map(str)
                  .str.lower()
                  .str.replace(r'\s+', ' ', regex=True)
                  .str.strip()
            )
            if "name" in df.columns:
                return df
        except Exception:
            continue

    raise ValueError("Could not parse CSV file with a valid header.")

def load_all_data(ratings_file, caseload_file, namelist_file):
    """
    Load and normalize ratings, namelist, and caseload.
    Caseload can be CSV or XLS/XLSX; either way, headers are
    lowercased, whitespace-stripped, and auto-detected.
    Returns: (ratings_df, caseload_df, namelist_df, period_dict)
    """
    # ——— 1️⃣ Load ratings.csv —————————————————————————
    ratings_encoding = detect_encoding(ratings_file)
    ratings_df = pd.read_csv(ratings_file, encoding=ratings_encoding)
    ratings_df.columns = (
        ratings_df.columns
          .map(str)
          .str.lower()
          .str.replace(r'\s+', ' ', regex=True)
          .str.strip()
    )

    # ——— 2️⃣ Load namelist.csv —————————————————————————
    namelist_encoding = detect_encoding(namelist_file)
    namelist_df = pd.read_csv(namelist_file, encoding=namelist_encoding)
    namelist_df.columns = (
        namelist_df.columns
          .map(str)
          .str.lower()
          .str.replace(r'\s+', ' ', regex=True)
          .str.strip()
    )

    # ——— 3️⃣ Load case_load (CSV or XLSX) ———————————————————
    # Read file into bytes once
    caseload_bytes = caseload_file.read()
    filename = getattr(caseload_file, "name", "").lower()

    if filename.endswith((".xls", ".xlsx")):
        # auto‐detect which row is the actual header
        found = False
        for skip in range(0, 15):
            bio = io.BytesIO(caseload_bytes)
            try:
                df_try = pd.read_excel(bio, skiprows=skip, header=0)
                df_try.columns = (
                    df_try.columns
                      .map(str)
                      .str.lower()
                      .str.replace(r'\s+', ' ', regex=True)
                      .str.strip()
                )
                if "name" in df_try.columns:
                    caseload_df = df_try
                    found = True
                    break
            except Exception:
                continue
        if not found:
            raise ValueError("Could not parse Excel file with a valid header.")
    else:
        caseload_file.seek(0)
        caseload_df = detect_header_and_load_csv(caseload_file)

    # ——— 4️⃣ Extract the reporting period ——————————————————
    period = extract_dates_from_columns(caseload_df.columns)

    return ratings_df, caseload_df, namelist_df, period
