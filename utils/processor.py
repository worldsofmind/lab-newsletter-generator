
import pandas as pd

def compute_officer_stats(officer_row, case_load_df, ratings_df, period):
    officer_name = officer_row["name"]
    abbreviation = officer_row["abbreviation"]
    function = officer_row["function"]

    # Filter relevant caseload
    case_data = case_load_df[case_load_df["name"] == officer_name]

    # Dates
    date_start = pd.to_datetime(period["date_start"])
    date_end = pd.to_datetime(period["date_end"])

    # Filter for average calculation within officer function group
    group_df = case_load_df[case_load_df["function"] == function]
    group_means = group_df.mean(numeric_only=True)

    def safe_get_mean(col):
        return round(group_means.get(col, 0), 1)

    def safe_get_value(row, col):
        return int(row[col]) if col in row and pd.notna(row[col]) else 0

    stats = {
        "name": officer_name,
        "abbreviation": abbreviation,
        "function": function,
        "period": {
            "date_start": period["date_start"],
            "date_end": period["date_end"],
            "date_start_verbose": period.get("date_start_verbose", ""),
            "date_end_verbose": period.get("date_end_verbose", ""),
            "month_start": period.get("month_start", ""),
            "month_end": period.get("month_end", "")
        }
    }

    # OPENING
    stats["inhouse_opening"] = safe_get_value(case_data.iloc[0], "inhouse_opening")
    stats["avg_inhouse_opening"] = safe_get_mean("inhouse_opening")
    stats["assigned_opening"] = safe_get_value(case_data.iloc[0], "assigned_opening")
    stats["avg_assigned_opening"] = safe_get_mean("assigned_opening")

    # IN-PERIOD
    for col in ["inhouse_added", "inhouse_nfa_712", "inhouse_nfa_others",
                "assigned_added", "assigned_nfa_712", "assigned_nfa_others"]:
        stats[col] = safe_get_value(case_data.iloc[0], col)
        stats["avg_" + col] = safe_get_mean(col)

    # REASSIGNED calculations
    stats["inhouse_end"] = safe_get_value(case_data.iloc[0], "inhouse_end")
    stats["assigned_end"] = safe_get_value(case_data.iloc[0], "assigned_end")

    stats["inhouse_reassigned"] = (
        stats["inhouse_opening"] + stats["inhouse_added"]
        - stats["inhouse_nfa_712"] - stats["inhouse_nfa_others"]
        - stats["inhouse_end"]
    )
    stats["avg_inhouse_reassigned"] = "N/A"

    stats["assigned_reassigned"] = (
        stats["assigned_opening"] + stats["assigned_added"]
        - stats["assigned_nfa_712"] - stats["assigned_nfa_others"]
        - stats["assigned_end"]
    )
    stats["avg_assigned_reassigned"] = "N/A"

    # ENDING
    stats["avg_inhouse_end"] = safe_get_mean("inhouse_end")
    stats["avg_assigned_end"] = safe_get_mean("assigned_end")

    # Ratings – fallback if missing
    officer_ratings = ratings_df[ratings_df["LO"] == abbreviation]
    survey = {}
    if not officer_ratings.empty:
        rating_cols = [col for col in officer_ratings.columns if "Q" in col]
        for q in rating_cols:
            valid_scores = officer_ratings[q].dropna().astype(float)
            if not valid_scores.empty:
                survey[q] = round(valid_scores.mean(), 1)
    stats["survey_ratings"] = survey if survey else None

    # Case ratings (in-house & assigned)
    stats["inhouse_case_ratings"] = []
    stats["assigned_case_ratings"] = []

    for _, row in officer_ratings.iterrows():
        if row.get("Case Type") == "In-House":
            stats["inhouse_case_ratings"].append({
                "case_ref": row.get("Case Ref", ""),
                "applicant": row.get("Applicant", ""),
                "score": row.get("Avg", "")
            })
        elif row.get("Case Type") == "Assigned":
            stats["assigned_case_ratings"].append({
                "case_ref": row.get("Case Ref", ""),
                "applicant": row.get("Applicant", ""),
                "score": row.get("Avg", "")
            })

    return stats
