import numpy as np
import pandas as pd


def pd12_to_monthly_hazard(pd_12m):
    if pd_12m <= 0:
        return 0.0
    if pd_12m >= 1:
        return 1.0
    return -np.log(1 - pd_12m) / 12


def build_pd_term_structure(pd_12m, months, scenario_multiplier):
    hazard = pd12_to_monthly_hazard(pd_12m) * scenario_multiplier
    survival = 1.0
    rows = []

    for t in range(1, months + 1):
        monthly_pd = 1 - np.exp(-hazard)
        survival *= 1 - monthly_pd
        rows.append(
            {"month": t, "monthly_pd": monthly_pd, "cumulative_pd": 1 - survival}
        )

    return pd.DataFrame(rows)
