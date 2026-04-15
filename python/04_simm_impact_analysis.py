# Cumulus9 - All rights reserved.
# SIMM version impact analysis: compare margin between two SIMM versions.

import time
import requests

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = "xxxxxxxxxxxxxxxxxx"
C9_API_SECRET = "sk-xxxxxxxxxxxxxxxxxx"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {C9_API_SECRET}",
}

# Configure versions to compare
NEW_VERSION = "2_7"
OLD_VERSION = "2_6"
HOLDING_PERIOD = 10


def post_portfolio(payload: dict) -> dict:
    """POST a portfolio payload and return the JSON response."""
    response = requests.post(f"{C9_API_ENDPOINT}/portfolios", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Sample CRIF portfolio
# ---------------------------------------------------------------------------

base_payload = {
    "calculation_type": "simm",
    "portfolio": [
        {
            "account_code": "Account ABC",
            "product_class": "RatesFX",
            "risk_type": "Risk_IRCurve",
            "qualifier": "JPY",
            "bucket": "1",
            "label1": "15Y",
            "label2": "OIS",
            "amount_usd": 10_000_000,
        },
        {
            "account_code": "Account ABC",
            "product_class": "RatesFX",
            "risk_type": "Risk_IRCurve",
            "qualifier": "JPY",
            "bucket": "1",
            "label1": "30Y",
            "label2": "OIS",
            "amount_usd": -100_000,
        },
    ],
}

# ---------------------------------------------------------------------------
# Calculate margin under each version
# ---------------------------------------------------------------------------

start = time.time()

base_payload["simm_metrics"] = {"version": NEW_VERSION, "holding_period": HOLDING_PERIOD}
new_margin = round(post_portfolio(base_payload)["data"][0]["initial_margin"])

base_payload["simm_metrics"] = {"version": OLD_VERSION, "holding_period": HOLDING_PERIOD}
old_margin = round(post_portfolio(base_payload)["data"][0]["initial_margin"])

impact = new_margin - old_margin
elapsed = round(time.time() - start, 2)

print(f"SIMM v{NEW_VERSION.replace('_', '.'):<5}  ${new_margin:>15,}")
print(f"SIMM v{OLD_VERSION.replace('_', '.'):<5}  ${old_margin:>15,}")
print(f"{'Impact':<12}  ${impact:>15,}")
print(f"\nCompleted in {elapsed}s")
