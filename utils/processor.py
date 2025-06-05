import pandas as pd

def _get_value(row, column, default=0):
    try:
        val = row[column]
        return int(val) if pd.notnull(val) else default
    except KeyError:
        return default

def compute_officer_stats(row, caseload_df, ratings_df, period, all_caseload_df):
    name = row["Name"]
    abbreviation = row["Abbreviation"]
    function = row["self_type"]

    stats = {
        "inhouse_opening": _get_value(row, "In-house Caseload as at 08/05/2024"),
        "inhouse_added": _get_value(row, "Additional In-house Cases Between 08/05/2024 to 02/08/2024"),
        "inhouse_nfa": _get_value(row, "In-house Cases NFA- 07 and NFA-12 Between 08/05/2024 to 02/08/2024")
                       + _get_value(row, "In-house Cases NFA- others Between 08/05/2024 to 02/08/2024"),
        "inhouse_end": _get_value(row, "In-house Caseload as at 02/08/2024"),
        "assigned_opening": _get_value(row, "Assigned Caseload as at 08/05/202 4"),
        "assigned_added": _get_value(row, "Additional Assigned Cases Between 08/05/2024 to 02/08/2024"),
        "assigned_nfa": _get_value(row, "Assigned Cases NFA- 07 Between 08/05/2024 to 02/08/2024")
                        + _get_value(row, "Assigned Cases NFA- others Between 08/05/2024 to 02/08/2024"),
        "assigned_end": _get_value(row, "Assigned Caseload as at 02/08/2024")
    }

    # Derived reassigned counts
    stats["inhouse_reassigned"] = (
        stats["inhouse_opening"] + stats["inhouse_added"] -
        stats["inhouse_nfa"] - stats["inhouse_end"]
    )
    stats["assigned_reassigned"] = (
        stats["assigned_opening"] + stats["assigned_added"] -
        stats["assigned_nfa"] - stats["assigned_end"]
    )

    # Averages
    def avg(col_name):
        try:
            vals = pd.to_numeric(all_caseload_df[col_name], errors="coerce").dropna()
            return round(vals.mean(), 1) if not vals.empty else "N/A"
        except KeyError:
            return "N/A"

    return {
        "name": name,
        "abbreviation": abbreviation,
        "function": function,
        "period": period,
        **stats,
        "avg_inhouse_opening": avg("In-house Caseload as at 08/05/2024"),
        "avg_inhouse_added": avg("Additional In-house Cases Between 08/05/2024 to 02/08/2024"),
        "avg_inhouse_nfa": avg("In-house Cases NFA- 07 and NFA-12 Between 08/05/2024 to 02/08/2024")
                           + avg("In-house Cases NFA- others Between 08/05/2024 to 02/08/2024"),
        "avg_inhouse_end": avg("In-house Caseload as at 02/08/2024"),
        "avg_inhouse_reassigned": "N/A",  # complex to average across derived field
        "avg_assigned_opening": avg("Assigned Caseload as at 08/05/202 4"),
        "avg_assigned_added": avg("Additional Assigned Cases Between 08/05/2024 to 02/08/2024"),
        "avg_assigned_nfa": avg("Assigned Cases NFA- 07 Between 08/05/2024 to 02/08/2024")
                            + avg("Assigned Cases NFA- others Between 08/05/2024 to 02/08/2024"),
        "avg_assigned_end": avg("Assigned Caseload as at 02/08/2024"),
        "avg_assigned_reassigned": "N/A"  # same as above
    }
