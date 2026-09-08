# Cumulus9 - All rights reserved.
# Calculate CME listed-rates and cleared-IRS margin, then optimize it.

import os
import requests

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = os.getenv("C9_API_ENDPOINT", "xxxxxxxxxxxxxxxxxx")
C9_API_SECRET = os.getenv("C9_API_SECRET", "sk-xxxxxxxxxxxxxxxxxx")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {C9_API_SECRET}",
}

payload = {
    "vendor_symbology": "clearing",
    "currency_code": "USD",  # Explicit currency for the USD comparison below.
    "calculation_type": "margins",
    "in_memory": True,
    "portfolio": [
        {
            "account_code": "CME_RATES_IRS",
            "exchange_code": "CME",
            "contract_code": "SR3",
            "contract_type": "FUT",
            "contract_expiry": "202803",
            "net_position": -250,
            "account_type": "H",
        },
        {
            "account_code": "CME_RATES_IRS",
            "clearing_house": "CME",
            "trade_id": "IRS-10Y-RECEIVE",
            "type": "OIS",
            "direction": "RECEIVE",
            "notional": 100000000,
            "currency": "USD",
            "effective_date": "20260908",
            "maturity_date": "20360908",
            "fixed_rate": 3.50,
            "float_index": "USD-SOFR-COMPOUND",
            "pay_frequency": "6M",
        },
        {
            "account_code": "CME_RATES_IRS",
            "clearing_house": "CME",
            "trade_id": "IRS-5Y-PAY",
            "type": "OIS",
            "direction": "PAY",
            "notional": 50000000,
            "currency": "USD",
            "effective_date": "20260908",
            "maturity_date": "20310908",
            "fixed_rate": 3.35,
            "float_index": "USD-SOFR-COMPOUND",
            "pay_frequency": "6M",
        },
    ],
}

# Calculate the margin for the combined portfolio.
response = requests.post(f"{C9_API_ENDPOINT}/portfolios", headers=HEADERS, json=payload)
response.raise_for_status()
results = response.json()

print(f"Combined initial margin: ${results['data'][0]['initial_margin']:,.2f}")

# Find the best allocation between listed and cleared-rates margin.
payload["portfolio"][0]["cross_margin"] = True
response = requests.post(f"{C9_API_ENDPOINT}/portfolios/optimize", headers=HEADERS, json=payload)
response.raise_for_status()
optimization = response.json()["data"][0]

print(f"Baseline total: ${optimization['baseline']['total']:,.2f}")
print(f"Optimized total: ${optimization['optimized']['total']:,.2f}")
print(f"Saving: ${optimization['optimized']['saving']:,.2f}")
print(f"Saving: {optimization['optimized']['saving_pct']:.2f}%")

print("\nRecommended futures allocation:")
for leg in optimization["legs"]:
    print(f"{leg['contract_code']}: {leg['recommendation']}")
    print(f"Lots moved to cleared rates: {leg['lots_to_seq']}")
    print(f"Lots left in listed margin: {leg['lots_left_in_seg']}")

# Example staging output on 6 September 2026:
#
# Combined initial margin: $3,527,745.46
# Baseline total: $3,527,745.46
# Optimized total: $2,992,170.20
# Saving: $535,575.26
# Saving: 15.18%
#
# Recommended futures allocation:
# SR3 - Three-Month SOFR (SR3) Futures: MOVE_TO_SEQ
# Lots moved to cleared rates: -250
# Lots left in listed margin: 0
