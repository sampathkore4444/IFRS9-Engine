"""
CORE SYSTEM
✔ Scenario weighted
✔ Discounted
✔ Stage-aware (extended in prod)
"""

from engine.discounting import discount_factor


def calculate_ecl(row, scenarios):
    total_ecl = 0

    for s in scenarios.values():
        pd = min(row["pd"] * s["pd_multipier"], 1)
        lgd = min(row["lgd"] * s["lgd_multipier"], 1)
        df = discount_factor(row["eir"], 12)

        scenario_ecl = pd * lgd * row["EAD"] * df

        total_ecl += s["weight"] * scenario_ecl

    return total_ecl
