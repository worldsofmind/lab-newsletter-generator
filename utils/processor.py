
import pandas as pd
from collections import defaultdict

SURVEY_QUESTIONS = 
[
    "My LAB case officers made sufficient efforts to help me understand what was happening in my case",
    "I got enough help from my LAB case officers when I needed to give them documents and information for my case",
    "I am satisfied with what LAB has done to move my case along",
    "The LAB officers handling my case were respectful and understanding",
    "I knew what I could do if I could not pay LAB’s fees for the work done on my case (contribution)",
    "I was able to communicate easily with the LAB officers handling my case",
    "I am overall satisfied with LAB’s services"
]


def compute_officer_stats(officer_row, case_load_df, ratings_df, period, all_caseload_df):
    officer_name = officer_row["Name"].strip().lower()
    stats = defaultdict(lambda: "N/A")

    def _get_value(df_row, col):
        return pd.to_numeric(df_row.get(col, 0), errors="coerce")

    case_row = case_load_df[case_load_df["Name"].str.strip().str.lower() == officer_name]
    case_row = case_row.iloc[0] if not case_row.empty else pd.Series(dtype=object)

    def get_stat(col_pattern):
        col_name = col_pattern.format(**period)
        return _get_value(case_row, col_name) if col_name in case_row else 0

    stats["inhouse_opening"] = get_stat("In-house Caseload as at {date_start}")
    stats["inhouse_end"] = get_stat("In-house Caseload as at {date_end}")
    stats["inhouse_added"] = get_stat("Additional In-house Cases Between {date_start} to {date_end}")
    stats["inhouse_nfa"] = get_stat("NFA In-house Cases Between {date_start} to {date_end}")
    stats["inhouse_removed"] = get_stat("Total Removed In-house Cases Between {date_start} to {date_end}")
    stats["inhouse_reassigned"] = max(stats["inhouse_removed"] - stats["inhouse_nfa"], 0)

    stats["assigned_opening"] = get_stat("Assigned Caseload as at {date_start}")
    stats["assigned_end"] = get_stat("Assigned Caseload as at {date_end}")
    stats["assigned_added"] = get_stat("Additional Assigned Cases Between {date_start} to {date_end}")
    stats["assigned_nfa"] = get_stat("NFA Assigned Cases Between {date_start} to {date_end}")
    stats["assigned_removed"] = get_stat("Total Removed Assigned Cases Between {date_start} to {date_end}")
    stats["assigned_reassigned"] = max(stats["assigned_removed"] - stats["assigned_nfa"], 0)

    def avg(col_name):
        values = pd.to_numeric(all_caseload_df[col_name], errors="coerce").dropna()
        return round(values.mean(), 1) if not values.empty else "N/A"

    avg_map = {
        "avg_inhouse_opening": "In-house Caseload as at {date_start}",
        "avg_inhouse_end": "In-house Caseload as at {date_end}",
        "avg_assigned_opening": "Assigned Caseload as at {date_start}",
        "avg_assigned_end": "Assigned Caseload as at {date_end}",
        "avg_inhouse_added": "Additional In-house Cases Between {date_start} to {date_end}",
        "avg_inhouse_nfa": "NFA In-house Cases Between {date_start} to {date_end}",
        "avg_assigned_added": "Additional Assigned Cases Between {date_start} to {date_end}",
        "avg_assigned_nfa": "NFA Assigned Cases Between {date_start} to {date_end}"
    }

    for key, col in avg_map.items():
        col_name = col.format(**period)
        stats[key] = avg(col_name) if col_name in all_caseload_df.columns else "N/A"

    ratings_df.columns = ratings_df.columns.str.strip().str.lower()
    ratings_df["name"] = ratings_df["name"].astype(str).str.strip().str.lower()
    ratings_df["assigned out indicator"] = ratings_df["assigned out indicator"].astype(str).str.lower().str.strip()
    matched_ratings = ratings_df[ratings_df["name"] == officer_name]

    q_cols = [q.lower() for q in SURVEY_QUESTIONS]
    survey_cols = [col for col in ratings_df.columns if col in q_cols]
    display_q_map = {q.lower(): q for q in SURVEY_QUESTIONS}

    if not matched_ratings.empty and survey_cols:
        survey = matched_ratings[survey_cols]
        stats["survey_ratings"] = {
            display_q_map[col]: round(survey[col].mean(), 1)
            for col in survey.columns if pd.api.types.is_numeric_dtype(survey[col])
        }
    else:
        stats["survey_ratings"] = {}

    def case_ratings(assigned_statuses):
        filtered = matched_ratings[
            matched_ratings["assigned out indicator"].isin(assigned_statuses)
        ]
        if filtered.empty:
            return []
        score_cols = [col for col in filtered.columns if col in q_cols]
        filtered = filtered.copy()
        filtered["score"] = filtered[score_cols].mean(axis=1)
        return [
            {
                "case_ref": row.get("case ref no", "NA"),
                "applicant": row.get("applicant", "NA"),
                "score": round(row["score"], 1)
            }
            for _, row in filtered.iterrows()
            if pd.notnull(row.get("case ref no")) and pd.notnull(row.get("applicant"))
        ]

    stats["inhouse_case_ratings"] = case_ratings(["no", "n"])
    stats["assigned_case_ratings"] = case_ratings(["yes", "y"])

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
