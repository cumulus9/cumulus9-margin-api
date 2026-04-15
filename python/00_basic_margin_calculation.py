# Cumulus9 - All rights reserved.
# Basic synchronous margin calculation for an ETD portfolio.

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
# Portfolio payload -- multi-account, multi-exchange ETD positions
# ---------------------------------------------------------------------------

payload = {
    "vendor_symbology": "clearing",
    "calculation_type": "margins",
    "portfolio": [
        {
            "account_code": "Account 001",
            "exchange_code": "ASX",
            "contract_code": "XT",
            "contract_type": "F",
            "contract_expiry": "DEC-25",
            "contract_strike": "",
            "net_position": "500",
            "account_type": "H",
        },
        {
            "account_code": "Account 001",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "Future",
            "contract_expiry": "DEC-25",
            "contract_strike": "",
            "net_position": "500",
            "account_type": "H",
        },
        {
            "account_code": "Account 001",
            "exchange_code": "NYMEX",
            "contract_code": "LO",
            "contract_type": "CALL",
            "contract_expiry": "202512",
            "contract_strike": "50.1",
            "net_position": "-1000",
            "account_type": "H",
        },
        {
            "account_code": "Account 002",
            "exchange_code": "EUREX",
            "contract_code": "FDAX",
            "contract_type": "FUT",
            "contract_expiry": "202612",
            "contract_strike": "",
            "net_position": "-50",
            "account_type": "H",
        },
    ],
}

# ---------------------------------------------------------------------------
# Submit and print results
# ---------------------------------------------------------------------------

results = post_portfolio(payload)

for account in results["data"]:
    print(f"{account['account_code']}: initial_margin = ${account['initial_margin']:,.2f}")

# Full JSON response:
print(json.dumps(results, indent=2))
