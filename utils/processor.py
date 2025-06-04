
import pandas as pd
import difflib

def filter_period(df, start, end):
    # Try to find the column most similar to 'Date Assigned to Current Officer'
    possible_cols = df.columns.tolist()
    date_col = difflib.get_close_matches('Date Assigned to Current Officer', possible_cols, n=1, cutoff=0.5)
    if not date_col:
        raise KeyError("Could not find a column similar to 'Date Assigned to Current Officer'")
    date_col = date_col[0]
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    mask = (df[date_col] >= pd.to_datetime(start)) & (df[date_col] <= pd.to_datetime(end))
    return df[mask]

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['name_self']
    abbreviation = name.split()[-1].strip("()")  # fallback for display
    start_date, end_date = period['date_start'], period['date_end']

    case_df = filter_period(caseload_df.copy(), start_date, end_date)
    case_df = case_df[case_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]

    inhouse_cases = case_df[case_df['Case Type'].str.contains('In-house', case=False, na=False)]
    assigned_cases = case_df[case_df['Case Type'].str.contains('Assigned', case=False, na=False)]

    officer_ratings = ratings_df[ratings_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]
    avg_rating = officer_ratings['Overall rating'].mean() if not officer_ratings.empty else None

    return {
        'name': name,
        'abbreviation': abbreviation,
        'inhouse_count': len(inhouse_cases),
        'assigned_count': len(assigned_cases),
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
