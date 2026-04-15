# Cumulus9 - All rights reserved.
# Batch processing: submit a large portfolio for background calculation
# and poll for completion.

import time
import requests

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = "xxxxxxxxxxxxxxxxxx"
C9_API_SECRET = "sk-xxxxxxxxxxxxxxxxxx"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {C9_API_SECRET}",
}

# ---------------------------------------------------------------------------
# Build a large portfolio (multiple accounts)
# ---------------------------------------------------------------------------

portfolio = []
for i in range(200):
    portfolio.append({
        "account_code": f"account_{i:04d}",
        "exchange_code": "ICE.EU",
        "contract_code": "B",
        "contract_type": "FUT",
        "contract_expiry": "202512",
        "net_position": str(100 * (i + 1)),
        "account_type": "H",
    })

payload = {
    "calculation_type": "margins",
    "vendor_symbology": "clearing",
    "portfolio": portfolio,
}

# ---------------------------------------------------------------------------
# Step 1: Submit the batch
# ---------------------------------------------------------------------------
# x-processing-mode options:
#   "fifo"        - First-in, first-out (default)
#   "priority"    - Priority queue promotion
#   "replace_all" - Clear all queued batches for this user before adding

response = requests.post(
    f"{C9_API_ENDPOINT}/portfolios/batch",
    headers={**HEADERS, "x-processing-mode": "fifo"},
    json=payload,
)
response.raise_for_status()

batch_id = response.json()["batch_id"]
print(f"Batch submitted: {batch_id}")

# ---------------------------------------------------------------------------
# Step 2: Poll for completion
# ---------------------------------------------------------------------------

while True:
    status_response = requests.get(
        f"{C9_API_ENDPOINT}/portfolios/batch/{batch_id}",
        headers=HEADERS,
    )
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
