import pandas as pd
import numpy as np

def compute_officer_stats(officer_row, case_df, ratings_df):
    officer_name = officer_row['name']
    abbreviation = officer_row['abbreviation']
    function = officer_row['function']
    period = {
        "date_start": "08/05/2024",
        "date_end": "02/08/2024",
        "date_start_verbose": "8 May 2024",
        "date_end_verbose": "2 Aug 2024",
        "month_start": "May",
        "month_end": "Aug"
    }

    # Helper functions to safely extract and average values from case_df
    def safe_get(col_name):
        return (
            case_df.loc[case_df["name"].str.lower() == officer_name.lower(), col_name]
            .squeeze()
            if col_name in case_df.columns
            else 0
        )

    def safe_mean(col_name):
        if col_name in case_df.columns:
            val = case_df[col_name].mean()
            return round(val, 1)
        return "N/A"

    #
    # ── IN‐HOUSE STATISTICS ─────────────────────────────────────────────────────────
    #

    inhouse_opening    = safe_get(f"in-house caseload as at {period['date_start']}")
    inhouse_added      = safe_get(f"additional in-house cases between {period['date_start']} to {period['date_end']}")
    inhouse_nfa_712    = safe_get(f"in-house cases nfa- 07 and nfa-12 between {period['date_start']} to {period['date_end']}")
    inhouse_nfa_others = safe_get(f"in-house cases nfa- others between {period['date_start']} to {period['date_end']}")
    inhouse_end        = safe_get(f"in-house caseload as at {period['date_end']}")

    # ── REASSIGNED IN‐HOUSE (computed) ─────────────────────────────────────────────
    inhouse_completed   = inhouse_nfa_712 + inhouse_nfa_others
    inhouse_reassigned  = inhouse_end - ((inhouse_opening + inhouse_added) - inhouse_completed)

    # In‐house average (across all officers), rounded to one decimal
    avg_inhouse_opening = safe_mean(f"in-house caseload as at {period['date_start']}")
    avg_inhouse_added   = safe_mean(f"additional in-house cases between {period['date_start']} to {period['date_end']}")
    avg_inhouse_nfa_712 = safe_mean(f"in-house cases nfa- 07 and nfa-12 between {period['date_start']} to {period['date_end']}")
    avg_inhouse_nfa_others = safe_mean(f"in-house cases nfa- others between {period['date_start']} to {period['date_end']}")

    # Compute avg_inhouse_reassigned by applying the same formula to every row, if columns exist
    ih_open_col = f"in-house caseload as at {period['date_start']}"
    ih_added_col = f"additional in-house cases between {period['date_start']} to {period['date_end']}"
    ih_nfa712_col = f"in-house cases nfa- 07 and nfa-12 between {period['date_start']} to {period['date_end']}"
    ih_nfa_oth_col = f"in-house cases nfa- others between {period['date_start']} to {period['date_end']}"
    ih_end_col = f"in-house caseload as at {period['date_end']}"

    if {ih_open_col, ih_added_col, ih_nfa712_col, ih_nfa_oth_col, ih_end_col}.issubset(set(case_df.columns)):
        series_op = case_df[ih_open_col]
        series_ad = case_df[ih_added_col]
        series_nfa712 = case_df[ih_nfa712_col]
        series_nfaoth = case_df[ih_nfa_oth_col]
        series_end = case_df[ih_end_col]
        series_completed = series_nfa712 + series_nfaoth
        series_reassigned = series_end - ((series_op + series_ad) - series_completed)
        avg_inhouse_reassigned = round(series_reassigned.mean(), 1)
    else:
        avg_inhouse_reassigned = "N/A"

    avg_inhouse_end = safe_mean(f"in-house caseload as at {period['date_end']}")
    avg_increase_decrease_inhouse = safe_mean("increase /decrease of cases")
    avg_clearance_rate_inhouse = safe_mean("clearance rate (%)")

    #
    # ── ASSIGNED STATISTICS ────────────────────────────────────────────────────────
    #

    assigned_opening    = safe_get(f"assigned caseload as at {period['date_start']}")
    assigned_added      = safe_get(f"additional assigned cases between {period['date_start']} to {period['date_end']}")
    assigned_nfa_712    = safe_get(f"assigned cases nfa- 07 between {period['date_start']} to {period['date_end']}")
    assigned_nfa_others = safe_get(f"assigned cases nfa- others between {period['date_start']} to {period['date_end']}")
    assigned_end        = safe_get(f"assigned caseload as at {period['date_end']}")

    # ── REASSIGNED ASSIGNED (computed) ──────────────────────────────────────────────
    assigned_completed    = assigned_nfa_712 + assigned_nfa_others
    assigned_reassigned   = assigned_end - ((assigned_opening + assigned_added) - assigned_completed)

    # Assigned average (across all officers), rounded to one decimal
    avg_assigned_opening = safe_mean(f"assigned caseload as at {period['date_start']}")
    avg_assigned_added   = safe_mean(f"additional assigned cases between {period['date_start']} to {period['date_end']}")
    avg_assigned_nfa_712 = safe_mean(f"assigned cases nfa- 07 between {period['date_start']} to {period['date_end']}")
    avg_assigned_nfa_others = safe_mean(f"assigned cases nfa- others between {period['date_start']} to {period['date_end']}")

    # Compute avg_assigned_reassigned by applying formula to every row, if columns exist
    as_open_col = f"assigned caseload as at {period['date_start']}"
    as_added_col = f"additional assigned cases between {period['date_start']} to {period['date_end']}"
    as_nfa712_col = f"assigned cases nfa- 07 between {period['date_start']} to {period['date_end']}"
    as_nfa_oth_col = f"assigned cases nfa- others between {period['date_start']} to {period['date_end']}"
    as_end_col = f"assigned caseload as at {period['date_end']}"

    if {as_open_col, as_added_col, as_nfa712_col, as_nfa_oth_col, as_end_col}.issubset(set(case_df.columns)):
        series_op_a = case_df[as_open_col]
        series_ad_a = case_df[as_added_col]
        series_nfa712_a = case_df[as_nfa712_col]
        series_nfaoth_a = case_df[as_nfa_oth_col]
        series_end_a = case_df[as_end_col]
        series_completed_a = series_nfa712_a + series_nfaoth_a
        series_reassigned_a = series_end_a - ((series_op_a + series_ad_a) - series_completed_a)
        avg_assigned_reassigned = round(series_reassigned_a.mean(), 1)
    else:
        avg_assigned_reassigned = "N/A"

    avg_assigned_end = safe_mean(f"assigned caseload as at {period['date_end']}")
    avg_increase_decrease_assigned = safe_mean("increase/ decrease of cases")
    avg_clearance_rate_assigned = safe_mean("clearance rate (%).1")

    #
    # ── TOTAL CASELOAD & OVERALL STATISTICS ─────────────────────────────────────────
    #
    total_start = safe_get(f"total caseload as at {period['date_start']}")
    total_end = safe_get(f"total caseload as at {period['date_end']}")
    total_nfa_ed = safe_get("total cases nfa-ed")
    pct_change_overall = safe_get("% increase or decrease")

    avg_total_caseload_start = safe_mean(f"total caseload as at {period['date_start']}")
    avg_total_caseload_end = safe_mean(f"total caseload as at {period['date_end']}")
    avg_total_cases_nfa_ed = safe_mean("total cases nfa-ed")
    avg_percentage_increase_decrease_overall = safe_mean("% increase or decrease")

    #
    # ── RATINGS EXTRACTION ───────────────────────────────────────────────────────────
    #
    metadata_cols = {
        'case ref no', 'subject matter', 'mto',
        'assigned out indicator', 'applicant', 'abbreviation', 'name', 'type'
    }

    filtered_ratings = ratings_df[ratings_df['name'].str.lower() == officer_name.lower()]

    if not filtered_ratings.empty:
        question_cols = [col for col in filtered_ratings.columns if col not in metadata_cols]
        survey_ratings = {col: round(filtered_ratings[col].mean(), 2) for col in question_cols}

        temp = filtered_ratings.copy()
        temp['avg_score'] = temp[question_cols].mean(axis=1)

        inhouse_case_ratings = []
        assigned_case_ratings = []
        for _, row in temp.iterrows():
            entry = {
                'case_ref': row['case ref no'],
                'applicant': row['applicant'],
                'score': round(row['avg_score'], 2)
            }
            if str(row['assigned out indicator']).strip().upper() == 'N':
                inhouse_case_ratings.append(entry)
            else:
                assigned_case_ratings.append(entry)
    else:
        survey_ratings = {}
        inhouse_case_ratings = []
        assigned_case_ratings = []

    #
    # ── ASSEMBLE FINAL STATS DICTIONARY ────────────────────────────────────────────
    #
    stats = {
        "name": officer_name,
        "abbreviation": abbreviation,
        "function": function,

        "period": period,

        "inhouse_opening": inhouse_opening,
        "inhouse_added": inhouse_added,
        "inhouse_nfa_712": inhouse_nfa_712,
        "inhouse_nfa_others": inhouse_nfa_others,
        "inhouse_reassigned": inhouse_reassigned,
        "inhouse_end": inhouse_end,
        "increase_decrease_inhouse": inhouse_end - inhouse_opening,
        "clearance_rate_inhouse": (
            (inhouse_nfa_712 + inhouse_nfa_others) / inhouse_opening * 100
            if inhouse_opening else 0
        ),

        "assigned_opening": assigned_opening,
        "assigned_added": assigned_added,
        "assigned_nfa_712": assigned_nfa_712,
        "assigned_nfa_others": assigned_nfa_others,
        "assigned_reassigned": assigned_reassigned,
        "assigned_end": assigned_end,
        "increase_decrease_assigned": assigned_end - assigned_opening,
        "clearance_rate_assigned": (
            (assigned_nfa_712 + assigned_nfa_others) / assigned_opening * 100
            if assigned_opening else 0
        ),

        "total_start": total_start,
        "total_end": total_end,
        "total_nfa_ed": total_nfa_ed,
        "pct_change_overall": pct_change_overall,

        "avg_inhouse_opening": avg_inhouse_opening,
        "avg_inhouse_added": avg_inhouse_added,
        "avg_inhouse_nfa_712": avg_inhouse_nfa_712,
        "avg_inhouse_nfa_others": avg_inhouse_nfa_others,
        "avg_inhouse_reassigned": avg_inhouse_reassigned,
        "avg_inhouse_end": avg_inhouse_end,
        "avg_increase_decrease_inhouse": avg_increase_decrease_inhouse,
        "avg_clearance_rate_inhouse": avg_clearance_rate_inhouse,

        "avg_assigned_opening": avg_assigned_opening,
        "avg_assigned_added": avg_assigned_added,
        "avg_assigned_nfa_712": avg_assigned_nfa_712,
        "avg_assigned_nfa_others": avg_assigned_nfa_others,
        "avg_assigned_reassigned": avg_assigned_reassigned,
        "avg_assigned_end": avg_assigned_end,
        "avg_increase_decrease_assigned": avg_increase_decrease_assigned,
        "avg_clearance_rate_assigned": avg_clearance_rate_assigned,

        "avg_total_caseload_start": avg_total_caseload_start,
        "avg_total_caseload_end": avg_total_caseload_end,
        "avg_total_cases_nfa_ed": avg_total_cases_nfa_ed,
        "avg_percentage_increase_decrease_overall": avg_percentage_increase_decrease_overall,

        "survey_ratings": survey_ratings,
        "inhouse_case_ratings": inhouse_case_ratings,
        "assigned_case_ratings": assigned_case_ratings
    }

    return stats


