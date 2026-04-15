# Cumulus9 - All rights reserved.
# Margin ageing: estimate how margin changes as contracts approach maturity
# by decrementing expiry dates and recalculating.

import datetime
import json
import pandas as pd
import requests

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = "xxxxxxxxxxxxxxxxxx"
C9_API_SECRET = "sk-xxxxxxxxxxxxxxxxxx"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {C9_API_SECRET}",
}


def post_portfolio(payload: dict) -> dict:
    """POST a portfolio payload and return the JSON response."""
    response = requests.post(f"{C9_API_ENDPOINT}/portfolios", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Ageing helpers
# ---------------------------------------------------------------------------


def offset_date(date_str: str, days: int) -> str:
    """Shift a YYYYMMDD (or YYYYMM) date string by the given number of days."""
    if len(date_str) == 6 or date_str[-2:] == "00":
        date_str = date_str[:6] + "28"
    dt = datetime.datetime.strptime(date_str, "%Y%m%d").date() + datetime.timedelta(days=days)
    return dt.strftime("%Y%m%d")


def is_expired(date_str: str) -> bool:
    """Return True if the contract expiry is in the past."""
    if len(date_str) == 6 or date_str[-2:] == "00":
        date_str = date_str[:6] + "28"
    return datetime.datetime.today().date() > datetime.datetime.strptime(date_str, "%Y%m%d").date()


def age_portfolio(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """Return a copy of the portfolio with expiries shifted back by `days`, dropping expired rows."""
    df = df.copy()
    df["contract_expiry"] = df["contract_expiry"].apply(lambda x: offset_date(str(x), -days))
    df = df[~df["contract_expiry"].apply(lambda x: is_expired(str(x)))]
    return df


def calculate_total_margin(df: pd.DataFrame) -> float:
    """Submit a portfolio DataFrame and return the total initial margin across all accounts."""
    payload = {
        "vendor_symbology": "clearing",
        "calculation_type": "margins",
        "portfolio": json.loads(df.to_json(orient="records")),
    }
    results = post_portfolio(payload)
    return sum(account["initial_margin"] for account in results["data"])


# ---------------------------------------------------------------------------
# Run ageing analysis
# ---------------------------------------------------------------------------

df = pd.read_csv("./sample_portfolio.csv", dtype=str, na_filter=False)

offsets = [0, 30, 90, 120]
for days in offsets:
    aged = age_portfolio(df, days) if days > 0 else df.copy()
    if days > 0:
        aged["account_code"] = aged["account_code"] + f"_aged_{days}d"
    margin = calculate_total_margin(aged)
    label = "now" if days == 0 else f"{days}d"
    print(f"{label}:\t${margin:,.0f}")
