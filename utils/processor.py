
import pandas as pd

def filter_period(df, date_col, start, end):
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    mask = (df[date_col] >= pd.to_datetime(start)) & (df[date_col] <= pd.to_datetime(end))
    return df[mask]

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['name_self']
    start_date, end_date = period['date_start'], period['date_end']

    # Detect the date column dynamically
    date_col = next((col for col in caseload_df.columns if 'assigned' in str(col).lower() and 'as at' in str(col).lower()), None)
    if not date_col:
        raise ValueError("Could not find a valid 'Date Assigned' column in the case_load data.")

    case_df = filter_period(caseload_df.copy(), date_col, start_date, end_date)
    case_df = case_df[case_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]

    inhouse_cases = case_df[case_df['Case Type'].str.contains('In-house', case=False, na=False)]
    assigned_cases = case_df[case_df['Case Type'].str.contains('Assigned', case=False, na=False)]

    ratings = ratings_df[ratings_df['LO'].str.strip().str.lower() == name.strip().lower()]
    rating_avg = ratings['Rating'].mean() if not ratings.empty else None

    return {
        'name': officer['name_full'],
        'abbreviation': officer['abbreviation'],
        'inhouse_count': len(inhouse_cases),
        'assigned_count': len(assigned_cases),
        'rating': rating_avg
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    reports = []
    for _, row in namelist_df.iterrows():
        report = compute_officer_stats(row, caseload_df, ratings_df, period)
        reports.append(report)
    return reports
