import streamlit as st
import pandas as pd
import yaml
import ast

from data.loader import load_loan_snapshot
from staging.sicr import assign_stage
from models.lifetime_pd import build_pd_term_structure
from models.lgd_cashflow import lgd_cashflow
from models.ead_amortization import build_ead_schedule
from models.ead_ccf import calculate_ead_ccf

from engine.ecl_monthly import monthly_ecl_without_ead_model
from engine.ecl_monthly import monthly_ecl_with_ead_model

# --- Streamlit UI ---
st.title("IFRS 9 ECL Engine")

st.markdown(
    """
This app calculates **Expected Credit Loss (ECL)** for loans using IFRS 9 methodology.
Upload your loan snapshot CSV to run the engine.
"""
)

uploaded_file = st.file_uploader("Upload Loan Snapshot CSV", type="csv")

if uploaded_file:
    # Load loan snapshot
    loans = pd.read_csv(uploaded_file)

    # Show preview
    st.subheader("Loan Snapshot Preview")
    st.dataframe(loans.head())

    # Convert recovery_cashflows from string to list
    if "recovery_cashflows" in loans.columns:
        loans["recovery_cashflows"] = loans["recovery_cashflows"].apply(
            ast.literal_eval
        )
        loans["recovery_cashflows"] = loans["recovery_cashflows"].apply(
            lambda lst: [(i + 1, cf) for i, cf in enumerate(lst)]
        )

    # Load configs
    with open("config/sicr.yaml") as f:
        sicr_cfg = yaml.safe_load(f)

    with open("config/scenarios.yaml") as f:
        scenarios = yaml.safe_load(f)["scenarios"]

    with open("config/ccf.yaml") as f:
        ccf_cfg = yaml.safe_load(f)

    # Run IFRS 9 engine
    results = []

    st.info("Running IFRS 9 calculations...")

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

        ecl_total = 0.0

        for s in scenarios.values():
            pd_ts = build_pd_term_structure(
                row["pd_12m"], row["remaining_months"], s["pd_multiplier"]
            )

            lgd = (
                lgd_cashflow(row["ead"], row["recovery_cashflows"], row["eir"])
                * s["lgd_multiplier"]
            )

            # ecl = monthly_ecl_without_ead_model(
            #     pd_term_structure=pd_ts,
            #     lgd=lgd,
            #     ead=row["ead"],  # without modelling ead
            #     eir=row["eir"],
            #     stage=stage,
            # )

            ecl = monthly_ecl_with_ead_model(
                pd_term_structure=pd_ts,
                lgd=lgd,
                ead_term_structure=ead_ts,  # With modelling ead
                eir=row["eir"],
                stage=stage,
            )

            ecl_total += s["weight"] * ecl

        results.append(
            {
                "loan_id": row["loan_id"],
                "stage": stage,
                "sicr_reason": sicr_reason,
                "ecl": float(ecl_total),
            }
        )

    df_results = pd.DataFrame(results)

    st.subheader("ECL Results")
    st.dataframe(df_results)

    # Option to download results
    csv = df_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="ifrs9_results.csv",
        mime="text/csv",
    )
