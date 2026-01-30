def discount_factor(eir, t):
    return 1 / ((1 + eir) ** (t / 12))
