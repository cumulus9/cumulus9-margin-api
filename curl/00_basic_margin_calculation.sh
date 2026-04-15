#!/usr/bin/env bash
# Cumulus9 - All rights reserved.
# Basic synchronous margin calculation for an ETD portfolio using cURL.

set -euo pipefail

# Credentials -- contact support@cumulus9.com to obtain these.
# Export C9_API_ENDPOINT and C9_API_SECRET as environment variables, or edit below.
C9_API_ENDPOINT="${C9_API_ENDPOINT:-xxxxxxxxxxxxxxxxxx}"
C9_API_SECRET="${C9_API_SECRET:-sk-xxxxxxxxxxxxxxxxxx}"

curl -s -X POST "${C9_API_ENDPOINT}/portfolios" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${C9_API_SECRET}" \
  -d '{
    "vendor_symbology": "clearing",
    "calculation_type": "margins",
    "portfolio": [
        {
            "account_code": "Account 001",
            "exchange_code": "ASX",
            "contract_code": "XT",
            "contract_type": "F",
            "contract_expiry": "DEC-25",
            "contract_strike": "",
            "net_position": "500",
            "account_type": "H"
        },
        {
            "account_code": "Account 001",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "Future",
            "contract_expiry": "DEC-25",
            "contract_strike": "",
            "net_position": "500",
            "account_type": "H"
        },
        {
            "account_code": "Account 001",
            "exchange_code": "NYMEX",
            "contract_code": "LO",
            "contract_type": "CALL",
            "contract_expiry": "202512",
            "contract_strike": "50.1",
            "net_position": "-1000",
            "account_type": "H"
        },
        {
            "account_code": "Account 002",
            "exchange_code": "EUREX",
            "contract_code": "FDAX",
            "contract_type": "FUT",
            "contract_expiry": "202612",
            "contract_strike": "",
            "net_position": "-50",
            "account_type": "H"
        }
    ]
}' | jq .
