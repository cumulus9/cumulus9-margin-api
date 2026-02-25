# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.

from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()

# please contact support@cumulus9.com to receive the below credentials
c9_api_endpoint = os.getenv("C9_API_ENDPOINT")
c9_api_secret = os.getenv("C9_API_SECRET")

# you can update the following variables to test different versions and holding periods
new_version = "2_7"
old_version = "2_6"
holding_period = 10

# -----------------------------------------------------------------------------
# REST API function to post
# -----------------------------------------------------------------------------


def post(url, data):
    try:
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + c9_api_secret}
        return requests.post(c9_api_endpoint + url, headers=headers, json=data)
    except Exception as error:
        raise ValueError("Cumulus9 API - " + str(error)) from error


# -----------------------------------------------------------------------------
# create portfolio payload
# -----------------------------------------------------------------------------

portfolio_payload = {
    "calculation_type": "simm",
    "use_closest_match": "true",
    "execution_mode": "sync",
    "portfolio": [
        {
            "account_code": "Account ABC",
            "product_class": "RatesFX",
            "risk_type": "Risk_IRCurve",
            "qualifier": "JPY",
            "bucket": "1",
            "label1": "15Y",
            "label2": "OIS",
            "amount_usd": 10000000,
        },
        {
            "account_code": "Account ABC",
            "product_class": "RatesFX",
            "risk_type": "Risk_IRCurve",
            "qualifier": "JPY",
            "bucket": "1",
            "label1": "30Y",
            "label2": "OIS",
            "amount_usd": -100000,
        },
    ],
}

# -----------------------------------------------------------------------------
# SEND PORTFOLIO_PAYLOAD TO API
# -----------------------------------------------------------------------------

start_time = time.time()

# calculate new_version margin
portfolio_payload["simm_metrics"] = {"version": new_version, "holding_period": 10}
response = post("/portfolios", portfolio_payload)
new_version_margin = round(response.json()["data"][0]["initial_margin"])

# calculate old_version margin
portfolio_payload["simm_metrics"] = {"version": old_version, "holding_period": 10}
response = post("/portfolios", portfolio_payload)
old_version_margin = round(response.json()["data"][0]["initial_margin"])

margin_impact = new_version_margin - old_version_margin

print(f"SIMM Margin v{new_version.replace('_', '.'):<{5}} | ${new_version_margin:,}")
print(f"SIMM Margin v{old_version.replace('_', '.'):<{5}} | ${old_version_margin:,}")
print(f"{'SIMM Margin Impact':<{8}} | ${margin_impact:,}")

runtime = round(time.time() - start_time, 2)
print(f"Completed in {runtime} seconds")
