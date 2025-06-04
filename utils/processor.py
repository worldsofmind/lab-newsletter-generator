import pandas as pd
import difflib

def filter_period(df, start, end):
    date_col_candidates = difflib.get_close_matches("Date Assigned to Current Officer", df.columns, n=1)
    if not date_col_candidates:
        raise KeyError("Could not find a column similar to 'Date Assigned to Current Officer'")
    date_col = date_col_candidates[0]
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    mask = (df[date_col] >= pd.to_datetime(start)) & (df[date_col] <= pd.to_datetime(end))
    return df[mask]

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['name_self']
    start_date, end_date = period['date_start'], period['date_end']

    case_df = filter_period(caseload_df.copy(), start_date, end_date)
    case_df = case_df[case_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]

    inhouse_cases = case_df.filter(like='In-house', axis=1).sum(axis=1).sum()
    assigned_cases = case_df.filter(like='Assigned', axis=1).sum(axis=1).sum()

    rating_row = ratings_df[ratings_df['LO'].str.lower() == name.strip().lower()]
    avg_rating = rating_row.iloc[0]['Average Rating'] if not rating_row.empty else None

    return {
        'name': name,
        'inhouse_count': int(inhouse_cases),
        'assigned_count': int(assigned_cases),
        'avg_rating': round(avg_rating, 2) if avg_rating else 'N/A'
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    return [compute_officer_stats(row, caseload_df, ratings_df, period) for _, row in namelist_df.iterrows()]
