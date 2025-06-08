import pandas as pd
import numpy as np

def compute_officer_stats(officer_row, case_df, ratings_df):
    officer_name = officer_row['name']
    abbreviation = officer_row['abbreviation']
    function = officer_row['function']  # e.g. "LO" or "LE"
    func_lower = function.lower()
    period = {
        "date_start": "08/05/2024",
        "date_end": "02/08/2024",
        "date_start_verbose": "8 May 2024",
        "date_end_verbose": "2 Aug 2024",
        "month_start": "May",
        "month_end": "Aug"
    }

    # Helper to safely get a single officer's value from case_df
    def safe_get(col_name):
        if col_name not in case_df.columns:
            return 0
        series = case_df.loc[
            case_df["name"].str.lower() == officer_name.lower(),
            col_name
        ]
        if series.empty:
            return 0
        return series.squeeze()

    # Helper to compute the average for a given column, but only among
    # rows whose 'function' matches this officer's function.
    def safe_group_mean(col_name):
        if col_name not in case_df.columns:
            return "N/A"
        # Filter to rows where function matches (case-insensitive)
        group = case_df.loc[case_df["function"].str.lower() == func_lower, col_name]
        if group.empty:
            return "N/A"
        return round(group.mean(), 1)

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

    # In‐house averages (across officers with same function), rounded to one decimal
    avg_inhouse_opening       = safe_group_mean(f"in-house caseload as at {period['date_start']}")
    avg_inhouse_added         = safe_group_mean(f"additional in-house cases between {period['date_start']} to {period['date_end']}")
    avg_inhouse_nfa_712       = safe_group_mean(f"in-house cases nfa- 07 and nfa-12 between {period['date_start']} to {period['date_end']}")
    avg_inhouse_nfa_others    = safe_group_mean(f"in-house cases nfa- others between {period['date_start']} to {period['date_end']}")
    avg_inhouse_reassigned    = "N/A"
    # Compute average reassigned for in-house group if all relevant columns exist
    ih_cols = {
        f"in-house caseload as at {period['date_start']}",
        f"additional in-house cases between {period['date_start']} to {period['date_end']}",
        f"in-house cases nfa- 07 and nfa-12 between {period['date_start']} to {period['date_end']}",
        f"in-house cases nfa- others between {period['date_start']} to {period['date_end']}",
        f"in-house caseload as at {period['date_end']}"
    }
    if ih_cols.issubset(set(case_df.columns)):
        group_df = case_df[case_df["function"].str.lower() == func_lower]
        series_op = group_df[f"in-house caseload as at {period['date_start']}"]
        series_ad = group_df[f"additional in-house cases between {period['date_start']} to {period['date_end']}"]
        series_nfa712 = group_df[f"in-house cases nfa- 07 and nfa-12 between {period['date_start']} to {period['date_end']}"]
        series_nfaoth = group_df[f"in-house cases nfa- others between {period['date_start']} to {period['date_end']}"]
        series_end = group_df[f"in-house caseload as at {period['date_end']}"]
        series_completed = series_nfa712 + series_nfaoth
        series_reassigned = series_end - ((series_op + series_ad) - series_completed)
        avg_inhouse_reassigned = round(series_reassigned.mean(), 1)
    avg_inhouse_end            = safe_group_mean(f"in-house caseload as at {period['date_end']}")
    avg_increase_decrease_ih   = safe_group_mean("increase /decrease of cases")
    avg_clearance_rate_ih      = safe_group_mean("clearance rate (%)")

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

    # Assigned averages for the same function group, one decimal
    avg_assigned_opening     = safe_group_mean(f"assigned caseload as at {period['date_start']}")
    avg_assigned_added       = safe_group_mean(f"additional assigned cases between {period['date_start']} to {period['date_end']}")
    avg_assigned_nfa_712     = safe_group_mean(f"assigned cases nfa- 07 between {period['date_start']} to {period['date_end']}")
    avg_assigned_nfa_others  = safe_group_mean(f"assigned cases nfa- others between {period['date_start']} to {period['date_end']}")
    avg_assigned_reassigned  = "N/A"
    as_cols = {
        f"assigned caseload as at {period['date_start']}",
        f"additional assigned cases between {period['date_start']} to {period['date_end']}",
        f"assigned cases nfa- 07 between {period['date_start']} to {period['date_end']}",
        f"assigned cases nfa- others between {period['date_start']} to {period['date_end']}",
        f"assigned caseload as at {period['date_end']}"
    }
    if as_cols.issubset(set(case_df.columns)):
        group_df_a = case_df[case_df["function"].str.lower() == func_lower]
        series_op_a = group_df_a[f"assigned caseload as at {period['date_start']}"]
        series_ad_a = group_df_a[f"additional assigned cases between {period['date_start']} to {period['date_end']}"]
        series_nfa712_a = group_df_a[f"assigned cases nfa- 07 between {period['date_start']} to {period['date_end']}"]
        series_nfaoth_a = group_df_a[f"assigned cases nfa- others between {period['date_start']} to {period['date_end']}"]
        series_end_a = group_df_a[f"assigned caseload as at {period['date_end']}"]
        series_completed_a = series_nfa712_a + series_nfaoth_a
        series_reassigned_a = series_end_a - ((series_op_a + series_ad_a) - series_completed_a)
        avg_assigned_reassigned = round(series_reassigned_a.mean(), 1)
    avg_assigned_end            = safe_group_mean(f"assigned caseload as at {period['date_end']}")
    avg_increase_decrease_as    = safe_group_mean("increase/ decrease of cases")
    avg_clearance_rate_as       = safe_group_mean("clearance rate (%).1")

    #
    # ── TOTAL CASELOAD & OVERALL STATISTICS ─────────────────────────────────────────
    #
    total_start = safe_get(f"total caseload as at {period['date_start']}")
    total_end   = safe_get(f"total caseload as at {period['date_end']}")
    total_nfa_ed = safe_get("total cases nfa-ed")
    pct_change_overall = safe_get("% increase or decrease")

    avg_total_start = safe_group_mean(f"total caseload as at {period['date_start']}")
    avg_total_end   = safe_group_mean(f"total caseload as at {period['date_end']}")
    avg_total_nfa   = safe_group_mean("total cases nfa-ed")
    avg_pct_change  = safe_group_mean("% increase or decrease")

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
        "avg_increase_decrease_inhouse": avg_increase_decrease_ih,
        "avg_clearance_rate_inhouse": avg_clearance_rate_ih,

        "avg_assigned_opening": avg_assigned_opening,
        "avg_assigned_added": avg_assigned_added,
        "avg_assigned_nfa_712": avg_assigned_nfa_712,
        "avg_assigned_nfa_others": avg_assigned_nfa_others,
        "avg_assigned_reassigned": avg_assigned_reassigned,
        "avg_assigned_end": avg_assigned_end,
        "avg_increase_decrease_assigned": avg_increase_decrease_as,
        "avg_clearance_rate_assigned": avg_clearance_rate_as,

        "avg_total_caseload_start": avg_total_start,
        "avg_total_caseload_end": avg_total_end,
        "avg_total_cases_nfa_ed": avg_total_nfa,
        "avg_percentage_increase_decrease_overall": avg_pct_change,

        "survey_ratings": survey_ratings,
        "inhouse_case_ratings": inhouse_case_ratings,
        "assigned_case_ratings": assigned_case_ratings
    }

    return stats
