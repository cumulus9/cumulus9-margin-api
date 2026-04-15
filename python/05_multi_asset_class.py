# Cumulus9 - All rights reserved.
# Multi-asset-class portfolio: ETD, Fixed Income, FX, CUSIP, and CRIF
# positions in a single request with margins + analytics + SIMM.

import json
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
# Portfolio combining all five position types
# ---------------------------------------------------------------------------

payload = {
    "calculation_type": "margins,analytics,simm",
    "vendor_symbology": "clearing",
    "currency_code": "USD",
    "use_closest_match": True,
    "risk_metrics": {
        "lookback": 250,
        "ci": 99,
        "method": "value-at-risk",
        "mpor": 1,
        "mode": "absolute",
    },
    "simm_metrics": {
        "version": "2_6_5",
        "holding_period": 10,
    },
    "portfolio": [
        # --- ETD: futures and options ---
        {
            "account_code": "ETD_Account",
            "exchange_code": "NYMEX",
            "contract_code": "CL",
            "contract_type": "FUT",
            "contract_expiry": "202612",
            "net_position": "500",
            "account_type": "H",
        },
        {
            "account_code": "ETD_Account",
            "exchange_code": "NYMEX",
            "contract_code": "LO",
            "contract_type": "CALL",
            "contract_expiry": "202612",
            "contract_strike": "75",
            "net_position": "-200",
            "account_type": "H",
        },
        {
            "account_code": "ETD_Account",
            "exchange_code": "EUREX",
            "contract_code": "FDAX",
            "contract_type": "FUT",
            "contract_expiry": "202612",
            "net_position": "-50",
            "account_type": "H",
        },
        # --- Fixed Income: bonds by terms ---
        {
            "account_code": "FI_Account",
            "currency": "USD",
            "contract_type": "BOND",
            "maturity": "20461021",
            "coupon_rate": 6,
            "coupon_frequency": 2,
            "notional": 1000000,
        },
        {
            "account_code": "FI_Account",
            "currency": "USD",
            "contract_type": "BOND",
            "maturity": "20361021",
            "coupon_rate": 4,
            "coupon_frequency": 2,
            "notional": -1000000,
        },
        # --- FX ---
        {
            "account_code": "FX_Account",
            "currency_pair": "EUR_USD",
            "amount": 5000000,
        },
        {
            "account_code": "FX_Account",
            "currency_pair": "GBP_JPY",
            "amount": -3000000,
        },
        # --- Fixed Income by CUSIP ---
        {
            "account_code": "CUSIP_Account",
            "cusip": "912828ZT6",
            "notional": 2000000,
        },
        # --- CRIF (SIMM) ---
        {
            "account_code": "SIMM_Account",
            "im_model": "SIMM",
            "product_class": "RatesFX",
            "risk_type": "Risk_IRCurve",
            "qualifier": "USD",
            "bucket": "1",
            "label1": "15Y",
            "label2": "OIS",
            "amount_usd": 1000000,
        },
        {
            "account_code": "SIMM_Account",
            "im_model": "SIMM",
            "product_class": "RatesFX",
            "risk_type": "Risk_IRCurve",
            "qualifier": "EUR",
            "bucket": "1",
            "label1": "10Y",
            "label2": "OIS",
            "amount_usd": -500000,
        },
    ],
}

# ---------------------------------------------------------------------------
# Submit and print results
# ---------------------------------------------------------------------------

results = post_portfolio(payload)

print(f"Request: {results['request_id']}  |  Status: {results['status']}  |  Runtime: {results.get('runtime', '?')}ms\n")

for account in results["data"]:
    im = account["initial_margin"]
    var = account.get("value_at_risk", 0)
    dv01 = account.get("dv01", 0)
    print(f"  {account['account_code']:<20}  IM: ${im:>14,.2f}  VaR: ${var:>14,.2f}  DV01: ${dv01:>10,.2f}")

    # Show exceptions if any
    if account.get("exceptions"):
        for exc in account["exceptions"]:
            print(f"    [exception] position {exc['position_id']}: {exc['exception']}")

    # Show closest matches if any
    if account.get("closest_matches"):
        for cm in account["closest_matches"]:
            print(f"    [closest match] position {cm['position_id']}: {cm['exception']}")

print(f"\nFull response:\n{json.dumps(results, indent=2)}")
