
import pandas as pd
from collections import defaultdict

def compute_officer_stats(officer_row, case_load_df, ratings_df, period, all_caseload_df):
    officer_name = officer_row["Name"].strip().lower()
    stats = defaultdict(lambda: "N/A")

    def _get_value(df_row, col):
        return pd.to_numeric(df_row.get(col, 0), errors="coerce")

    # Match row from case_load
    case_row = case_load_df[case_load_df["Name"].str.strip().str.lower() == officer_name]
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

    # Averages
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

    # Survey Ratings
    ratings_df['LO'] = ratings_df['LO'].astype(str).str.strip().str.lower()
    ratings_df['LE'] = ratings_df['LE'].astype(str).str.strip().str.lower()
    ratings = ratings_df[
        (ratings_df["LO"] == officer_name) |
        (ratings_df["LE"] == officer_name)
    ]

    survey_cols = [col for col in ratings.columns if col.startswith("Q") or "satisfied" in col.lower()]
    if not ratings.empty:
        survey = ratings[survey_cols]
        stats["survey_ratings"] = {
            col.strip(): round(survey[col].mean(), 1)
            for col in survey.columns if pd.api.types.is_numeric_dtype(survey[col])
        }
    else:
        stats["survey_ratings"] = {}

    # Case ratings (in-house / assigned)
    def case_ratings(assigned):
        filtered = ratings[ratings["ASSIGNED OUT INDICATOR"].astype(str).str.strip().str.lower() == assigned]
        if filtered.empty:
            return []
        question_cols = [col for col in filtered.columns if col.startswith("Q") or "satisfied" in col.lower()]
        filtered = filtered.copy()
        filtered["score"] = filtered[question_cols].mean(axis=1)
        return [
            {
                "case_ref": row.get("CASE REF NO", "NA"),
                "applicant": row.get("NAME", "NA"),
                "score": round(row["score"], 1)
            }
            for _, row in filtered.iterrows()
            if pd.notnull(row.get("CASE REF NO")) and pd.notnull(row.get("NAME"))
        ]

    stats["inhouse_case_ratings"] = case_ratings("no")
    stats["assigned_case_ratings"] = case_ratings("yes")

    stats["name"] = officer_row["Name"]
    stats["abbreviation"] = officer_row.get("Abbreviation", "")
    stats["function"] = officer_row.get("self_type", "")
    stats["period"] = period
    return stats

def process_all_officers(namelist_df, case_load_df, ratings_df, period):
    return [
        compute_officer_stats(row, case_load_df, ratings_df, period, case_load_df)
        for _, row in namelist_df.iterrows()
    ]
