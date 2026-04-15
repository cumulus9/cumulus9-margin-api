#!/usr/bin/env bash
# Cumulus9 - All rights reserved.
# Batch processing: submit a portfolio for background calculation and poll for completion.

set -euo pipefail

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT="${C9_API_ENDPOINT:-xxxxxxxxxxxxxxxxxx}"
C9_API_SECRET="${C9_API_SECRET:-sk-xxxxxxxxxxxxxxxxxx}"

# ---------------------------------------------------------------------------
# Step 1: Submit the batch
# ---------------------------------------------------------------------------
# x-processing-mode options: fifo (default), priority, replace_all

BATCH_RESPONSE=$(curl -s -X POST "${C9_API_ENDPOINT}/portfolios/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${C9_API_SECRET}" \
  -H "x-processing-mode: fifo" \
  -d '{
    "vendor_symbology": "clearing",
    "calculation_type": "margins",
    "portfolio": [
        {
            "account_code": "Account 001",
            "exchange_code": "ASX",
            "contract_code": "XT",
            "contract_type": "F",
            "contract_expiry": "DEC-26",
            "net_position": "500",
            "account_type": "H"
        },
        {
            "account_code": "Account 002",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "FUT",
            "contract_expiry": "202612",
            "net_position": "1000",
            "account_type": "H"
        },
        {
            "account_code": "Account 003",
            "exchange_code": "EUREX",
            "contract_code": "FDAX",
            "contract_type": "FUT",
            "contract_expiry": "202612",
            "net_position": "-50",
            "account_type": "H"
        }
    ]
}')

BATCH_ID=$(echo "$BATCH_RESPONSE" | jq -r '.batch_id')
echo "Batch submitted: ${BATCH_ID}"

# ---------------------------------------------------------------------------
# Step 2: Poll for completion
# ---------------------------------------------------------------------------

while true; do
    STATUS_RESPONSE=$(curl -s "${C9_API_ENDPOINT}/portfolios/batch/${BATCH_ID}" \
      -H "Authorization: Bearer ${C9_API_SECRET}")

    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
    PCT=$(echo "$STATUS_RESPONSE" | jq -r '.completed_pct')
    RUNTIME=$(echo "$STATUS_RESPONSE" | jq -r '.runtime_ms')

    echo "  [${STATUS}] ${PCT}% complete (${RUNTIME}ms elapsed)"

    if [[ "$STATUS" == "completed" || "$STATUS" == "failed" || "$STATUS" == "completed_with_errors" ]]; then
        echo ""
        echo "Batch ${STATUS} in ${RUNTIME}ms"
        break
    fi

    sleep 5
done
