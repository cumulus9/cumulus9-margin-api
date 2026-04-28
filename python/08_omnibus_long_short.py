# Cumulus9 - All rights reserved.
# Using the omnibus indicator with explicit long_qty / short_qty.
#
# An omnibus account holds positions on behalf of multiple end-clients whose
# longs and shorts must NOT be netted for margin purposes -- the clearing
# house charges margin on the gross long and the gross short separately.
#
# To request omnibus treatment:
#   - Set `omnibus_ind = "Y"` on the position.
#   - Provide `long_qty` and `short_qty` instead of relying on `net_position`
#     alone. The engine charges margin against both sides.
#
# Important: `omnibus_ind` applies ONLY to sub-accounts. A position must
# carry both `account_code` (the master/clearing account) and
# `sub_account_code` (the omnibus book) for the flag to take effect.
# Non-omnibus sub-accounts can be submitted alongside in the same request --
# leave `omnibus_ind` unset (or "F") for them.

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
    response = requests.post(f"{C9_API_ENDPOINT}/portfolios", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Portfolio: one master clearing account "FCM_001" with two sub-accounts.
#   - OMNIBUS_A is an omnibus book: 800 long and 600 short of the same
#     contract held for different end-clients. Margin is charged on
#     800 long + 600 short separately (1400 contracts), NOT on the
#     net 200 long.
#   - PROP_DESK is a proprietary book on a different contract, with normal
#     net-position treatment.
# ---------------------------------------------------------------------------

payload = {
    "vendor_symbology": "clearing",
    "calculation_type": "margins",
    "portfolio": [
        # Omnibus sub-account: explicit long and short legs, do not net.
        {
            "account_code": "FCM_001",
            "sub_account_code": "OMNIBUS_A",
            "sub_account_name": "Customer Omnibus Book A",
            "exchange_code": "NYMEX",
            "contract_code": "CL",
            "contract_type": "FUT",
            "contract_expiry": "203612",
            "long_qty": "800",
            "short_qty": "600",
            "net_position": "200",  # = long_qty - short_qty
            "omnibus_ind": "Y",
            "account_type": "H",
        },
        # Non-omnibus prop sub-account on a different contract.
        {
            "account_code": "FCM_001",
            "sub_account_code": "PROP_DESK",
            "sub_account_name": "Proprietary Trading Desk",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "FUT",
            "contract_expiry": "203612",
            "net_position": "300",
            "omnibus_ind": "F",
            "account_type": "H",
        },
    ],
}

results = post_portfolio(payload)

# ---------------------------------------------------------------------------
# Inspect results -- compare omnibus vs. non-omnibus sub-accounts
# ---------------------------------------------------------------------------

for r in results["data"]:
    label = r["account_code"]
    if r.get("parent_portfolio_id"):
        parent = next((p for p in results["data"] if p["portfolio_id"] == r["parent_portfolio_id"]), None)
        if parent:
            label = f"{parent['account_code']} / {r['account_code']}"
    im = r["initial_margin"]
    gm = r["gross_margin"]
    print(f"{label:<30} initial_margin=${im:>14,.2f}  gross_margin=${gm:>14,.2f}")

# Full response for reference
print("\nFull response:")
print(json.dumps(results, indent=2))
