# Cumulus9 - All rights reserved.
# Batch processing: submit a large portfolio for background calculation
# and poll for completion.

import time
import requests

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = "xxxxxxxxxxxxxxxxxx"
C9_API_SECRET = "sk-xxxxxxxxxxxxxxxxxx"

HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {C9_API_SECRET}"}

# ---------------------------------------------------------------------------
# Build a large portfolio (multiple accounts)
# ---------------------------------------------------------------------------

account_codes = [f"account_{i:04d}" for i in range(200)]
portfolio = []
for i, account_code in enumerate(account_codes):
    portfolio.append(
        {
            "account_code": account_code,
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "FUT",
            "contract_expiry": "203212",
            "net_position": str(100 * (i + 1)),
            "account_type": "H",
        }
    )

payload = {"calculation_type": "margins", "vendor_symbology": "clearing", "portfolio": portfolio}

# ---------------------------------------------------------------------------
# Step 1: Submit the batch
# ---------------------------------------------------------------------------
# x-processing-mode options:
#   "fifo"        - First-in, first-out (default)
#   "priority"    - Priority queue promotion
#   "replace_all" - Clear all queued batches for this user before adding

response = requests.post(
    f"{C9_API_ENDPOINT}/portfolios/batch", headers={**HEADERS, "x-processing-mode": "fifo"}, json=payload
)
response.raise_for_status()

batch_id = response.json()["batch_id"]
print(f"Batch submitted: {batch_id}")

# ---------------------------------------------------------------------------
# Step 2: Poll for completion
# ---------------------------------------------------------------------------

while True:
    status_response = requests.get(f"{C9_API_ENDPOINT}/portfolios/batch/{batch_id}", headers=HEADERS)
    status_response.raise_for_status()
    status = status_response.json()

    pct = status["completed_pct"]
    state = status["status"]
    runtime = status["runtime_ms"]

    print(f"  [{state}] {pct:.1f}% complete ({runtime}ms elapsed)")

    if state in ("completed", "failed", "completed_with_errors"):
        break

    time.sleep(5)

print(f"\nBatch {state} in {status['runtime_ms']}ms")
if status.get("completed_at"):
    print(f"Completed at: {status['completed_at']}")

if state == "failed":
    raise SystemExit("Batch failed; no results to fetch.")

# ---------------------------------------------------------------------------
# Step 3: Fetch results
# ---------------------------------------------------------------------------
# One call for the whole batch. The batch is split into chunks internally, and
# how many depends on engine response sizes and worker memory, so this answers
# at the level you submitted instead. Page with limit/offset for a large book.

batch_accounts = []
offset = 0
while True:
    page_response = requests.get(
        f"{C9_API_ENDPOINT}/portfolios/batch/{batch_id}/results",
        headers=HEADERS,
        params={"limit": 5000, "offset": offset},
    )
    page_response.raise_for_status()
    page = page_response.json()
    batch_accounts.extend(page["results"])
    offset += len(page["results"])
    if not page["results"] or offset >= page["total"]:
        break

print(f"\nFetched {len(batch_accounts)} account results")

total_im = sum(a.get("initial_margin") or 0 for a in batch_accounts)
print(f"Total initial margin across batch: ${total_im:,.2f}\n")

# Print the top 5 accounts by initial margin
top = sorted(batch_accounts, key=lambda a: a.get("initial_margin") or 0, reverse=True)[:5]
print("Top 5 accounts by initial margin:")
for a in top:
    print(f"  {a['account_code']}: ${a['initial_margin']:,.2f} ({a['status']})")

# `source` is "live" when the account still carries this batch's calculation, so
# every field is populated. It turns "history" once a later calculation has
# replaced the account's current figures: initial_margin, OLV, additional
# margin, VaR and stress loss survive, while requirement and the gross figures
# come back None rather than as a zero you would read as a real number.
superseded = [a for a in batch_accounts if a["source"] == "history"]
if superseded:
    print(f"\n{len(superseded)} accounts have been recalculated since this batch ran")

# ---------------------------------------------------------------------------
# Step 4: Drill down into one account
# ---------------------------------------------------------------------------
# The call above returns account totals. GET /results returns the full
# calculation detail: per-engine breakdowns, priced positions, exceptions.
# Always pass portfolio_id -- without it you get every account in that chunk,
# which for a large book can be tens of megabytes.

first = batch_accounts[0]
detail_response = requests.get(
    f"{C9_API_ENDPOINT}/results",
    headers=HEADERS,
    params={"request_id": first["request_id"], "portfolio_id": first["portfolio_id"]},
)
detail_response.raise_for_status()
detail = detail_response.json()

print(f"\nDrill-down for {first['account_code']}:")
for account in detail:
    positions = account.get("portfolio") or []
    print(f"  {len(positions)} positions, IM ${account['initial_margin']:,.2f}")

# portfolio_id is derived from the account code, so you can address one account
# without reading the list first:
#
#   import hashlib
#   portfolio_id = hashlib.md5(account_codes[0].encode()).hexdigest()
#
# For the current state of the whole book, regardless of which batch produced
# it, GET /results/accounts returns one row per live account.
