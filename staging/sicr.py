# # Significant increase in credit risk
# def assign_stage(row, sicr_cfg):
#     if row["days_past_due"] >= sicr_cfg["days_past_due_stage3"]:
#         return 3, "DEFAULT"

#     sicr_triggers = []

#     if row["days_past_due"] >= sicr_cfg["days_past_due_stage2"]:
#         sicr_triggers.append("30_DPD")

#     if row["current_pd"] >= sicr_cfg["pd_deterioration_factor"] * row["origination_pd"]:
#         sicr_triggers.append("PD_DETERIORATION")

#     if row["forbearance_flag"] == 1:
#         sicr_triggers.append("FORBEARANCE")

#     if sicr_triggers:
#         return 2, ",".join(sicr_triggers)

#     return 1, "PERFORMING"


def assign_stage(row, sicr_cfg):
    if row["days_past_due"] >= sicr_cfg["days_past_due_stage3"]:
        return 3, "DEFAULT"

    triggers = []

    if row["days_past_due"] >= sicr_cfg["days_past_due_stage2"]:
        triggers.append("30_DPD")

    if row["pd_12m"] >= sicr_cfg["pd_deterioration_factor"] * row["origination_pd"]:
        triggers.append("PD_DETERIORATION")

    if triggers:
        return 2, ",".join(triggers)

    return 1, "PERFORMING"
