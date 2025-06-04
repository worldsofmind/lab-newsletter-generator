
import pandas as pd

def filter_period(df, date_col, start, end):
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    mask = (df[date_col] >= pd.to_datetime(start)) & (df[date_col] <= pd.to_datetime(end))
    return df[mask]

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['name_self']
    abbreviation = officer['abbreviation']
    full_display_name = f"{name} ({abbreviation})"

    start_date, end_date = period['date_start'], period['date_end']

    # Auto-detect relevant date and case columns
    date_col = None
    for col in caseload_df.columns:
        if 'assigned' in col.lower() and 'date' in col.lower():
            date_col = col
            break
    if not date_col:
        raise KeyError("Could not find a column similar to 'Date Assigned to Current Officer'")

    case_df = filter_period(caseload_df.copy(), date_col, start_date, end_date)
    case_df = case_df[case_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]

    inhouse_cases = case_df[case_df['Case Type'].str.contains('In-house', case=False, na=False)]
    assigned_cases = case_df[case_df['Case Type'].str.contains('Assigned', case=False, na=False)]

    officer_ratings = ratings_df[ratings_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]
    avg_rating = officer_ratings['Overall Rating'].mean() if not officer_ratings.empty else None

    return {
        'name': full_display_name,
        'inhouse_count': len(inhouse_cases),
        'assigned_count': len(assigned_cases),
        'avg_rating': round(avg_rating, 2) if avg_rating else "N/A"
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    reports = []
    for _, row in namelist_df.iterrows():
        report = compute_officer_stats(row, caseload_df, ratings_df, period)
        reports.append(report)
    return reports
