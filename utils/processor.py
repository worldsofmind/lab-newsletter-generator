
import pandas as pd
from collections import defaultdict

def compute_officer_stats(row, caseload_df, ratings_df, period, all_caseload_df):
    name = row["Name"]
    abbreviation = row["Abbreviation"]
    function = row["self_type"]

    officer_data = caseload_df[caseload_df["Name"].str.strip() == name]

    stats = {
        "name": name,
        "abbreviation": abbreviation,
        "function": function,
        "period": period,
        "inhouse_opening": _get_value(officer_data, "In-house Caseload as at 08/05/2024"),
        "inhouse_added": _get_value(officer_data, "Additional In-house Cases Between 08/05/2024 to 02/08/2024"),
        "inhouse_nfa": (
            _get_value(officer_data, "In-house Cases NFA- 07 and NFA-12 Between 08/05/2024 to 02/08/2024")
            + _get_value(officer_data, "In-house Cases NFA- others Between 08/05/2024 to 02/08/2024")
        ),
        "inhouse_closed": "N/A",  # no closed column provided
        "inhouse_end": _get_value(officer_data, "In-house Caseload as at 02/08/2024"),

        "assigned_opening": _get_value(officer_data, "Assigned Caseload as at 08/05/202 4"),
        "assigned_added": _get_value(officer_data, "Additional Assigned Cases Between 08/05/2024 to 02/08/2024"),
        "assigned_nfa": (
            _get_value(officer_data, "Assigned Cases NFA- 07 Between 08/05/2024 to 02/08/2024")
            + _get_value(officer_data, "Assigned Cases NFA- others Between 08/05/2024 to 02/08/2024")
        ),
        "assigned_closed": "N/A",  # no closed column provided
        "assigned_end": _get_value(officer_data, "Assigned Caseload as at 02/08/2024"),
    }

    # Averages
    stats.update({
        "avg_inhouse_opening": round(all_caseload_df["In-house Caseload as at 08/05/2024"].mean(), 1),
        "avg_inhouse_added": round(all_caseload_df["Additional In-house Cases Between 08/05/2024 to 02/08/2024"].mean(), 1),
        "avg_inhouse_closed": "N/A",
        "avg_inhouse_end": round(all_caseload_df["In-house Caseload as at 02/08/2024"].mean(), 1),
        "avg_assigned_opening": round(all_caseload_df["Assigned Caseload as at 08/05/202 4"].mean(), 1),
        "avg_assigned_added": round(all_caseload_df["Additional Assigned Cases Between 08/05/2024 to 02/08/2024"].mean(), 1),
        "avg_assigned_closed": "N/A",
        "avg_assigned_end": round(all_caseload_df["Assigned Caseload as at 02/08/2024"].mean(), 1),
    })

    # Survey Ratings
    questions = [col for col in ratings_df.columns if "LAB" in col and "Indicator" not in col]
    survey = ratings_df[ratings_df["LO"] == abbreviation]
    if not survey.empty:
        survey_scores = {
            q: round(survey[q].dropna().astype(float).mean(), 1)
            for q in questions
        }
    else:
        survey_scores = {}

    stats["survey_ratings"] = survey_scores

    # Case Ratings
    def extract_case_ratings(df, assigned):
        filtered = df[(df["LO"] == abbreviation) & (df["ASSIGNED OUT INDICATOR"] == assigned)]
        ratings = []
        for _, r in filtered.iterrows():
            scores = [r[q] for q in questions if pd.notna(r[q])]
            if scores:
                ratings.append({
                    "case_ref": r["CASE REF NO"],
                    "applicant": r["NAME"],
                    "score": round(pd.Series(scores).astype(float).mean(), 1)
                })
        return ratings

    stats["inhouse_case_ratings"] = extract_case_ratings(ratings_df, "N")
    stats["assigned_case_ratings"] = extract_case_ratings(ratings_df, "Y")

    return stats

def _get_value(df, col, default=0):
    try:
        val = df[col].values[0]
        return int(val) if not pd.isna(val) else default
    except Exception:
        return default
