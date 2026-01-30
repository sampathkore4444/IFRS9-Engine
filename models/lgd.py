# CASHFLOW-BASED
# ✔ Discounted
# ✔ Time-based
# ✔ Regulator-approved


def discounted_recoveries(cashflows, eir):
    return sum(cf / ((1 + eir) ** (t / 12)) for t, cf in cashflows)


def lgd(ead, recoveries, eir):
    if ead == 0:
        return 0
    return max(0, 1 - discounted_recoveries(recoveries, eir) / ead)
