# Cumulus9 - All rights reserved.
# Calculate fixed-income VaR, stress tests and FICC margin.

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
    "calculation_type": "margins,analytics",
    "in_memory": True,
    "stress_test_enabled": True,
    "stress_test_details_enabled": True,
    "risk_metrics": {
        "lookback": 250,
        "ci": 99,
        "method": "value-at-risk",
        "mpor": 1,
    },
    "portfolio": [
        {
            "account_code": "UST_FICC_ACCOUNT",
            "contract_type": "UST",
            "currency": "USD",
            "maturity": "20281115",
            "coupon_rate": 4.125,
            "coupon_frequency": 2,
            "notional": 25000000,
        },
        {
            "account_code": "UST_FICC_ACCOUNT",
            "contract_type": "UST",
            "currency": "USD",
            "maturity": "20331115",
            "coupon_rate": 4.500,
            "coupon_frequency": 2,
            "notional": -15000000,
        },
        {
            "account_code": "UST_FICC_ACCOUNT",
            "contract_type": "UST",
            "currency": "USD",
            "maturity": "20431115",
            "coupon_rate": 4.750,
            "coupon_frequency": 2,
            "notional": 10000000,
        },
    ],
}

response = requests.post(f"{C9_API_ENDPOINT}/portfolios", headers=HEADERS, json=payload)
response.raise_for_status()
results = response.json()

account = results["data"][0]
ficc_margin = sum(
    row["initial_margin"]
    for row in account["margin_by_ccp"]
    if row["result_type"] == "ficc"
)
dv01_sign = "-" if account["dv01"] < 0 else ""

print(f"Total initial margin: ${account['initial_margin']:,.2f}")
print(f"FICC initial margin: ${ficc_margin:,.2f}")
print(f"Value at risk: ${account['value_at_risk']:,.2f}")
print(f"Worst stress loss: ${account['stress_loss']:,.2f}")
print(f"DV01: {dv01_sign}${abs(account['dv01']):,.2f} per bp")

print("\nConfigured stress test P&L:")
scenario_names = {
    scenario["scenario_id"]: scenario["scenario_name"]
    for scenario in account["stress_tests"]["scenarios"]
}
for scenario in account["stress_tests"]["values"]:
    if scenario["stress_loss"] != 0:
        sign = "-" if scenario["stress_loss"] < 0 else ""
        print(f"{scenario_names[scenario['scenario_id']]}: {sign}${abs(scenario['stress_loss']):,.2f}")

# Example staging output on 6 September 2026:
#
# Total initial margin: $148,998.42
# FICC initial margin: $148,998.42
# Value at risk: $70,336.59
# Worst stress loss: $184,936.57
# DV01: -$7,142.63 per bp
#
# Configured stress test P&L:
# Brexit Referendum (2016): -$1,554.14
# Russian invasion of Ukraine (2022): $1,165.97
# Negative Oil Prices Really (2020): -$1,554.14
# COVID-19 Pandemic Financial Crisis (2020): -$4,272.54
# Italian Economic Crisis (2018): -$777.14
