
import pandas as pd

def filter_period(df, date_col, start, end):
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    mask = (df[date_col] >= pd.to_datetime(start)) & (df[date_col] <= pd.to_datetime(end))
    return df[mask]

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['name_self']
    start_date, end_date = period['date_start'], period['date_end']

    case_df = filter_period(caseload_df.copy(), 'Date Assigned to Current Officer', start_date, end_date)
    case_df = case_df[case_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]

    inhouse_cases = case_df[case_df['Case Type'].str.contains('In-house', case=False, na=False)]
    assigned_cases = case_df[case_df['Case Type'].str.contains('Assigned', case=False, na=False)]

    officer_ratings = ratings_df[
        ratings_df['LO'].str.strip().str.lower() == name.strip().lower()
        ]

    report = {
        'name': name,
        'inhouse_count': len(inhouse_cases),
        'assigned_count': len(assigned_cases),
        'ratings_count': len(officer_ratings),
    }
    return report

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    reports = []
    for _, row in namelist_df.iterrows():
        try:
            report = compute_officer_stats(row, caseload_df, ratings_df, period)
            reports.append(report)
        except Exception as e:
            print(f"Error processing officer {row.get('name_self', '[unknown]')}: {e}")
    return reports
