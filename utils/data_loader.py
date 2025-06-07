import pandas as pd
import re
from datetime import datetime
from utils.encoding import detect_encoding  # adjust path if yours differs

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
    file.seek(0)
    for skip in range(0, 15):
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
    lowercased and whitespace-stripped, and the true header
    is auto-detected by looking for a 'name' column.
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
    caseload_file.seek(0)
    name = getattr(caseload_file, "name", "").lower()

    if name.endswith((".xls", ".xlsx")):
        # Auto‐detect header row in Excel, just like CSV logic
        caseload_file.seek(0)
        for skip in range(0, 15):
            try:
                df = pd.read_excel(caseload_file, skiprows=skip)
                df.columns = (
                    df.columns
                      .map(str)
                      .str.lower()
                      .str.replace(r'\s+', ' ', regex=True)
                      .str.strip()
                )
                if "name" in df.columns:
                    caseload_df = df
                    break
            except Exception:
                pass
        else:
            raise ValueError("Could not parse Excel file with a valid header.")

    else:
        # Fallback to your CSV routine
        caseload_df = detect_header_and_load_csv(caseload_file)

    # ——— 4️⃣ Extract the reporting period ——————————————————
    period = extract_dates_from_columns(caseload_df.columns)

    return ratings_df, caseload_df, namelist_df, period
