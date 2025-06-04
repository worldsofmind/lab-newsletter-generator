import pandas as pd

def compute_officer_stats(officer, caseload_df, ratings_df, period):
    name = officer['name_self']
    abbreviation = name.split()[-1].strip("()")

    # Match row by officer name
    officer_row = caseload_df[caseload_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]
    if officer_row.empty:
        return {
            'name': name,
            'abbreviation': abbreviation,
            'inhouse_count': 0,
            'assigned_count': 0,
            'avg_rating': 'N/A'
        }

    inhouse_cases = officer_row.filter(like='In-house', axis=1).sum(axis=1).sum()
    assigned_cases = officer_row.filter(like='Assigned', axis=1).sum(axis=1).sum()

    rating_row = ratings_df[ratings_df['LO/LE'].str.strip().str.lower() == name.strip().lower()]
    avg_rating = rating_row['Overall rating'].mean() if not rating_row.empty else None

    return {
        'name': name,
        'abbreviation': abbreviation,
        'inhouse_count': int(inhouse_cases),
        'assigned_count': int(assigned_cases),
        'avg_rating': round(avg_rating, 2) if avg_rating else 'N/A'
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    reports = []
    for _, row in namelist_df.iterrows():
        try:
            reports.append(compute_officer_stats(row, caseload_df, ratings_df, period))
        except Exception as e:
            print(f"Error processing officer {row['name_self']}: {e}")
    return reports
