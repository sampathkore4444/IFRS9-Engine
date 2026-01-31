def calculate_ead_ccf(outstanding, limit, ccf):
    """
    EAD calculation for revolving facilities
    """
    undrawn = max(limit - outstanding, 0)
    return outstanding + ccf * undrawn
