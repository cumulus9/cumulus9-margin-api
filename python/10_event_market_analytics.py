# Cumulus9 - All rights reserved.
# Calculate margin and risk analytics for event-market positions.

import os
import requests

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = os.getenv("C9_API_ENDPOINT", "xxxxxxxxxxxxxxxxxx")
C9_API_SECRET = os.getenv("C9_API_SECRET", "sk-xxxxxxxxxxxxxxxxxx")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {C9_API_SECRET}",
}

# Event-market discovery is licence-gated. Use the discovery endpoints to roll
# these tickers when their markets expire.
payload = {
    "vendor_symbology": "clearing",
    "currency_code": "USD",  # Explicit currency for the USD comparison below.
    "calculation_type": "margins",
    "in_memory": True,
    "portfolio": [
        {
            "account_code": "EVENT_ACCOUNT",
            "market_type": "EVENT",
            "exchange_code": "KALSHI",
            "ticker": "AMAZONFTC-29DEC31",
            "side": "YES",
            "quantity": 1000,
            "price_dollars": 0.535,
            "netting_enabled": True,
            "currency_code": "USD",
        },
        {
            "account_code": "EVENT_ACCOUNT",
            "market_type": "EVENT",
            "exchange_code": "KALSHI",
            "ticker": "APPLEUS-29DEC31",
            "side": "NO",
            "quantity": 600,
            "price_dollars": 0.27,
            "netting_enabled": True,
            "currency_code": "USD",
        },
    ],
}

response = requests.post(f"{C9_API_ENDPOINT}/portfolios", headers=HEADERS, json=payload)
response.raise_for_status()
results = response.json()

account = results["data"][0]
event_risk = account["event_risk"]

print(f"Event initial margin: ${account['initial_margin']:,.2f}")
print(f"Value at risk: ${event_risk['value_at_risk']:,.2f}")
print(f"Expected shortfall: ${event_risk['expected_shortfall']:,.2f}")
print(f"Worst stress loss: ${event_risk['stress_loss']:,.2f}")
print(f"Worst stress scenario: {event_risk['stress_scenario']}")
print(f"Positions modelled: {event_risk['coverage']['positions_modelled']}")

print("\nSettlement scenarios:")
for scenario in event_risk["scenarios"]:
    sign = "-" if scenario["pnl"] < 0 else ""
    print(f"{scenario['name']}: {sign}${abs(scenario['pnl']):,.2f}")

print("\nProbability shocks:")
for shock in event_risk["probability_shocks"]["portfolio"]:
    sign = "-" if shock["pnl"] < 0 else ""
    print(f"{shock['shock']:+.0%}: {sign}${abs(shock['pnl']):,.2f}")

# Example staging output on 6 September 2026:
#
# Event initial margin: $697.00
# Value at risk: $20.01
# Expected shortfall: $20.01
# Worst stress loss: $697.00
# Worst stress scenario: full_settlement
# Positions modelled: 2
#
# Settlement scenarios:
# adverse_1sd: -$21.97
# adverse_2sd: -$43.94
# adverse_3sd: -$65.91
# directional_up_3sd: $20.02
# directional_down_3sd: -$20.02
# full_settlement: -$697.00
#
# Probability shocks:
# -30%: -$120.00
# -20%: -$80.00
# -10%: -$40.00
# +0%: $0.00
# +10%: $40.00
# +20%: $80.00
# +30%: $141.00
