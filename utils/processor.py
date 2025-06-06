
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
        return case_df.loc[case_df['name'] == officer_name, col].values[0] if col in case_df.columns else 0

    def safe_mean(col):
        return round(peer_group[col].mean(), 1) if col in peer_group.columns else 'N/A'

    # In-house
    inhouse_opening = safe_get('In-house Caseload as at 08/05/2024')
    inhouse_added = safe_get('Additional In-house Cases Between 08/05/2024 to 02/08/2024')
    inhouse_nfa_712 = safe_get('In-house Cases NFA- 07 and NFA-12 Between 08/05/2024 to 02/08/2024')
    inhouse_nfa_others = safe_get('In-house Cases NFA- others Between 08/05/2024 to 02/08/2024')
    inhouse_end = safe_get('In-house Caseload as at 02/08/2024')
    inhouse_reassigned = max(inhouse_added - inhouse_nfa_712 - inhouse_nfa_others - (inhouse_end - inhouse_opening), 0)

    # Assigned
    assigned_opening = safe_get('Assigned Caseload as at 08/05/2024')
    assigned_added = safe_get('Additional Assigned Cases Between 08/05/2024 to 02/08/2024')
    assigned_nfa_712 = safe_get('Assigned Cases NFA- 07 Between 08/05/2024 to 02/08/2024')
    assigned_nfa_others = safe_get('Assigned Cases NFA- others Between 08/05/2024 to 02/08/2024')
    assigned_end = safe_get('Assigned Caseload as at 02/08/2024')
    assigned_reassigned = max(assigned_added - assigned_nfa_712 - assigned_nfa_others - (assigned_end - assigned_opening), 0)

    # Averages
    def get_avg(col): return round(peer_group[col].mean(), 1) if col in peer_group.columns else 'N/A'

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
        "avg_inhouse_opening": get_avg('In-house Caseload as at 08/05/2024'),
        "avg_inhouse_added": get_avg('Additional In-house Cases Between 08/05/2024 to 02/08/2024'),
        "avg_inhouse_nfa_712": get_avg('In-house Cases NFA- 07 and NFA-12 Between 08/05/2024 to 02/08/2024'),
        "avg_inhouse_nfa_others": get_avg('In-house Cases NFA- others Between 08/05/2024 to 02/08/2024'),
        "avg_inhouse_reassigned": 'N/A',
        "avg_inhouse_end": get_avg('In-house Caseload as at 02/08/2024'),
        "avg_assigned_opening": get_avg('Assigned Caseload as at 08/05/2024'),
        "avg_assigned_added": get_avg('Additional Assigned Cases Between 08/05/2024 to 02/08/2024'),
        "avg_assigned_nfa_712": get_avg('Assigned Cases NFA- 07 Between 08/05/2024 to 02/08/2024'),
        "avg_assigned_nfa_others": get_avg('Assigned Cases NFA- others Between 08/05/2024 to 02/08/2024'),
        "avg_assigned_reassigned": 'N/A',
        "avg_assigned_end": get_avg('Assigned Caseload as at 02/08/2024')
    }

    return stats
