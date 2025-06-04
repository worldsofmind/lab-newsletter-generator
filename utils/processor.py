
import pandas as pd

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['name_self']
    abbreviation = name.split()[-1].strip("()")

    # Use entire caseload_df, no date filtering
    case_df = caseload_df.copy()
    case_df = case_df[case_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]

    inhouse_cases = case_df.filter(like='In-house', axis=1).sum(axis=1).sum()
    assigned_cases = case_df.filter(like='Assigned', axis=1).sum(axis=1).sum()

    officer_ratings = ratings_df[ratings_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]
    avg_rating = officer_ratings['Overall rating'].mean() if not officer_ratings.empty else None

    return {
        'name': name,
        'abbreviation': abbreviation,
        'inhouse_count': int(inhouse_cases),
        'assigned_count': int(assigned_cases),
        'avg_rating': round(avg_rating, 2) if avg_rating else 'N/A'
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period, selected_officer=None):
    reports = []
    if selected_officer:
        row = namelist_df[namelist_df['name_self'] == selected_officer].iloc[0]
        reports.append(compute_officer_stats(row, caseload_df, ratings_df, period))
    else:
        for _, row in namelist_df.iterrows():
            reports.append(compute_officer_stats(row, caseload_df, ratings_df, period))
    return reports
