import pandas as pd

RATING_QUESTIONS = [
    "My LAB case officers made sufficient efforts to understand my situation and needs",
    "I got enough help from my LAB case officers to resolve my problem or deal with my situation",
    "I am satisfied with what LAB has done to help me",
    "The LAB officers handling my case were respectful and professional",
    "I knew what I could do if I could not pay the legal fees",
    "I was able to communicate easily with the LAB officers handling my case",
    "I am overall satisfied with LAB’s services"
]

def compute_officer_stats(officer, caseload_df, ratings_df, period, all_caseload_df):
    name = officer['Name']
    abbreviation = officer['Abbreviation']
    start_date, end_date = period['date_start'], period['date_end']

    # Normalize officer name and filter
    case_df = caseload_df[caseload_df['Name'].str.strip().str.lower() == name.strip().lower()]
    ratings_df = ratings_df[ratings_df['Name'].str.strip().str.lower() == name.strip().lower()]

    # Column map for the period
    colmap = {
        "inhouse_opening": f"In-house Caseload as at {start_date}",
        "inhouse_additional": f"Additional In-house Cases Between {start_date} to {end_date}",
        "inhouse_nfa_07_12": f"In-house Cases NFA- 07 and NFA-12 Between {start_date} to {end_date}",
        "inhouse_nfa_others": f"In-house Cases NFA- others Between {start_date} to {end_date}",
        "inhouse_ending": f"In-house Caseload as at {end_date}",
        "assigned_opening": f"Assigned Caseload as at {start_date}",
        "assigned_additional": f"Additional Assigned Cases Between {start_date} to {end_date}",
        "assigned_nfa_07_12": f"Assigned Cases NFA- 07 Between {start_date} to {end_date}",
        "assigned_nfa_others": f"Assigned Cases NFA- others Between {start_date} to {end_date}",
        "assigned_ending": f"Assigned Caseload as at {end_date}",
    }

    stats = {key: int(case_df[colmap[key]].values[0]) if colmap[key] in case_df.columns else 0 for key in colmap}

    # Compute averages across all officers
    averages = {}
    for key, col in colmap.items():
        if col in all_caseload_df.columns:
            averages[f"avg_{key}"] = round(all_caseload_df[col].mean(), 2)
        else:
            averages[f"avg_{key}"] = "N/A"

    # Ratings: overall satisfaction
    overall_col = "I am overall satisfied with LAB’s services"
    if overall_col in ratings_df.columns:
        overall_satisfaction = round(ratings_df[overall_col].mean(), 2)
    else:
        overall_satisfaction = "N/A"

    # Ratings by case
    ratings_inhouse = []
    ratings_assigned = []
    for _, row in ratings_df.iterrows():
        if pd.isna(row["CASE REF NO"]) or pd.isna(row["APPLICANT"]):
            continue
        scores = [row[q] for q in RATING_QUESTIONS if q in row and pd.notna(row[q])]
        if scores:
            entry = {
                "case_ref": row["CASE REF NO"],
                "applicant": row["APPLICANT"],
                "avg_score": round(sum(scores) / len(scores), 2)
            }
            if row.get("ASSIGNED OUT INDICATOR") == "Y":
                ratings_assigned.append(entry)
            else:
                ratings_inhouse.append(entry)

    return {
        "name": name,
        "abbreviation": abbreviation,
        "period": period,
        **stats,
        **averages,
        "avg_overall_satisfaction": overall_satisfaction,
        "ratings_inhouse": ratings_inhouse,
        "ratings_assigned": ratings_assigned
    }

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    return [
        compute_officer_stats(row, caseload_df, ratings_df, period, caseload_df)
        for _, row in namelist_df.iterrows()
    ]
