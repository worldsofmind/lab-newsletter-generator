
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

    # Defensive lookup for 'Case Type'
    case_type_col = next((col for col in case_df.columns if 'case type' in col.lower()), None)
    if case_type_col:
        inhouse_cases = case_df[case_df[case_type_col].str.contains('In-house', case=False, na=False)]
        assigned_cases = case_df[case_df[case_type_col].str.contains('Assigned', case=False, na=False)]
    else:
        raise KeyError("Could not find a 'Case Type' column in case_df.")

    rating_row = ratings_df[(ratings_df['LO'].str.strip().str.lower() == name.strip().lower()) |
                            (ratings_df['LE'].str.strip().str.lower() == name.strip().lower())]

    rating_score = rating_row['Rating'].values[0] if not rating_row.empty else None

    return {
        "officer_name": officer['name_full'],
        "inhouse_cases": len(inhouse_cases),
        "assigned_cases": len(assigned_cases),
        "rating": rating_score
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    reports = []
    for _, row in namelist_df.iterrows():
        report = compute_officer_stats(row, caseload_df, ratings_df, period)
        reports.append(report)
    return reports
