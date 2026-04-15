# Cumulus9 - All rights reserved.
# Check engine health and list available margin parameters.

import json
import requests

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = "xxxxxxxxxxxxxxxxxx"
C9_API_SECRET = "sk-xxxxxxxxxxxxxxxxxx"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {C9_API_SECRET}",
}

response = requests.get(f"{C9_API_ENDPOINT}/healthcheck/analytics-engine", headers=HEADERS)
response.raise_for_status()

engines = response.json()

for engine in engines:
    status = engine.get("status", "UNKNOWN")
    service = engine.get("service", "?")
    version = engine.get("version", "?")
    print(f"  {service:<20} v{version:<10} {status}")

# Full response:
print(json.dumps(engines, indent=2))
