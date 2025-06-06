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

    # Helper functions to safely extract values from case_df
    def safe_get(col_name):
        return (
            case_df.loc[case_df["name"].str.lower() == officer_name.lower(), col_name]
            .squeeze()
            if col_name in case_df.columns
            else 0
        )

    def safe_mean(col_name):
        return (
            case_df[col_name].mean() if col_name in case_df.columns else "N/A"
        )

    #
    # ── IN‐HOUSE STATISTICS ─────────────────────────────────────────────────────────
    #

    inhouse_opening    = safe_get(f"in-house caseload as at {period['date_start']}")
    inhouse_added      = safe_get(f"additional in-house cases between {period['date_start']} to {period['date_end']}")
    inhouse_nfa_712    = safe_get(f"in-house cases nfa- 07 and nfa-12 between {period['date_start']} to {period['date_end']}")
    inhouse_nfa_others = safe_get(f"in-house cases nfa- others between {period['date_start']} to {period['date_end']}")
    inhouse_end        = safe_get(f"in-house caseload as at {period['date_end']}")

    # ── REASSIGNED IN‐HOUSE (computed) ─────────────────────────────────────────────
    # “Completed” in‐house cases = NFA‐07+NFA‐12 + NFA‐others
    inhouse_completed   = inhouse_nfa_712 + inhouse_nfa_others
    # Reassigned_in_house = actual_end – [ opening + added – completed ]
    inhouse_reassigned  = inhouse_end - ((inhouse_opening + inhouse_added) - inhouse_completed)

    # In‐house averages (across all officers)
    avg_inhouse_opening             = safe_mean(f"in-house caseload as at {period['date_start']}")
    avg_inhouse_added               = safe_mean(f"additional in-house cases between {period['date_start']} to {period['date_end']}")
    avg_inhouse_nfa_712             = safe_mean(f"in-house cases nfa- 07 and nfa-12 between {period['date_start']} to {period['date_end']}")
    avg_inhouse_nfa_others          = safe_mean(f"in-house cases nfa- others between {period['date_start']} to {period['date_end']}")
    avg_inhouse_reassigned          = "N/A"   # (optional: you can compute a group‐wide mean if desired)
    avg_inhouse_end                 = safe_mean(f"in-house caseload as at {period['date_end']}")
    avg_increase_decrease_inhouse   = safe_mean("increase /decrease of cases")
    avg_clearance_rate_inhouse      = safe_mean("clearance rate (%)")

    #
    # ── ASSIGNED STATISTICS ────────────────────────────────────────────────────────
    #
    assigned_opening    = safe_get(f"assigned caseload as at {period['date_start']}")
    assigned_added      = safe_get(f"additional assigned cases between {period['date_start']} to {period['date_end']}")
    assigned_nfa_712    = safe_get(f"assigned cases nfa- 07 between {period['date_start']} to {period['date_end']}")
    assigned_nfa_others = safe_get(f"assigned cases nfa- others between {period['date_start']} to {period['date_end']}")
    assigned_end        = safe_get(f"assigned caseload as at {period['date_end']}")

    # ── REASSIGNED ASSIGNED (computed) ──────────────────────────────────────────────
    # “Completed” assigned = NFA‐07 + NFA‐others
    assigned_completed    = assigned_nfa_712 + assigned_nfa_others
    # Reassigned_assigned = actual_end – [ opening + added – completed ]
    assigned_reassigned   = assigned_end - ((assigned_opening + assigned_added) - assigned_completed)

    # Assigned averages (across all officers)
    avg_assigned_opening       = safe_mean(f"assigned caseload as at {period['date_start']}")
    avg_assigned_added         = safe_mean(f"additional assigned cases between {period['date_start']} to {period['date_end']}")
    avg_assigned_nfa_712       = safe_mean(f"assigned cases nfa- 07 between {period['date_start']} to {period['date_end']}")
    avg_assigned_nfa_others    = safe_mean(f"assigned cases nfa- others between {period['date_start']} to {period['date_end']}")
    avg_assigned_reassigned    = "N/A"   # (optional: group‐wide mean if desired)
    avg_assigned_end           = safe_mean(f"assigned caseload as at {period['date_end']}")
    avg_increase_decrease_assigned = safe_mean("increase/ decrease of cases")
    avg_clearance_rate_assigned    = safe_mean("clearance rate (%).1")

    #
    # ── TOTAL CASELOAD & OVERALL STATISTICS ─────────────────────────────────────────
    #
    total_start                        = safe_get(f"total caseload as at {period['date_start']}")
    total_end                          = safe_get(f"total caseload as at {period['date_end']}")
    total_nfa_ed                       = safe_get("total cases nfa-ed")
    pct_change_overall                 = safe_get("% increase or decrease")

    avg_total_caseload_start           = safe_mean(f"total caseload as at {period['date_start']}")
    avg_total_caseload_end             = safe_mean(f"total caseload as at {period['date_end']}")
    avg_total_cases_nfa_ed             = safe_mean("total cases nfa-ed")
    avg_percentage_increase_decrease_overall = safe_mean("% increase or decrease")

    #
    # ── ASSEMBLE FINAL STATS DICTIONARY ────────────────────────────────────────────
    #
    stats = {
        # Officer identity
        "name": officer_name,
        "abbreviation": abbreviation,
        "function": function,

        # Period metadata
        "period": period,

        # In‐house stats
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

        # Assigned stats
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

        # Total/ad hoc stats
        "total_start": total_start,
        "total_end": total_end,
        "total_nfa_ed": total_nfa_ed,
        "pct_change_overall": pct_change_overall,

        # Averages across all officers
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
        "avg_percentage_increase_decrease_overall": avg_percentage_increase_decrease_overall
    }

    return stats
