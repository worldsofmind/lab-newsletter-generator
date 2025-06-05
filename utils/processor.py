
import pandas as pd
from collections import defaultdict

def compute_officer_stats(case_df, ratings_df, namelist_df):
    officers = []
    officer_groups = namelist_df.groupby('self_type')

    for _, row in namelist_df.iterrows():
        abbreviation = row['abbreviation']
        name = row['Name']
        function = row['Function']
        group = row['self_type']

        officer_data = {
            'abbreviation': abbreviation,
            'name': name,
            'function': function,
            'period': {
                'date_start': case_df.columns[1].split()[-1],
                'date_end': case_df.columns[-1].split()[-1],
                'date_start_verbose': "8 May 2024",
                'date_end_verbose': "2 Aug 2024",
                'month_start': "May",
                'month_end': "Aug"
            }
        }

        # Extract case data
        officer_cases = case_df[case_df['Name'] == name]

        def safe_sum(col):
            return officer_cases[col].sum() if col in officer_cases else 0

        # Opening & Closing
        officer_data['inhouse_opening'] = safe_sum(case_df.columns[1])
        officer_data['assigned_opening'] = safe_sum(case_df.columns[2])
        officer_data['inhouse_end'] = safe_sum(case_df.columns[-2])
        officer_data['assigned_end'] = safe_sum(case_df.columns[-1])

        # In-period changes
        officer_data['inhouse_added'] = safe_sum('New In-house')
        officer_data['inhouse_nfa_712'] = safe_sum('NFA7 In-house') + safe_sum('NFA12 In-house')
        officer_data['inhouse_nfa_others'] = safe_sum('NFA Other In-house')
        officer_data['inhouse_reassigned'] = safe_sum('Reassigned In-house')

        officer_data['assigned_added'] = safe_sum('New Assigned')
        officer_data['assigned_nfa_712'] = safe_sum('NFA7 Assigned') + safe_sum('NFA12 Assigned')
        officer_data['assigned_nfa_others'] = safe_sum('NFA Other Assigned')
        officer_data['assigned_reassigned'] = safe_sum('Reassigned Assigned')

        # Group-level averages (LO/LE)
        group_cases = case_df[case_df['self_type'] == group]

        def avg(col):
            return round(group_cases[col].mean(), 1) if col in group_cases else "N/A"

        officer_data['avg_inhouse_opening'] = avg(case_df.columns[1])
        officer_data['avg_assigned_opening'] = avg(case_df.columns[2])
        officer_data['avg_inhouse_end'] = avg(case_df.columns[-2])
        officer_data['avg_assigned_end'] = avg(case_df.columns[-1])
        officer_data['avg_inhouse_added'] = avg('New In-house')
        officer_data['avg_inhouse_nfa_712'] = avg('NFA7 In-house') + avg('NFA12 In-house') if 'NFA7 In-house' in case_df and 'NFA12 In-house' in case_df else "N/A"
        officer_data['avg_inhouse_nfa_others'] = avg('NFA Other In-house')
        officer_data['avg_inhouse_reassigned'] = avg('Reassigned In-house')
        officer_data['avg_assigned_added'] = avg('New Assigned')
        officer_data['avg_assigned_nfa_712'] = avg('NFA7 Assigned') + avg('NFA12 Assigned') if 'NFA7 Assigned' in case_df and 'NFA12 Assigned' in case_df else "N/A"
        officer_data['avg_assigned_nfa_others'] = avg('NFA Other Assigned')
        officer_data['avg_assigned_reassigned'] = avg('Reassigned Assigned')

        # Survey ratings
        survey_rows = ratings_df[ratings_df['abbreviation'] == abbreviation]
        survey_ratings = {}
        for col in survey_rows.columns[2:]:
            valid_scores = survey_rows[col].dropna().astype(float)
            if not valid_scores.empty:
                survey_ratings[col] = round(valid_scores.mean(), 1)
        officer_data['survey_ratings'] = survey_ratings

        # Case ratings
        inhouse_ratings = []
        assigned_ratings = []
        for _, r in survey_rows.iterrows():
            ref = r['case_ref'] if 'case_ref' in r else "N/A"
            applicant = r['applicant'] if 'applicant' in r else "N/A"
            score = r['rating'] if 'rating' in r else None
            if pd.notna(score):
                score = round(float(score), 1)
                if r['case_type'] == 'In-House':
                    inhouse_ratings.append({'case_ref': ref, 'applicant': applicant, 'score': score})
                elif r['case_type'] == 'Assigned':
                    assigned_ratings.append({'case_ref': ref, 'applicant': applicant, 'score': score})

        officer_data['inhouse_case_ratings'] = inhouse_ratings
        officer_data['assigned_case_ratings'] = assigned_ratings

        officers.append(officer_data)

    return officers
