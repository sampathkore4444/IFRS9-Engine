import yaml
from data.loader import load_loan_snapshot
from staging.sicr import assign_stage
from models.lifetime_pd import build_pd_term_structure
from models.lgd_cashflow import lgd_cashflow

from models.ead_amortization import build_ead_schedule
from models.ead_ccf import calculate_ead_ccf

from engine.ecl_monthly import monthly_ecl_with_ead_model
from engine.ecl_monthly import monthly_ecl_without_ead_model
import ast


# Load configs
with open("config/sicr.yaml") as f:
    sicr_cfg = yaml.safe_load(f)

with open("config/scenarios.yaml") as f:
    scenarios = yaml.safe_load(f)["scenarios"]

with open("config/ccf.yaml") as f:
    ccf_cfg = yaml.safe_load(f)

# Load data
loans = load_loan_snapshot("loan_snapshot.csv")
print(loans.head())

# Convert recovery_cashflows from string to list
loans["recovery_cashflows"] = loans["recovery_cashflows"].apply(ast.literal_eval)

# Convert to list of (t, cf)
loans["recovery_cashflows"] = loans["recovery_cashflows"].apply(
    lambda lst: [(i + 1, cf) for i, cf in enumerate(lst)]
)

results = []

for _, row in loans.iterrows():
    stage, sicr_reason = assign_stage(row, sicr_cfg)

    # -----------------------------
    # EAD LOGIC (ADD HERE) to model ead
    # -----------------------------
    product = row["product_type"]

    if product in ["term_loan", "mortgage"]:
        # Contractual amortization
        ead_ts = build_ead_schedule(
            ead=row["ead"], eir=row["eir"], remaining_months=row["remaining_months"]
        )

    elif product in ["credit_card", "overdraft"]:
        # CCF-based EAD
        ead_ccf = calculate_ead_ccf(
            outstanding=row["ead"],
            limit=row["credit_limit"],
            ccf=ccf_cfg[product]["ccf"],
        )
        ead_ts = [ead_ccf] * row["remaining_months"]

    else:
        # Fallback (safe default)
        ead_ts = [row["ead"]] * row["remaining_months"]

    # -----------------------------
    # Continue as before
    # -----------------------------

    ecl_total = 0.0

    for s in scenarios.values():
        pd_ts = build_pd_term_structure(
            row["pd_12m"], row["remaining_months"], s["pd_multiplier"]
        )

        lgd = (
            lgd_cashflow(row["ead"], row["recovery_cashflows"], row["eir"])
            * s["lgd_multiplier"]
        )

        ecl = monthly_ecl_without_ead_model(
            pd_term_structure=pd_ts,
            lgd=lgd,
            ead=row["ead"],  # without modelling ead
            eir=row["eir"],
            stage=stage,
        )

        # ecl = monthly_ecl_with_ead_model(
        #     pd_term_structure=pd_ts,
        #     lgd=lgd,
        #     ead_term_structure=ead_ts,  # With modelling ead
        #     eir=row["eir"],
        #     stage=stage,
        # )

        ecl_total += s["weight"] * ecl

    results.append(
        {
            "loan_id": row["loan_id"],
            "stage": stage,
            "sicr_reason": sicr_reason,
            "ecl": float(ecl_total),
        }
    )

for r in results:
    print(r)

    """import yaml
from data.loader_sql import load_loan_snapshot_sql, save_ecl_to_sql
from staging.sicr import assign_stage
from models.lifetime_pd import build_pd_term_structure
from models.lgd_cashflow import lgd_cashflow
from engine.ecl_monthly import monthly_ecl
from utils.logger import get_logger

logger = get_logger(__name__)

def main_ifrs9():
    # Load configs
    with open("config/sicr.yaml") as f:
        sicr_cfg = yaml.safe_load(f)
    with open("config/scenarios.yaml") as f:
        scenarios = yaml.safe_load(f)["scenarios"]

    # Load loans from SQL
    conn_string = "postgresql://user:password@host:port/db"
    query = "SELECT * FROM loan_snapshot WHERE reporting_date = CURRENT_DATE;"
    loans = load_loan_snapshot_sql(conn_string, query)

    results = []

    for _, row in loans.iterrows():
        stage, sicr_reason = assign_stage(row, sicr_cfg)
        ecl_total = 0.0

        for s in scenarios.values():
            pd_ts = build_pd_term_structure(
                row["pd_12m"], row["remaining_months"], s["pd_multiplier"]
            )
            lgd = lgd_cashflow(row["ead"], row["recovery_cashflows"], row["eir"]) * s["lgd_multiplier"]
            ecl = monthly_ecl(pd_ts, lgd, row["ead"], row["eir"], stage)
            ecl_total += s["weight"] * ecl

        results.append({
            "loan_id": row["loan_id"],
            "stage": stage,
            "sicr_reason": sicr_reason,
            "ecl": ecl_total
        })

    df_results = pd.DataFrame(results)
    save_ecl_to_sql(df_results, conn_string, "ifrs9_ecl_results")
    logger.info("IFRS 9 run completed successfully")

    """
