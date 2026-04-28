# Cumulus9 - All rights reserved.
# Posting portfolios by account and sub-account, then reading gross vs. net margins.
#
# When `sub_account_code` is set on a position, the API stores the position
# both at the parent (master) account level AND at the sub-account level.
# The response contains one result row per portfolio:
#   - The parent account row aggregates every sub-account underneath it.
#   - Each sub-account gets its own row with `parent_portfolio_id` linking back.
#
# `gross_margin` is the sum of margins computed before any cross-account or
# cross-portfolio offset; `initial_margin` is the post-offset (net) requirement.
# Comparing the two reveals the diversification benefit at the master level.

import json
import requests

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = "xxxxxxxxxxxxxxxxxx"
C9_API_SECRET = "sk-xxxxxxxxxxxxxxxxxx"


HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {C9_API_SECRET}"}


def post_portfolio(payload: dict) -> dict:
    response = requests.post(f"{C9_API_ENDPOINT}/portfolios", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Portfolio: one master account "FUND_A" split across two sub-accounts
# ---------------------------------------------------------------------------
# Sub-account "STRAT_LONG" runs a long Brent Crude futures book.
# Sub-account "STRAT_SHORT" runs a short Brent Crude futures book on the
# same contract. At the master account level the two books partially offset,
# so initial_margin (net) will be lower than gross_margin (sum of sub-accounts).

payload = {
    "vendor_symbology": "clearing",
    "calculation_type": "margins",
    "portfolio": [
        {
            "account_code": "FUND_A",
            "sub_account_code": "STRAT_LONG",
            "sub_account_name": "Long-only Energy Strategy",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "FUT",
            "contract_expiry": "203612",
            "net_position": "1000",
            "account_type": "H",
        },
        {
            "account_code": "FUND_A",
            "sub_account_code": "STRAT_SHORT",
            "sub_account_name": "Short-only Energy Strategy",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "FUT",
            "contract_expiry": "203612",
            "net_position": "-700",
            "account_type": "H",
        },
        {
            "account_code": "FUND_A",
            "sub_account_code": "STRAT_LONG",
            "exchange_code": "NYMEX",
            "contract_code": "CL",
            "contract_type": "FUT",
            "contract_expiry": "203612",
            "net_position": "500",
            "account_type": "H",
        },
    ],
}

results = post_portfolio(payload)

# ---------------------------------------------------------------------------
# Inspect results
# ---------------------------------------------------------------------------
# `data` contains one entry per portfolio. The parent account row has no
# `parent_portfolio_id`; sub-account rows carry their parent's portfolio_id.

parents = [r for r in results["data"] if not r.get("parent_portfolio_id")]
sub_accounts = [r for r in results["data"] if r.get("parent_portfolio_id")]

print("Master accounts:")
for r in parents:
    im = r["initial_margin"]
    gm = r["gross_margin"]
    offset = gm - im
    print(f"  {r['account_code']:<15} initial=${im:>14,.2f}  gross=${gm:>14,.2f}  offset=${offset:>12,.2f}")

print("\nSub-accounts:")
for r in sub_accounts:
    parent = next((p for p in parents if p["portfolio_id"] == r["parent_portfolio_id"]), None)
    parent_label = parent["account_code"] if parent else "?"
    im = r["initial_margin"]
    gm = r["gross_margin"]
    print(f"  {parent_label} / {r['account_code']:<15} initial=${im:>14,.2f}  gross=${gm:>14,.2f}")

# Full response for reference
print("\nFull response:")
print(json.dumps(results, indent=2))
