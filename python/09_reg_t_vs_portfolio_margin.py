# Cumulus9 - All rights reserved.
# Compare OCC Reg T margin with OCC TIMS portfolio margin.

import requests

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = "xxxxxxxxxxxxxxxxxx"
C9_API_SECRET = "sk-xxxxxxxxxxxxxxxxxx"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {C9_API_SECRET}",
}

# The two accounts contain exactly the same AAPL portfolio.
# REGT requests strategy-based Reg T margin.
# C requests risk-based TIMS portfolio margin.
payload = {
    "vendor_symbology": "clearing",
    "calculation_type": "margins",
    "in_memory": True,
    "portfolio": [
        {
            "account_code": "OCC_REG_T",
            "exchange_code": "OCC",
            "contract_code": "AAPL",
            "contract_type": "CASH",
            "net_position": 100,
            "account_type": "REGT",
        },
        {
            "account_code": "OCC_REG_T",
            "exchange_code": "OCC",
            "contract_code": "AAPL",
            "contract_type": "CALL",
            "contract_expiry": "20261016",
            "contract_strike": 340,
            "net_position": -1,
            "account_type": "REGT",
        },
        {
            "account_code": "OCC_REG_T",
            "exchange_code": "OCC",
            "contract_code": "AAPL",
            "contract_type": "PUT",
            "contract_expiry": "20261016",
            "contract_strike": 300,
            "net_position": -1,
            "account_type": "REGT",
        },
        {
            "account_code": "OCC_REG_T",
            "exchange_code": "OCC",
            "contract_code": "AAPL",
            "contract_type": "CALL",
            "contract_expiry": "20261016",
            "contract_strike": 350,
            "net_position": 1,
            "account_type": "REGT",
        },
        {
            "account_code": "OCC_PORTFOLIO_MARGIN",
            "exchange_code": "OCC",
            "contract_code": "AAPL",
            "contract_type": "CASH",
            "net_position": 100,
            "account_type": "C",
        },
        {
            "account_code": "OCC_PORTFOLIO_MARGIN",
            "exchange_code": "OCC",
            "contract_code": "AAPL",
            "contract_type": "CALL",
            "contract_expiry": "20261016",
            "contract_strike": 340,
            "net_position": -1,
            "account_type": "C",
        },
        {
            "account_code": "OCC_PORTFOLIO_MARGIN",
            "exchange_code": "OCC",
            "contract_code": "AAPL",
            "contract_type": "PUT",
            "contract_expiry": "20261016",
            "contract_strike": 300,
            "net_position": -1,
            "account_type": "C",
        },
        {
            "account_code": "OCC_PORTFOLIO_MARGIN",
            "exchange_code": "OCC",
            "contract_code": "AAPL",
            "contract_type": "CALL",
            "contract_expiry": "20261016",
            "contract_strike": 350,
            "net_position": 1,
            "account_type": "C",
        },
    ],
}

response = requests.post(f"{C9_API_ENDPOINT}/portfolios", headers=HEADERS, json=payload)
response.raise_for_status()
results = response.json()

reg_t = next(account for account in results["data"] if account["account_code"] == "OCC_REG_T")
tims = next(account for account in results["data"] if account["account_code"] == "OCC_PORTFOLIO_MARGIN")

difference = tims["initial_margin"] - reg_t["initial_margin"]
sign = "-" if difference < 0 else ""

print(f"Reg T initial margin: ${reg_t['initial_margin']:,.2f}")
print(f"TIMS portfolio margin: ${tims['initial_margin']:,.2f}")
print(f"TIMS minus Reg T: {sign}${abs(difference):,.2f}")

# Example staging output on 6 September 2026:
#
# Reg T initial margin: $20,951.90
# TIMS portfolio margin: $7,163.66
# TIMS minus Reg T: -$13,788.24
