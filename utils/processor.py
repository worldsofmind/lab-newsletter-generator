
import pandas as pd
import numpy as np

def clean_column_names(df):
    df.columns = df.columns.str.replace("\n", " ", regex=True).str.strip()
    return df

def extract_case_stats(row, caseload_df, period, all_caseload_df):
    start, end = period["date_start"], period["date_end"]
    caseload_df = clean_column_names(caseload_df)

    name = row["Name"]
    abbreviation = row["Abbreviation"]

    def safe_get(col):
        return caseload_df.loc[caseload_df["Name"] == name, col].values[0] if col in caseload_df.columns else "N/A"

    stats = {
        "name": name,
        "abbreviation": abbreviation,
        "inhouse_opening": safe_get(f"In-house Caseload as at {start}"),
        "inhouse_added": safe_get(f"In-house Caseload Added Between {start} to {end}"),
        "inhouse_nfa": safe_get(f"In-house NFA Between {start} to {end}"),
        "inhouse_closed": safe_get(f"In-house Closed Between {start} to {end}"),
        "inhouse_end": safe_get(f"In-house Caseload as at {end}"),
        "assigned_opening": safe_get(f"Assigned Caseload as at {start}"),
        "assigned_added": safe_get(f"Assigned Caseload Added Between {start} to {end}"),
        "assigned_nfa": safe_get(f"Assigned NFA Between {start} to {end}"),
        "assigned_closed": safe_get(f"Assigned Closed Between {start} to {end}"),
        "assigned_end": safe_get(f"Assigned Caseload as at {end}"),
        "avg_inhouse_opening": safe_get("Average In-house Caseload as at Start"),
        "avg_inhouse_added": safe_get("Average In-house Caseload Added"),
        "avg_inhouse_closed": safe_get("Average In-house Caseload Closed"),
        "avg_inhouse_end": safe_get("Average In-house Caseload as at End"),
        "avg_assigned_opening": safe_get("Average Assigned Caseload as at Start"),
        "avg_assigned_added": safe_get("Average Assigned Caseload Added"),
        "avg_assigned_closed": safe_get("Average Assigned Caseload Closed"),
        "avg_assigned_end": safe_get("Average Assigned Caseload as at End"),
    }
    return stats

def extract_ratings(row, ratings_df):
    name = row["Name"]
    relevant = ratings_df[ratings_df["Name"] == name]

    survey_questions = [
        "I am overall satisfied with LAB’s services",
        "My lawyer understood my concerns and responded appropriately",
        "The advice and information provided were helpful",
        "The process was explained clearly to me",
        "I felt respected and listened to",
        "The services provided met my expectations",
        "I would recommend LAB’s services to others"
    ]

    survey_scores = {}
    for q in survey_questions:
        if q in relevant.columns:
            scores = pd.to_numeric(relevant[q], errors='coerce').dropna()
            if not scores.empty:
                survey_scores[q] = round(scores.mean(), 1)

    has_survey = len(survey_scores) > 0

    def extract_case_ratings(indicator_value):
        cases = relevant[relevant["ASSIGNED OUT INDICATOR"] == indicator_value]
        ratings = []
        for _, row in cases.iterrows():
            row_scores = [pd.to_numeric(row[q], errors='coerce') for q in survey_questions if q in row and pd.notna(row[q])]
            if row_scores:
                avg = round(np.nanmean(row_scores), 1)
                ratings.append({
                    "case_ref": row.get("CASE REF NO", "N/A"),
                    "applicant": row.get("APPLICANT", "N/A"),
                    "score": avg
                })
        return ratings

    inhouse_ratings = extract_case_ratings("N") + extract_case_ratings("") + extract_case_ratings(np.nan)
    assigned_ratings = extract_case_ratings("Y")

    return survey_scores if has_survey else None, inhouse_ratings, assigned_ratings

def compute_officer_stats(row, caseload_df, ratings_df, period, all_caseload_df):
    stats = extract_case_stats(row, caseload_df, period, all_caseload_df)
    survey, inhouse, assigned = extract_ratings(row, ratings_df)

    stats["survey_ratings"] = survey or []
    stats["inhouse_case_ratings"] = inhouse
    stats["assigned_case_ratings"] = assigned
    return stats

def process_all_officers(ratings_df, caseload_df, namelist_df, period):
    return [
        compute_officer_stats(row, caseload_df, ratings_df, period, caseload_df)
        for _, row in namelist_df.iterrows()
    ]
