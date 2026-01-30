# VALIDATION-FRIENDLY
import numpy as np


def monthly_hazard(pd_12m):
    return -np.log(1 - pd_12m) / 12


def lifetime_pd(pd_12m, months, scenario_multiplier):
    h = monthly_hazard(pd_12m=pd_12m) * scenario_multiplier
    survival = np.exp(-h * months)

    return 1 - survival
