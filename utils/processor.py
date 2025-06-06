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

    group_col = "function"
    peer_group = case_df[case_df[group_col] == function]

    # Extract statistics for the officer
    def safe_get(col):
        # Ensure 'name' is lowercase here too
        return case_df.loc[case_df['name'] == officer_name, col].values[0] if col in case_df.columns else 0

    def safe_mean(col):
        return round(peer_group[col].mean(), 1) if col in peer_group.columns else 'N/A'

    # In-house stats - IMPORTANT: All column names changed to lowercase to match data_loader.py output
    inhouse_opening = safe_get('in-house caseload as at 08/05/2024')
    inhouse_added = safe_get('additional in-house cases between 08/05/2024 to 02/08/2024')
    inhouse_nfa_712 = safe_get('in-house cases nfa- 07 and nfa-12 between 08/05/2024 to 02/08/2024')
    inhouse_nfa_others = safe_get('in-house cases nfa- others between 08/05/2024 to 02/08/2024')
    inhouse_end = safe_get('in-house caseload as at 02/08/2024')
    # Re-evaluating this line based on potential data inconsistencies vs. calculated
    # If the CSV directly provides 'Increase /Decrease of Cases' then it's directly from CSV
    # If not, this calculation needs to be robust. Given the initial issue is KeyError, let's assume direct mapping.
    inhouse_reassigned = 0 # Placeholder if not directly in CSV, or calculate if formula is needed.

    # Assigned stats - IMPORTANT: All column names changed to lowercase to match data_loader.py output
    assigned_opening = safe_get('assigned caseload as at 08/05/2024')
    assigned_added = safe_get('additional assigned cases between 08/05/2024 to 02/08/2024')
    assigned_nfa_712 = safe_get('assigned cases nfa- 07 between 08/05/2024 to 02/08/2024')
    assigned_nfa_others = safe_get('assigned cases nfa- others between 08/05/2024 to 02/08/2024')
    assigned_end = safe_get('assigned caseload as at 02/08/2024')
    assigned_reassigned = 0 # Placeholder if not directly in CSV

    # Totals (assuming these columns exist and are handled by data_loader for lowercasing)
    total_caseload_start = safe_get('total caseload as at 08/05/2024')
    total_caseload_end = safe_get('total caseload as at 02/08/2024')
    total_cases_nfa_ed = safe_get('total cases nfa-ed')
    percentage_increase_decrease = safe_get('% increase or decrease')


    # Averages - IMPORTANT: All column names changed to lowercase to match data_loader.py output
    avg_inhouse_opening = safe_mean('in-house caseload as at 08/05/2024')
    avg_inhouse_added = safe_mean('additional in-house cases between 08/05/2024 to 02/08/2024')
    avg_inhouse_nfa_712 = safe_mean('in-house cases nfa- 07 and nfa-12 between 08/05/2024 to 02/08/2024')
    avg_inhouse_nfa_others = safe_mean('in-house cases nfa- others between 08/05/2024 to 02/08/2024')
    avg_inhouse_reassigned = 'N/A' # If not in CSV, or 'N/A' as calculated above
    avg_inhouse_end = safe_mean('in-house caseload as at 02/08/2024')
    avg_increase_decrease_inhouse = safe_mean('increase /decrease of cases') # Check for exact name from CSV if still problem
    avg_clearance_rate_inhouse = safe_mean('clearance rate (%)')

    avg_assigned_opening = safe_mean('assigned caseload as at 08/05/2024')
    avg_assigned_added = safe_mean('additional assigned cases between 08/05/2024 to 02/08/2024')
    avg_assigned_nfa_712 = safe_mean('assigned cases nfa- 07 between 08/05/2024 to 02/08/2024')
    avg_assigned_nfa_others = safe_mean('assigned cases nfa- others between 08/05/2024 to 02/08/2024')
    avg_assigned_reassigned = 'N/A' # If not in CSV
    avg_assigned_end = safe_mean('assigned caseload as at 02/08/2024')
    avg_increase_decrease_assigned = safe_mean('increase/ decrease of cases')
    avg_clearance_rate_assigned = safe_mean('clearance rate (%).1') # Check for exact name from CSV if still problem

    avg_total_caseload_start = safe_mean('total caseload as at 08/05/2024')
    avg_total_caseload_end = safe_mean('total caseload as at 02/08/2024')
    avg_total_cases_nfa_ed = safe_mean('total cases nfa-ed')
    avg_percentage_increase_decrease_overall = safe_mean('% increase or decrease')

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
        "assigned_opening": assigned_opening,
        "assigned_added": assigned_added,
        "assigned_nfa_712": assigned_nfa_712,
        "assigned_nfa_others": assigned_nfa_others,
        "assigned_reassigned": assigned_reassigned,
        "assigned_end": assigned_end,
        "total_caseload_start": total_caseload_start,
        "total_caseload_end": total_caseload_end,
        "total_cases_nfa_ed": total_cases_nfa_ed,
        "percentage_increase_decrease": percentage_increase_decrease,

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
