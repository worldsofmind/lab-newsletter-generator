
import pandas as pd
import numpy as np
from datetime import datetime
import re

def parse_case_count(value):
    try:
        return int(value)
    except:
        return 0

def compute_case_stats(case_df, officer_name, officer_function, function_group, date_start, date_end):
    df = case_df.copy()
    df['Name'] = df['Name'].str.strip()
    officer_df = df[df['Name'] == officer_name]

    # Determine peer group
    peer_df = df[df['Function'] == officer_function]

    # Section 1: Opening
    inhouse_opening = parse_case_count(officer_df['In-house Caseload as at ' + date_start].values[0]) if not officer_df.empty else 0
    assigned_opening = parse_case_count(officer_df['Assigned Caseload as at ' + date_start].values[0]) if not officer_df.empty else 0
    avg_inhouse_opening = peer_df['In-house Caseload as at ' + date_start].apply(parse_case_count).mean()
    avg_assigned_opening = peer_df['Assigned Caseload as at ' + date_start].apply(parse_case_count).mean()

    # Section 2: Changes in period
    def get_stat(col):
        return parse_case_count(officer_df[col].values[0]) if col in officer_df else 0

    inhouse_added = get_stat('In-house Additions')
    inhouse_nfa_712 = get_stat('In-house NFA 7,12')
    inhouse_nfa_others = get_stat('In-house NFA Others')
    inhouse_reassigned = get_stat('In-house Reassigned')

    assigned_added = get_stat('Assigned Additions')
    assigned_nfa_712 = get_stat('Assigned NFA 7,12')
    assigned_nfa_others = get_stat('Assigned NFA Others')
    assigned_reassigned = get_stat('Assigned Reassigned')

    def avg_stat(col):
        return peer_df[col].apply(parse_case_count).mean() if col in peer_df.columns else 0

    avg_inhouse_added = avg_stat('In-house Additions')
    avg_inhouse_nfa_712 = avg_stat('In-house NFA 7,12')
    avg_inhouse_nfa_others = avg_stat('In-house NFA Others')
    avg_inhouse_reassigned = avg_stat('In-house Reassigned')

    avg_assigned_added = avg_stat('Assigned Additions')
    avg_assigned_nfa_712 = avg_stat('Assigned NFA 7,12')
    avg_assigned_nfa_others = avg_stat('Assigned NFA Others')
    avg_assigned_reassigned = avg_stat('Assigned Reassigned')

    # Section 3: Closing
    inhouse_end = parse_case_count(officer_df['In-house Caseload as at ' + date_end].values[0]) if not officer_df.empty else 0
    assigned_end = parse_case_count(officer_df['Assigned Caseload as at ' + date_end].values[0]) if not officer_df.empty else 0
    avg_inhouse_end = peer_df['In-house Caseload as at ' + date_end].apply(parse_case_count).mean()
    avg_assigned_end = peer_df['Assigned Caseload as at ' + date_end].apply(parse_case_count).mean()

    return {
        'inhouse_opening': inhouse_opening,
        'assigned_opening': assigned_opening,
        'avg_inhouse_opening': round(avg_inhouse_opening, 1),
        'avg_assigned_opening': round(avg_assigned_opening, 1),
        'inhouse_added': inhouse_added,
        'inhouse_nfa_712': inhouse_nfa_712,
        'inhouse_nfa_others': inhouse_nfa_others,
        'inhouse_reassigned': inhouse_reassigned,
        'assigned_added': assigned_added,
        'assigned_nfa_712': assigned_nfa_712,
        'assigned_nfa_others': assigned_nfa_others,
        'assigned_reassigned': assigned_reassigned,
        'avg_inhouse_added': round(avg_inhouse_added, 1),
        'avg_inhouse_nfa_712': round(avg_inhouse_nfa_712, 1),
        'avg_inhouse_nfa_others': round(avg_inhouse_nfa_others, 1),
        'avg_inhouse_reassigned': round(avg_inhouse_reassigned, 1),
        'avg_assigned_added': round(avg_assigned_added, 1),
        'avg_assigned_nfa_712': round(avg_assigned_nfa_712, 1),
        'avg_assigned_nfa_others': round(avg_assigned_nfa_others, 1),
        'avg_assigned_reassigned': round(avg_assigned_reassigned, 1),
        'inhouse_end': inhouse_end,
        'assigned_end': assigned_end,
        'avg_inhouse_end': round(avg_inhouse_end, 1),
        'avg_assigned_end': round(avg_assigned_end, 1)
    }
