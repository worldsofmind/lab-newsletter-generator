
import pandas as pd
import difflib

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['name_self']
    case_df = caseload_df.copy()
    case_df = case_df[case_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]

    # Defensive 'Case Type' detection (not always needed for aggregated data)
    case_type_col = next((col for col in case_df.columns if 'case type' in col.lower()), None)
    if case_type_col:
        inhouse_cases = case_df[case_df[case_type_col].str.contains('In-house', case=False, na=False)]
        assigned_cases = case_df[case_df[case_type_col].str.contains('Assigned', case=False, na=False)]
    else:
        inhouse_cases = case_df.filter(like='In-house', axis=1).sum(axis=1)
        assigned_cases = case_df.filter(like='Assigned', axis=1).sum(axis=1)

    officer_ratings = ratings_df[(ratings_df['LO'].str.strip().str.lower() == name.strip().lower()) |
                                 (ratings_df['LE'].str.strip().str.lower() == name.strip().lower())]

    avg_rating = officer_ratings['Overall Rating'].mean() if not officer_ratings.empty else None

    return {
        'name': officer['name_full'],
        'inhouse_cases': int(inhouse_cases.sum()) if isinstance(inhouse_cases, pd.Series) else len(inhouse_cases),
        'assigned_cases': int(assigned_cases.sum()) if isinstance(assigned_cases, pd.Series) else len(assigned_cases),
        'avg_rating': round(avg_rating, 2) if avg_rating is not None else 'N/A'
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    reports = []
    for _, row in namelist_df.iterrows():
        report = compute_officer_stats(row, caseload_df, ratings_df, period)
        reports.append(report)
    return reports
