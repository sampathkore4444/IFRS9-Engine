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


def monthly_ecl(pd_term_structure, lgd, ead, eir, stage):
    horizon = 12 if stage == 1 else pd_term_structure["month"].max()
    ecl = 0.0

    for _, row in pd_term_structure.iterrows():
        if row["month"] > horizon:
            break

        df = 1 / ((1 + eir) ** (row["month"] / 12))
        ecl += row["monthly_pd"] * lgd * ead * df

    return ecl
