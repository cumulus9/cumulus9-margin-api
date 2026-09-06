# Cumulus9 - All rights reserved.
# Calculate CME listed-rates and delta-ladder margin, then optimize it.

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
    "calculation_type": "margins",
    "in_memory": True,
    "portfolio": [
        {
            "account_code": "CME_RATES_LADDER",
            "exchange_code": "CME",
            "contract_code": "SR3",
            "contract_type": "FUT",
            "contract_expiry": "202803",
            "net_position": 250,
            "account_type": "H",
        },
        {
            "account_code": "CME_RATES_LADDER",
            "index": "USD_SOFR_1D_ERS",
            "tenor": "365D",
            "dv01": -42000,
        },
        {
            "account_code": "CME_RATES_LADDER",
            "index": "USD_SOFR_1D_ERS",
            "tenor": "1826D",
            "dv01": 78000,
        },
        {
            "account_code": "CME_RATES_LADDER",
            "index": "USD_SOFR_1D_ERS",
            "tenor": "3652D",
            "dv01": 115000,
        },
    ],
}

# Calculate the margin for the listed future and delta ladder.
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
# Combined initial margin: $2,957,174.10
# Baseline total: $2,957,174.10
# Optimized total: $2,940,276.84
# Saving: $16,897.26
# Saving: 0.57%
#
# Recommended futures allocation:
# SR3 - Three-Month SOFR (SR3) Futures: SPLIT
# Lots moved to cleared rates: 170
# Lots left in listed margin: 80
