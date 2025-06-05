
import pandas as pd
import numpy as np
from datetime import datetime

def compute_officer_stats(officer_row, caseload_df, ratings_df, period, all_caseload_df):
    abbreviation = officer_row['abbreviation']
    officer_name = officer_row['name']
    function = officer_row['function']

    # Filter officer caseload
    officer_cases = caseload_df[caseload_df['officer'] == abbreviation]
    officer_all_cases = all_caseload_df[all_caseload_df['officer'] == abbreviation]

    # Determine peer group for averages
    peer_group = all_caseload_df[all_caseload_df['function'] == function]

    def safe_mean(series):
        return int(round(series.mean())) if not series.empty else 'N/A'

    # Section 1: Opening
    inhouse_opening = officer_cases['In-house Caseload as at ' + period['date_start']].sum()
    assigned_opening = officer_cases['Assigned Caseload as at ' + period['date_start']].sum()

    avg_inhouse_opening = safe_mean(peer_group['In-house Caseload as at ' + period['date_start']])
    avg_assigned_opening = safe_mean(peer_group['Assigned Caseload as at ' + period['date_start']])

    # Section 2: Changes in period
    inhouse_added = officer_cases['In-house Cases Received'].sum()
    inhouse_nfa_712 = officer_cases['In-house Cases NFA (7, 12)'].sum()
    inhouse_nfa_others = officer_cases['In-house Cases NFA (Others)'].sum()
    inhouse_reassigned = officer_cases['In-house Reassigned to Others'].sum()

    assigned_added = officer_cases['Assigned Cases Received'].sum()
    assigned_nfa_712 = officer_cases['Assigned Cases NFA (7, 12)'].sum()
    assigned_nfa_others = officer_cases['Assigned Cases NFA (Others)'].sum()
    assigned_reassigned = officer_cases['Assigned Reassigned to Others'].sum()

    avg_inhouse_added = safe_mean(peer_group['In-house Cases Received'])
    avg_inhouse_nfa_712 = safe_mean(peer_group['In-house Cases NFA (7, 12)'])
    avg_inhouse_nfa_others = safe_mean(peer_group['In-house Cases NFA (Others)'])
    avg_inhouse_reassigned = safe_mean(peer_group['In-house Reassigned to Others'])

    avg_assigned_added = safe_mean(peer_group['Assigned Cases Received'])
    avg_assigned_nfa_712 = safe_mean(peer_group['Assigned Cases NFA (7, 12)'])
    avg_assigned_nfa_others = safe_mean(peer_group['Assigned Cases NFA (Others)'])
    avg_assigned_reassigned = safe_mean(peer_group['Assigned Reassigned to Others'])

    # Section 3: Closing
    inhouse_end = officer_cases['In-house Caseload as at ' + period['date_end']].sum()
    assigned_end = officer_cases['Assigned Caseload as at ' + period['date_end']].sum()

    avg_inhouse_end = safe_mean(peer_group['In-house Caseload as at ' + period['date_end']])
    avg_assigned_end = safe_mean(peer_group['Assigned Caseload as at ' + period['date_end']])

    return {
        'name': officer_name,
        'abbreviation': abbreviation,
        'function': function,
        'period': {
            'date_start': period['date_start'],
            'date_end': period['date_end'],
            'date_start_verbose': period['date_start_verbose'],
            'date_end_verbose': period['date_end_verbose'],
            'month_start': period['month_start'],
            'month_end': period['month_end']
        },
        'inhouse_opening': inhouse_opening,
        'assigned_opening': assigned_opening,
        'avg_inhouse_opening': avg_inhouse_opening,
        'avg_assigned_opening': avg_assigned_opening,

        'inhouse_added': inhouse_added,
        'inhouse_nfa_712': inhouse_nfa_712,
        'inhouse_nfa_others': inhouse_nfa_others,
        'inhouse_reassigned': inhouse_reassigned,

        'assigned_added': assigned_added,
        'assigned_nfa_712': assigned_nfa_712,
        'assigned_nfa_others': assigned_nfa_others,
        'assigned_reassigned': assigned_reassigned,

        'avg_inhouse_added': avg_inhouse_added,
        'avg_inhouse_nfa_712': avg_inhouse_nfa_712,
        'avg_inhouse_nfa_others': avg_inhouse_nfa_others,
        'avg_inhouse_reassigned': avg_inhouse_reassigned,

        'avg_assigned_added': avg_assigned_added,
        'avg_assigned_nfa_712': avg_assigned_nfa_712,
        'avg_assigned_nfa_others': avg_assigned_nfa_others,
        'avg_assigned_reassigned': avg_assigned_reassigned,

        'inhouse_end': inhouse_end,
        'assigned_end': assigned_end,
        'avg_inhouse_end': avg_inhouse_end,
        'avg_assigned_end': avg_assigned_end
    }
