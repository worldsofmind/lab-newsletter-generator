import pandas as pd

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['Name']
    abbreviation = officer['Abbreviation']
    start_date, end_date = period['date_start'], period['date_end']

    # Filter by period is skipped since the dates are from caseload columns, not individual row dates
    case_df = caseload_df.copy()
    case_df = case_df[case_df['Name'].str.strip().str.lower() == name.strip().lower()]

    inhouse_cases = case_df[case_df['Case Type'].str.contains('In-house', case=False, na=False)].shape[0]
    assigned_cases = case_df[case_df['Case Type'].str.contains('Assigned', case=False, na=False)].shape[0]

    ratings_filtered = ratings_df[ratings_df['Name'].str.strip().str.lower() == name.strip().lower()]
    avg_rating = ratings_filtered['I am overall satisfied with LAB’s services'].mean() if not ratings_filtered.empty else None

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
