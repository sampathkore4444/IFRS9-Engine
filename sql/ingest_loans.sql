SELECT 
    loan_id,
    pd_12m,
    remaining_months,
    ead,
    eir,
    days_past_due,
    origination_pd,
    recovery_cashflows,
    forbearance_flag
FROM loan_snapshot
WHERE reporting_date = CURRENT_DATE;
