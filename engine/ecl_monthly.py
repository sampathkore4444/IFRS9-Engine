# def monthly_ecl(pd_term_structure, lgd, ead, eir, stage, max_months):
#     ecl = 0.0

#     horizon = 12 if stage == 1 else max_months

#     for _, row in pd_term_structure.iterrows():
#         t = row["month"]
#         if t > horizon:
#             break

#         df = 1 / ((1 + eir) ** (t / 12))
#         ecl += row["monthly_pd"] * lgd * ead * df

#     return ecl


# def monthly_ecl(pd_term_structure, lgd, ead, eir, stage):
#     horizon = 12 if stage == 1 else pd_term_structure["month"].max()
#     ecl = 0.0

#     for _, row in pd_term_structure.iterrows():
#         if row["month"] > horizon:
#             break

#         df = 1 / ((1 + eir) ** (row["month"] / 12))
#         ecl += row["monthly_pd"] * lgd * ead * df

#     return ecl


def monthly_ecl(pd_term_structure, lgd, ead_term_structure, eir, stage):
    ecl = 0.0

    # Convert pandas → list (CRITICAL FIX)
    if hasattr(pd_term_structure, "values"):
        pd_ts = pd_term_structure.values.flatten().tolist()
    else:
        pd_ts = pd_term_structure

    horizon = min(12 if stage == 1 else len(pd_ts), len(ead_term_structure))

    for t in range(horizon):
        discount = 1 / ((1 + eir) ** ((t + 1) / 12))
        ecl += pd_ts[t] * lgd * ead_term_structure[t] * discount

    return ecl
