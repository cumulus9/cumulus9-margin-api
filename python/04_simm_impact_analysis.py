# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.


import base64
import requests
import time

# please contact support@cumulus9.com to receive the below credentials
c9_api_endpoint = "xxxxxxxxxxxxxxxxxx"
c9_api_auth_endpoint = "xxxxxxxxxxxxxxxxxx"
c9_api_client_id = "xxxxxxxxxxxxxxxxxx"
c9_api_client_secret = "xxxxxxxxxxxxxxxxxx"

# you can update the following variables to test different versions and holding periods
new_version = "2_7"
old_version = "2_6"
holding_period = 10

# -----------------------------------------------------------------------------
# REST API functions to retrieve the Cumulus9 access token and post
# -----------------------------------------------------------------------------


def get_access_token(api_credentials):
    basic_authorization_bytes = (api_credentials["client_id"] + ":" + api_credentials["client_secret"]).encode("ascii")
    basic_authorization_base64 = base64.b64encode(basic_authorization_bytes)
    headers = {
        "Authorization": "Basic " + basic_authorization_base64.decode("utf-8"),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = "grant_type=client_credentials&scope=riskcalc%2Fget"
    return requests.post(api_credentials["auth_endpoint"], headers=headers, data=data)


def post(url, data, api_credentials):
    try:
        auth = get_access_token(api_credentials)
        if auth.status_code == 200:
            access_token = auth.json()["access_token"]
            headers = {"Content-Type": "application/json", "Authorization": "Bearer " + access_token}
            return requests.post(api_credentials["endpoint"] + url, headers=headers, json=data)
        else:
            raise ValueError("HTTP", auth.status_code, "-", auth.reason)
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

# create credentials dictionary
api_credentials = {
    "endpoint": c9_api_endpoint,
    "auth_endpoint": c9_api_auth_endpoint,
    "client_id": c9_api_client_id,
    "client_secret": c9_api_client_secret,
}

# calculate new_version margin
portfolio_payload["simm_metrics"] = {"version": new_version, "holding_period": 10}
response = post("/portfolios", portfolio_payload, api_credentials)
new_version_margin = round(response.json()["data"][0]["initial_margin"])

# calculate old_version margin
portfolio_payload["simm_metrics"] = {"version": old_version, "holding_period": 10}
response = post("/portfolios", portfolio_payload, api_credentials)
old_version_margin = round(response.json()["data"][0]["initial_margin"])

margin_impact = new_version_margin - old_version_margin

print(f"SIMM Margin v{new_version.replace('_', '.'):<{5}} | ${new_version_margin:,}")
print(f"SIMM Margin v{old_version.replace('_', '.'):<{5}} | ${old_version_margin:,}")
print(f"{'SIMM Margin Impact':<{8}} | ${margin_impact:,}")

runtime = round(time.time() - start_time, 2)
print(f"Completed in {runtime} seconds")
