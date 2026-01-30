"""
AUDIT-CRITICAL
Auditors ask for this every month.
"""


def ecl_bridge(prev, curr):
    return {
        "opening_ecl": prev.sum(),
        "closing_ecl": curr.sum(),
        "movement": curr.sum() - prev.sum(),
    }
