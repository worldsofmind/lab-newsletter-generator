
import pandas as pd
import difflib

def filter_period(df, date_col, start, end):
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    mask = (df[date_col] >= pd.to_datetime(start)) & (df[date_col] <= pd.to_datetime(end))
    return df[mask]

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['name_self']
    start_date, end_date = period['date_start'], period['date_end']

    # Match date column approximately
    date_col = difflib.get_close_matches(
        'Date Assigned to Current Officer',
        caseload_df.columns,
        n=1,
        cutoff=0.6
    )
    if not date_col:
        raise KeyError("Could not find a column similar to 'Date Assigned to Current Officer'")

    case_df = filter_period(caseload_df.copy(), date_col[0], start_date, end_date)
    case_df = case_df[case_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]

    inhouse_cases = case_df[case_df['Case Type'].str.contains('In-house', case=False, na=False)]
    assigned_cases = case_df[case_df['Case Type'].str.contains('Assigned', case=False, na=False)]

    officer_ratings = ratings_df[ratings_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]
    avg_rating = officer_ratings['Overall Rating'].mean() if not officer_ratings.empty else None

    return {
        'name': officer['name_display'],
        'inhouse_cases': len(inhouse_cases),
        'assigned_cases': len(assigned_cases),
        'avg_rating': round(avg_rating, 2) if avg_rating is not None else 'N/A'
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    reports = []
    for _, row in namelist_df.iterrows():
        report = compute_officer_stats(row, caseload_df, ratings_df, period)
        reports.append(report)
    return reports
