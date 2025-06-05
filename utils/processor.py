
import pandas as pd
import numpy as np
from datetime import datetime

def compute_officer_stats(abbreviation, case_df, ratings_df, namelist_df):
    officer_row = namelist_df[namelist_df["Abbreviation"] == abbreviation].iloc[0]
    officer_name = officer_row["Name"]
    officer_function = officer_row["self_type"]

    # Get all LO or LE for calculating LO Avg or LE Avg
    peer_group = namelist_df[namelist_df["self_type"] == officer_function]["Abbreviation"].tolist()

    # Preprocess column dates
    start_col = [col for col in case_df.columns if "as at" in col.lower()][0]
    end_col = [col for col in case_df.columns if "as at" in col.lower()][-1]

    # Filter by officer
    officer_cases = case_df[case_df["Abbreviation"] == abbreviation]
    peers_cases = case_df[case_df["Abbreviation"].isin(peer_group)]

    # Compute stats
    def safe_mean(series): return round(series.mean(), 1) if not series.empty else "N/A"
    def safe_sum(series): return int(series.sum()) if not series.empty else 0

    def stat(colname): return safe_sum(officer_cases[colname])
    def avg_stat(colname): return safe_mean(peers_cases[colname])

    def stat_sum_from_cols(cols): return sum(safe_sum(officer_cases[c]) for c in cols)
    def avg_sum_from_cols(cols): return safe_mean(peers_cases[cols].sum(axis=1))

    # Assemble dictionary
    stats = {
        "name": officer_name,
        "abbreviation": abbreviation,
        "function": officer_function,
        "period": {
            "date_start": pd.to_datetime(start_col.split("as at")[-1].strip(), dayfirst=True).strftime("%d %b %Y"),
            "date_end": pd.to_datetime(end_col.split("as at")[-1].strip(), dayfirst=True).strftime("%d %b %Y"),
            "date_start_verbose": pd.to_datetime(start_col.split("as at")[-1].strip(), dayfirst=True).strftime("%d %B %Y"),
            "date_end_verbose": pd.to_datetime(end_col.split("as at")[-1].strip(), dayfirst=True).strftime("%d %B %Y"),
            "month_start": "MAY",
            "month_end": "AUG",
        },
        # Section 1
        "inhouse_opening": stat(start_col + " - In-house"),
        "assigned_opening": stat(start_col + " - Assigned"),
        "avg_inhouse_opening": avg_stat(start_col + " - In-house"),
        "avg_assigned_opening": avg_stat(start_col + " - Assigned"),

        # Section 2
        "inhouse_added": stat("New In-house"),
        "assigned_added": stat("New Assigned"),
        "avg_inhouse_added": avg_stat("New In-house"),
        "avg_assigned_added": avg_stat("New Assigned"),

        "inhouse_nfa_712": stat_sum_from_cols(["NFA7 In-house", "NFA12 In-house"]),
        "inhouse_nfa_others": stat("NFA Other In-house"),
        "assigned_nfa_712": stat_sum_from_cols(["NFA7 Assigned", "NFA12 Assigned"]),
        "assigned_nfa_others": stat("NFA Other Assigned"),

        "avg_inhouse_nfa_712": avg_sum_from_cols(["NFA7 In-house", "NFA12 In-house"]),
        "avg_inhouse_nfa_others": avg_stat("NFA Other In-house"),
        "avg_assigned_nfa_712": avg_sum_from_cols(["NFA7 Assigned", "NFA12 Assigned"]),
        "avg_assigned_nfa_others": avg_stat("NFA Other Assigned"),

        "inhouse_reassigned": stat("Reassigned In-house"),
        "assigned_reassigned": stat("Reassigned Assigned"),
        "avg_inhouse_reassigned": avg_stat("Reassigned In-house"),
        "avg_assigned_reassigned": avg_stat("Reassigned Assigned"),

        # Section 3
        "inhouse_end": stat(end_col + " - In-house"),
        "assigned_end": stat(end_col + " - Assigned"),
        "avg_inhouse_end": avg_stat(end_col + " - In-house"),
        "avg_assigned_end": avg_stat(end_col + " - Assigned"),
    }

    # Ratings - fallback to blank if officer not found
    survey_df = ratings_df[ratings_df["Abbreviation"] == abbreviation]
    survey_ratings = {}
    if not survey_df.empty:
        for col in survey_df.columns:
            if col not in ["Abbreviation", "Role"]:
                val = survey_df[col].values[0]
                if pd.notnull(val):
                    survey_ratings[col] = round(val, 1)
    stats["survey_ratings"] = survey_ratings

    # Case Ratings - dummy example until structure confirmed
    stats["inhouse_case_ratings"] = []
    stats["assigned_case_ratings"] = []

    return stats
