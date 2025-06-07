import pandas as pd
import numpy as np
from datetime import datetime

def compute_officer_stats(officer_row, case_df, ratings_df, period):
    """
    Compute all of the per-officer metrics _and_ inject the
    human-friendly reporting period strings.
    """
    # Basic officer info
    officer_name = officer_row['name']
    abbreviation = officer_row['abbreviation']
    function     = officer_row['function']  # e.g. "LO" or "LE"

    # Build verbose period labels
    start_dt = datetime.strptime(period['date_start'], "%d/%m/%Y")
    end_dt   = datetime.strptime(period['date_end'],   "%d/%m/%Y")
    period_verbose = {
        "date_start":         period['date_start'],
        "date_end":           period['date_end'],
        "date_start_verbose": start_dt.strftime("%-d %b %Y"),
        "date_end_verbose":   end_dt.strftime("%-d %b %Y"),
        "month_start":        start_dt.strftime("%b"),
        "month_end":          end_dt.strftime("%b"),
    }

    # ——— your existing metric computations go here ———
    # e.g.: filter case_df by abbreviation, compute totals, rates, etc.
    #
    # total_start = ...
    # total_end   = ...
    # clearance_rate = ...
    # survey_ratings = ...
    #
    # etc.

    stats = {
        "officer_name": officer_name,
        "abbreviation": abbreviation,
        "function":     function,
        "period":       period_verbose,

        # — then all your computed metrics, e.g.:
        # "total_caseload_start": total_start,
        # "total_caseload_end":   total_end,
        # "clearance_rate":       clearance_rate,
        # "survey_ratings":       survey_ratings,
        #
        # etc.
    }

    return stats
