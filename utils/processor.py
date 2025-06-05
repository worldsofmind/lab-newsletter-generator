
def compute_officer_stats(officer_row, caseload_df, ratings_df, namelist_df):
    officer_name = officer_row['name']
    officer_abbr = officer_row['abbreviation']
    officer_function = officer_row['function']

    # Filter case load for this officer
    officer_cases = caseload_df[caseload_df['Abbreviation'] == officer_abbr]
    if officer_cases.empty:
        return {}

    # Determine if the officer is an LO or LE
    is_lo = officer_function.strip().upper() == 'LO'
    group_key = 'LO' if is_lo else 'LE'

    # Filter caseload by group for LO Avg or LE Avg calculations
    group_cases = caseload_df[caseload_df['function'].str.upper().str.strip() == group_key]

    # Extract relevant values and safely convert to integers
    def safe_int(val):
        try:
            return int(val)
        except:
            return 0

    stats = {
        'inhouse_opening': safe_int(officer_cases['In-House Opening'].values[0]),
        'assigned_opening': safe_int(officer_cases['Assigned Opening'].values[0]),
        'inhouse_added': safe_int(officer_cases['In-House Additions'].values[0]),
        'assigned_added': safe_int(officer_cases['Assigned Additions'].values[0]),
        'inhouse_nfa': safe_int(officer_cases['In-House NFA'].values[0]),
        'assigned_nfa': safe_int(officer_cases['Assigned NFA'].values[0]),
        'inhouse_reassigned': safe_int(officer_cases['In-House Reassigned'].values[0]),
        'assigned_reassigned': safe_int(officer_cases['Assigned Reassigned'].values[0]),
        'inhouse_end': safe_int(officer_cases['In-House End'].values[0]),
        'assigned_end': safe_int(officer_cases['Assigned End'].values[0]),
    }

    # Compute averages across group
    def avg(column):
        vals = group_cases[column].apply(safe_int)
        return round(vals.mean(), 1) if not vals.empty else 'N/A'

    avg_stats = {
        'avg_inhouse_opening': avg('In-House Opening'),
        'avg_assigned_opening': avg('Assigned Opening'),
        'avg_inhouse_added': avg('In-House Additions'),
        'avg_assigned_added': avg('Assigned Additions'),
        'avg_inhouse_nfa': avg('In-House NFA'),
        'avg_assigned_nfa': avg('Assigned NFA'),
        'avg_inhouse_reassigned': avg('In-House Reassigned'),
        'avg_assigned_reassigned': avg('Assigned Reassigned'),
        'avg_inhouse_end': avg('In-House End'),
        'avg_assigned_end': avg('Assigned End')
    }

    stats.update(avg_stats)
    stats['name'] = officer_name
    stats['abbreviation'] = officer_abbr
    stats['function'] = officer_function

    return stats
