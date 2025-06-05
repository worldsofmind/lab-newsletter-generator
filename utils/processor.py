
import pandas as pd
from collections import defaultdict

def compute_officer_stats(officer_row, case_load_df, ratings_df, period, all_caseload_df):
    officer_name = officer_row["name"]
    stats = defaultdict(lambda: "N/A")

    def _get_value(df_row, col):
        return pd.to_numeric(df_row.get(col, 0), errors="coerce")

    # Find matching row in case load
    case_row = case_load_df[case_load_df["Name"].str.strip().str.lower() == officer_name.strip().lower()]
    case_row = case_row.iloc[0] if not case_row.empty else pd.Series(dtype=object)

    def get_stat(col_pattern):
        col_name = col_pattern.format(**period)
        return _get_value(case_row, col_name) if col_name in case_row else 0

    # In-house stats
    stats["inhouse_opening"] = get_stat("In-house Caseload as at {date_start}")
    stats["inhouse_end"] = get_stat("In-house Caseload as at {date_end}")
    stats["inhouse_added"] = get_stat("Additional In-house Cases Between {date_start} to {date_end}")
    stats["inhouse_nfa"] = get_stat("NFA In-house Cases Between {date_start} to {date_end}")
    stats["inhouse_removed"] = get_stat("Total Removed In-house Cases Between {date_start} to {date_end}")
    stats["inhouse_reassigned"] = max(stats["inhouse_removed"] - stats["inhouse_nfa"], 0)

    # Assigned stats
    stats["assigned_opening"] = get_stat("Assigned Caseload as at {date_start}")
    stats["assigned_end"] = get_stat("Assigned Caseload as at {date_end}")
    stats["assigned_added"] = get_stat("Additional Assigned Cases Between {date_start} to {date_end}")
    stats["assigned_nfa"] = get_stat("NFA Assigned Cases Between {date_start} to {date_end}")
    stats["assigned_removed"] = get_stat("Total Removed Assigned Cases Between {date_start} to {date_end}")
    stats["assigned_reassigned"] = max(stats["assigned_removed"] - stats["assigned_nfa"], 0)

    # LO averages
    def avg(col_name):
        values = pd.to_numeric(all_caseload_df[col_name], errors="coerce").dropna()
        return round(values.mean(), 1) if not values.empty else "N/A"

    for key, col in {
        "avg_inhouse_opening": "In-house Caseload as at {date_start}",
        "avg_inhouse_end": "In-house Caseload as at {date_end}",
        "avg_assigned_opening": "Assigned Caseload as at {date_start}",
        "avg_assigned_end": "Assigned Caseload as at {date_end}",
        "avg_inhouse_added": "Additional In-house Cases Between {date_start} to {date_end}",
        "avg_inhouse_nfa": "NFA In-house Cases Between {date_start} to {date_end}",
        "avg_assigned_added": "Additional Assigned Cases Between {date_start} to {date_end}",
        "avg_assigned_nfa": "NFA Assigned Cases Between {date_start} to {date_end}"
    }.items():
        col_name = col.format(**period)
        stats[key] = avg(col_name) if col_name in all_caseload_df.columns else "N/A"

    # Ratings (7-question averages)
    ratings = ratings_df[ratings_df["name"].str.lower() == officer_name.lower()]
    survey = ratings[[col for col in ratings.columns if col.startswith("Q")]] if not ratings.empty else pd.DataFrame()

    if not survey.empty:
        stats["survey_ratings"] = {
            col: round(survey[col].mean(), 1) for col in survey.columns if pd.api.types.is_numeric_dtype(survey[col])
        }
    else:
        stats["survey_ratings"] = {}

    def case_ratings(prefix):
        rated = ratings[ratings["Type"].str.lower() == prefix] if "Type" in ratings.columns else pd.DataFrame()
        rated = rated.copy()
        rated["score"] = rated[[c for c in ratings.columns if c.startswith("Q")]].mean(axis=1)
        return [
            {"case_ref": row["CASE REF NO"], "applicant": row["Applicant"], "score": round(row["score"], 1)}
            for _, row in rated.iterrows()
            if pd.notnull(row.get("CASE REF NO")) and pd.notnull(row.get("Applicant"))
        ] if not rated.empty else []

    stats["inhouse_case_ratings"] = case_ratings("in-house")
    stats["assigned_case_ratings"] = case_ratings("assigned")

    stats["name"] = officer_name
    stats["abbreviation"] = officer_row.get("abbreviation", "")
    stats["function"] = officer_row.get("function", "")
    stats["period"] = period
    return stats

def process_all_officers(namelist_df, case_load_df, ratings_df, period):
    return [
        compute_officer_stats(row, case_load_df, ratings_df, period, case_load_df)
        for _, row in namelist_df.iterrows()
    ]
