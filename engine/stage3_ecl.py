def stage3_ecl(ead, recovery_cashflows, eir):
    pv_recoveries = sum(cf / ((1 + eir) ** (t / 12)) for t, cf in recovery_cashflows)
    return max(ead - pv_recoveries, 0.0)
