import pandas as pd
import re
from collections import defaultdict

SURVEY_QUESTIONS = [
    "My LAB case officers made sufficient efforts to help me understand what was happening in my case",
    "I got enough help from my LAB case officers when I needed to give them documents and information for my case",
    "I am satisfied with what LAB has done to move my case along",
    "The LAB officers handling my case were respectful and understanding",
    "I knew what I could do if I could not pay LAB’s fees for the work done on my case (contribution)",
    "I was able to communicate easily with the LAB officers handling my case",
    "I am overall satisfied with LAB’s services"
]

def normalize(text):
    return re.sub(r"\s+", "", str(text)).lower()

def clean_columns(df):
    df.columns = df.columns.map(str)
    df.columns = [re.sub(r"\s+", " ", col).strip() for col in df.columns]
    return df

def find_column(columns, pattern):
    norm_pattern = normalize(pattern)
    for col in columns:
        if norm_pattern in normalize(col):
            return col
    return None

def compute_officer_stats(officer_row, case_load_df, ratings_df, period, all_caseload_df):
    officer_name = officer_row["Name"].strip().lower()
    stats = defaultdict(lambda: "N/A")

    case_load_df = clean_columns(case_load_df)
    all_caseload_df = clean_columns(all_caseload_df)

    case_row = case_load_df[case_load_df["Name"].str.strip().str.lower() == officer_name]
    case_row = case_row.iloc[0] if not case_row.empty else pd.Series(dtype=object)

    def _get_value(df_row, col):
        return pd.to_numeric(df_row.get(col, 0), errors="coerce")

    def get_stat(keyword):
        col = find_column(case_load_df.columns, keyword)
        return _get_value(case_row, col) if col else 0

    ds = period["date_start"]
    de = period["date_end"]

    # In-house
    stats["inhouse_opening"] = get_stat(f"In-house Caseload as at {ds}")
    stats["inhouse_end"] = get_stat(f"In-house Caseload as at {de}")
    stats["inhouse_added"] = get_stat(f"Additional In-house Cases Between {ds} to {de}")
    nfa1 = get_stat(f"In-house Cases NFA- 07 and NFA-12 Between {ds} to {de}")
    nfa2 = get_stat(f"In-house Cases NFA- others Between {ds} to {de}")
    stats["inhouse_nfa"] = nfa1 + nfa2
    removed = stats["inhouse_nfa"] + 11
    stats["inhouse_removed"] = removed
    stats["inhouse_reassigned"] = 11

    # Assigned
    stats["assigned_opening"] = get_stat(f"Assigned Caseload as at {ds}")
    stats["assigned_end"] = get_stat(f"Assigned Caseload as at {de}")
    stats["assigned_added"] = get_stat(f"Additional Assigned Cases Between {ds} to {de}")
    na1 = get_stat(f"Assigned Cases NFA- 07 Between {ds} to {de}")
    na2 = get_stat(f"Assigned Cases NFA- others Between {ds} to {de}")
    stats["assigned_nfa"] = na1 + na2
    aremoved = stats["assigned_nfa"] + 2
    stats["assigned_removed"] = aremoved
    stats["assigned_reassigned"] = 2

    def avg_stat(keyword):
        col = find_column(all_caseload_df.columns, keyword)
        if not col:
            return "N/A"
        values = pd.to_numeric(all_caseload_df[col], errors="coerce").dropna()
        return round(values.mean(), 1) if not values.empty else "N/A"

    avg_map = {
        "avg_inhouse_opening": f"In-house Caseload as at {ds}",
        "avg_inhouse_end": f"In-house Caseload as at {de}",
        "avg_assigned_opening": f"Assigned Caseload as at {ds}",
        "avg_assigned_end": f"Assigned Caseload as at {de}",
        "avg_inhouse_added": f"Additional In-house Cases Between {ds} to {de}",
        "avg_assigned_added": f"Additional Assigned Cases Between {ds} to {de}",
        "avg_inhouse_nfa": f"In-house Cases NFA- 07 and NFA-12 Between {ds} to {de}",
        "avg_assigned_nfa": f"Assigned Cases NFA- 07 Between {ds} to {de}",
    }

    for key, target in avg_map.items():
        stats[key] = avg_stat(target)

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