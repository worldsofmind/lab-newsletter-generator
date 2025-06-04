# lab_newsletter_generator/utils/processor.py

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

    inhouse_stats = {
        'opening': len(inhouse_cases),
        'new': len(inhouse_cases),
        'completed': len(inhouse_cases[inhouse_cases['Outcome'].str.contains('NFA', na=False)]),
        'closed': len(inhouse_cases[inhouse_cases['Outcome'].str.contains('Close', na=False)]),
        'reassigned': len(inhouse_cases[inhouse_cases['Outcome'].str.contains('Reassigned', na=False)]),
        'ending': len(inhouse_cases)
    }

    assigned_stats = {
        'opening': len(assigned_cases),
        'new': len(assigned_cases),
        'completed': len(assigned_cases[assigned_cases['Outcome'].str.contains('NFA', na=False)]),
        'closed': len(assigned_cases[assigned_cases['Outcome'].str.contains('Close', na=False)]),
        'reassigned': len(assigned_cases[assigned_cases['Outcome'].str.contains('Reassigned', na=False)]),
        'ending': len(assigned_cases)
    }

    ratings_filtered = ratings_df[ratings_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]
    survey_questions = [col for col in ratings_filtered.columns if col.startswith('Q') or 'Respect' in col or 'Knowledge' in col]
    ratings_summary = ratings_filtered[survey_questions].mean().round(2).to_dict()

    return {
        'officer_name': name,
        'inhouse_stats': inhouse_stats,
        'assigned_stats': assigned_stats,
        'ratings_summary': ratings_summary,
        'raw_ratings': ratings_filtered
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    reports = []
    for _, row in namelist_df.iterrows():
        report = compute_officer_stats(row, caseload_df, ratings_df, period)
        reports.append(report)
    return reports