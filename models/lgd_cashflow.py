def lgd_cashflow(ead, recovery_cashflows, eir):
    if ead <= 0:
        return 0.0

    pv_recoveries = sum(cf / ((1 + eir) ** (t / 12)) for t, cf in recovery_cashflows)

    lgd = 1 - pv_recoveries / ead
    return min(max(lgd, 0.0), 1.0)
