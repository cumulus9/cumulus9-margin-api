# Cumulus9 - All rights reserved.
# Calculate margin and risk analytics for event-market positions.

import requests

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = "xxxxxxxxxxxxxxxxxx"
C9_API_SECRET = "sk-xxxxxxxxxxxxxxxxxx"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {C9_API_SECRET}",
}

# Event tickers change as markets expire. Replace these with active tickers.
payload = {
    "vendor_symbology": "clearing",
    "calculation_type": "margins",
    "in_memory": True,
    "portfolio": [
        {
            "account_code": "EVENT_ACCOUNT",
            "market_type": "EVENT",
            "exchange_code": "KALSHI",
            "ticker": "KXMARALAGO-27-RDES",
            "side": "YES",
            "quantity": 1000,
            "price_dollars": 0.54,
            "netting_enabled": True,
            "currency_code": "USD",
        },
        {
            "account_code": "EVENT_ACCOUNT",
            "market_type": "EVENT",
            "exchange_code": "KALSHI",
            "ticker": "KXNFLDPOTY-27-KHAM",
            "side": "NO",
            "quantity": 600,
            "price_dollars": 0.63,
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
# Event initial margin: $918.00
# Value at risk: $23.64
# Expected shortfall: $23.64
# Worst stress loss: $262.00
# Worst stress scenario: full_settlement
# Positions modelled: 2
#
# Settlement scenarios:
# adverse_1sd: -$40.03
# adverse_2sd: -$80.06
# adverse_3sd: -$120.10
# directional_up_3sd: $120.10
# directional_down_3sd: -$120.10
# full_settlement: -$262.00
#
# Probability shocks:
# -30%: -$245.00
# -20%: -$200.00
# -10%: -$100.00
# +0%: $0.00
# +10%: $100.00
# +20%: $200.00
# +30%: $300.00
