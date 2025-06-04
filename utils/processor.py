
import pandas as pd
import difflib

def filter_period(df, start, end):
    possible_cols = df.columns.tolist()
    date_col = difflib.get_close_matches('Date Assigned to Current Officer', possible_cols, n=1)
    if not date_col:
        raise KeyError("Could not find a column similar to 'Date Assigned to Current Officer'")
    date_col = date_col[0]
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    mask = (df[date_col] >= pd.to_datetime(start)) & (df[date_col] <= pd.to_datetime(end))
    return df[mask]

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['name_self']
    abbreviation = name.split()[-1].strip("()")
    start_date, end_date = period['date_start'], period['date_end']
    case_df = filter_period(caseload_df.copy(), start_date, end_date)
    case_df = case_df[case_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]
    inhouse_cases = case_df[case_df['Case Type'].str.contains('In-house', case=False, na=False)].shape[0]
    assigned_cases = case_df[case_df['Case Type'].str.contains('Assigned', case=False, na=False)].shape[0]

    ratings_filtered = ratings_df[
        ratings_df['LO/LE'].str.strip().str.lower() == name.strip().lower()
    ]
    avg_rating = ratings_filtered['Rating'].mean() if not ratings_filtered.empty else None

    return {
        'name': name,
        'abbreviation': abbreviation,
        'inhouse_count': int(inhouse_cases),
        'assigned_count': int(assigned_cases),
        'avg_rating': round(avg_rating, 2) if avg_rating else 'N/A',
        'period': period
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    return [compute_officer_stats(row, caseload_df, ratings_df, period) for _, row in namelist_df.iterrows()]
