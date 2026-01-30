import pandas as pd
from utils.logger import get_logger
import sqlalchemy

logger = get_logger(__name__)


def load_loan_snapshot(path):
    logger.info("Loading loan snapshot")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("Loan snapshot is empty")

    return df


def load_loan_snapshot_sql(conn_string, query):
    engine = sqlalchemy.create_engine(conn_string)
    logger.info("Loading loan snapshot from SQL")
    df = pd.read_sql(query, engine)
    return df


def save_ecl_to_sql(df, conn_string, table_name):
    engine = sqlalchemy.create_engine(conn_string)
    logger.info(f"Saving ECL results to table {table_name}")
    df.to_sql(table_name, engine, if_exists="replace", index=False)
