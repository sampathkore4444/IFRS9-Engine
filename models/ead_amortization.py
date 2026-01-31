def build_ead_schedule(ead, eir, remaining_months):
    """
    Returns monthly EAD schedule for amortizing loans
    """
    monthly_rate = eir / 12
    n = remaining_months

    # Monthly installment
    pmt = (monthly_rate * ead) / (1 - (1 + monthly_rate) ** -n)

    ead_schedule = []
    outstanding = ead

    for t in range(1, n + 1):
        interest = outstanding * monthly_rate
        principal = pmt - interest
        outstanding = max(outstanding - principal, 0)

        ead_schedule.append(outstanding)

    return ead_schedule
