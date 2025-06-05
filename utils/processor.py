
import pandas as pd
from datetime import datetime

def compute_officer_stats(officer_row, caseload_df, ratings_df, period, all_caseload_df):
    name = officer_row["name_self"]
    function = officer_row["function"]
    relevant_df = caseload_df[caseload_df["Name"] == name]

    if function not in ["LO", "LE"]:
        return None

    group_df = caseload_df[caseload_df["Function"] == function]

    def safe_mean(series):
        return round(series.dropna().astype(float).mean(), 1) if not series.dropna().empty else 0

    def count_nfa(df, reasons, start_date, end_date, case_type):
        mask = (
            df["Closure Reason"].astype(str).isin(reasons) &
            (df["Case Category"] == case_type) &
            pd.to_datetime(df["Closure Date"], errors='coerce').between(start_date, end_date)
        )
        return df[mask].shape[0]

    def count_nfa_other(df, exclude_reasons, start_date, end_date, case_type):
        mask = (
            ~df["Closure Reason"].astype(str).isin(exclude_reasons) &
            (df["Case Category"] == case_type) &
            pd.to_datetime(df["Closure Date"], errors='coerce').between(start_date, end_date)
        )
        return df[mask].shape[0]

    def count_reassigned(df, case_type, start_date, end_date):
        mask = (
            (df["Case Category"] == case_type) &
            (df["Reassigned"] == "Yes") &
            pd.to_datetime(df["Reassign Date"], errors='coerce').between(start_date, end_date)
        )
        return df[mask].shape[0]

    # Dynamic columns
    inhouse_open_col = f"In-house Caseload as at {period['date_start']}"
    assigned_open_col = f"Assigned Caseload as at {period['date_start']}"
    inhouse_end_col = f"In-house Caseload as at {period['date_end']}"
    assigned_end_col = f"Assigned Caseload as at {period['date_end']}"
    new_inhouse_col = "New In-house Cases (May to Aug)"
    new_assigned_col = "New Assigned Cases (May to Aug)"

    # Pull individual values
    def extract(col, default=0):
        return relevant_df[col].values[0] if col in relevant_df.columns and not relevant_df[col].empty else default

    officer_stats = {
        "name": name,
        "abbreviation": officer_row["name_abbrev"],
        "function": function,
        "period": {
            "date_start": period["date_start"],
            "date_end": period["date_end"],
            "date_start_verbose": period["date_start_verbose"],
            "date_end_verbose": period["date_end_verbose"],
            "month_start": period["month_start"],
            "month_end": period["month_end"]
        },
        # 🟦 Opening values
        "inhouse_opening": extract(inhouse_open_col),
        "assigned_opening": extract(assigned_open_col),
        # 🟨 In-period
        "inhouse_added": extract(new_inhouse_col),
        "assigned_added": extract(new_assigned_col),
        "inhouse_nfa_712": count_nfa(all_caseload_df, ["7", "12"], period["date_start_dt"], period["date_end_dt"], "In-house"),
        "inhouse_nfa_others": count_nfa_other(all_caseload_df, ["7", "12"], period["date_start_dt"], period["date_end_dt"], "In-house"),
        "inhouse_reassigned": count_reassigned(all_caseload_df, "In-house", period["date_start_dt"], period["date_end_dt"]),
        "assigned_nfa_712": count_nfa(all_caseload_df, ["7", "12"], period["date_start_dt"], period["date_end_dt"], "Assigned"),
        "assigned_nfa_others": count_nfa_other(all_caseload_df, ["7", "12"], period["date_start_dt"], period["date_end_dt"], "Assigned"),
        "assigned_reassigned": count_reassigned(all_caseload_df, "Assigned", period["date_start_dt"], period["date_end_dt"]),
        # 🟩 Ending values
        "inhouse_end": extract(inhouse_end_col),
        "assigned_end": extract(assigned_end_col),
        # Averages by function group
        "avg_inhouse_opening": safe_mean(group_df[inhouse_open_col]) if inhouse_open_col in group_df else 0,
        "avg_assigned_opening": safe_mean(group_df[assigned_open_col]) if assigned_open_col in group_df else 0,
        "avg_inhouse_added": safe_mean(group_df[new_inhouse_col]) if new_inhouse_col in group_df else 0,
        "avg_assigned_added": safe_mean(group_df[new_assigned_col]) if new_assigned_col in group_df else 0,
        "avg_inhouse_end": safe_mean(group_df[inhouse_end_col]) if inhouse_end_col in group_df else 0,
        "avg_assigned_end": safe_mean(group_df[assigned_end_col]) if assigned_end_col in group_df else 0,
        # Placeholder for other averages
        "avg_inhouse_nfa_712": 0,
        "avg_inhouse_nfa_others": 0,
        "avg_inhouse_reassigned": 0,
        "avg_assigned_nfa_712": 0,
        "avg_assigned_nfa_others": 0,
        "avg_assigned_reassigned": 0
    }

    return officer_stats
