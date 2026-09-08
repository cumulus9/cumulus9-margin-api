# Cumulus9 - All rights reserved.
# Staging only: GBP reporting totals with native USD and EUR margin rows.
import os
import requests

payload = {
    "calculation_type": "margins",
    "currency_code": "GBP",  # Omit this key to use General Currency in staging.
    "vendor_symbology": "clearing",
    "in_memory": True,
    "portfolio": [
        {"account_code": "REPORTING_CURRENCY", "exchange_code": "CME", "contract_code": "ES", "contract_type": "FUT", "contract_expiry": "DEC-27", "net_position": "2", "account_type": "H"},
        {"account_code": "REPORTING_CURRENCY", "exchange_code": "EUREX", "contract_code": "FDAX", "contract_type": "FUT", "contract_expiry": "17-DEC-27", "net_position": "1", "account_type": "H"},
    ],
}
response = requests.post(
    f"{os.environ['C9_API_ENDPOINT']}/portfolios",
    headers={"Authorization": f"Bearer {os.environ['C9_API_SECRET']}"},
    json=payload,
)
response.raise_for_status()
for account in response.json()["data"]:
    if account.get("currency_version") != 1:
        raise RuntimeError("This example requires staging reporting-currency version 1.")
    currency = account["currency_code"]
    target_rate = account["reporting_fxrate"]
    print(f"Initial margin: {currency} {account['initial_margin']:,.2f}")
    for row in account.get("margin_by_ccp") or []:
        native_rate = row.get("fxrate")
        if not native_rate or not target_rate:
            print(f"{row['clearing_org']}: currency conversion unavailable")
            continue
        converted = row["initial_margin"] / native_rate * target_rate
        print(f"{row['clearing_org']}: {currency} {converted:,.2f} (native {row['currency_code']} {row['initial_margin']:,.2f})")
