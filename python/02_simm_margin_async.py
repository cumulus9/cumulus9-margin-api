# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.

# This script demonstrates how to submit a portfolio containing multiple accounts in asynchronous mode, enabling the concurrent processing of a large volume of calculations.
# Note: The Cumulus9 API imposes a default limit of 100 calculation requests per minute per user, but this rate can be adjusted for individual users upon request.

import base64
import concurrent.futures
import random
import requests
import time

# please contact support@cumulus9.com to receive the below credentials
c9_api_endpoint = "xxxxxxxxxxxxxxxxxx"
c9_api_auth_endpoint = "xxxxxxxxxxxxxxxxxx"
c9_api_client_id = "xxxxxxxxxxxxxxxxxx"
c9_api_client_secret = "xxxxxxxxxxxxxxxxxx"

# -----------------------------------------------------------------------------
# REST API functions to retrieve the Cumulus9 access token and post portfolio
# -----------------------------------------------------------------------------

# create credentials dictionary
api_credentials = {
    "endpoint": c9_api_endpoint,
    "auth_endpoint": c9_api_auth_endpoint,
    "client_id": c9_api_client_id,
    "client_secret": c9_api_client_secret,
}


def get_access_token():
    basic_authorization_bytes = (api_credentials["client_id"] + ":" + api_credentials["client_secret"]).encode("ascii")
    basic_authorization_base64 = base64.b64encode(basic_authorization_bytes)
    headers = {
        "Authorization": "Basic " + basic_authorization_base64.decode("utf-8"),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = "grant_type=client_credentials&scope=riskcalc%2Fget"
    return requests.post(api_credentials["auth_endpoint"], headers=headers, data=data)


def post(url, data):
    try:
        auth = get_access_token()
        if auth.status_code == 200:
            access_token = auth.json()["access_token"]
            headers = {"Content-Type": "application/json", "Authorization": "Bearer " + access_token}
            return requests.post(api_credentials["endpoint"] + url, headers=headers, json=data)
        else:
            raise ValueError("HTTP", auth.status_code, "-", auth.reason)
    except Exception as error:
        raise ValueError("Cumulus9 API - " + str(error)) from error


def get(url):
    try:
        auth = get_access_token()
        if auth.status_code == 200:
            access_token = auth.json()["access_token"]
            headers = {"Content-Type": "application/json", "Authorization": "Bearer " + access_token}
            return requests.get(api_credentials["endpoint"] + url, headers=headers)
        else:
            raise ValueError("HTTP", auth.status_code, "-", auth.reason)
    except Exception as error:
        raise ValueError("Cumulus9 API - " + str(error)) from error


# -----------------------------------------------------------------------------
# portfolio payload consisting of multiple accounts with random trades
# -----------------------------------------------------------------------------

portfolio = []
for i in range(50):
    portfolio += [
        {
            "account_code": f"portfolio_{i}",
            "product_class": "RatesFX",
            "risk_type": "Risk_IRCurve",
            "qualifier": "JPY",
            "bucket": "1",
            "label1": "15Y",
            "label2": "OIS",
            "amount_usd": random.randint(-10000000, 10000000),
        },
        {
            "account_code": f"portfolio_{i}",
            "product_class": "RatesFX",
            "risk_type": "Risk_IRCurve",
            "qualifier": "JPY",
            "bucket": "1",
            "label1": "30Y",
            "label2": "OIS",
            "amount_usd": random.randint(-10000000, 10000000),
        },
    ]

# break portfolio by account
portfolio_by_account_code = {}
for i in portfolio:
    if i["account_code"] not in portfolio_by_account_code:
        portfolio_by_account_code[i["account_code"]] = []
    portfolio_by_account_code[i["account_code"]].append(i)

# start timer to calculate the time taken to process the requests
start_time = time.time()

# -----------------------------------------------------------------------------
# post requests to the api in async mode - send portfolio
# -----------------------------------------------------------------------------

request_ids = []


# send async calculation request for given account_code
def send_request(account_code):
    portfolio_payload = {
        "calculation_type": "simm",
        "simm_metrics": {"version": "2_6_5", "holding_period": 10},
        "use_closest_match": "true",
        "execution_mode": "async",
        "portfolio": portfolio_by_account_code[account_code],
    }
    response = post("/portfolios", portfolio_payload)
    if response.status_code != 200:
        print(f"ERROR - Failed to process {account_code} {response.status_code} - {response.reason}")
    else:
        post_response = response.json()
        request_ids.append(post_response["request_id"])
        # print(f"INFO - Request {post_response['request_id']} for {account_code} has been sent")


# send requests concurrently
with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(send_request, {i["account_code"] for i in portfolio})

# -----------------------------------------------------------------------------
# get requests to the api in async mode - retrieve results
# -----------------------------------------------------------------------------

completes_count = 0
results = []


# retrieve results for given request_id
def retrieve_results(request_id):
    global completes_count
    try:
        get_response = get("/results?request_id=" + request_id).json()
        if get_response[0]["request_id"] == request_id:
            return get_response, request_id
    except Exception:
        print(f"INFO - {len(request_ids)} still in progressing...")
        return None, request_id


with concurrent.futures.ThreadPoolExecutor() as executor:
    while len(request_ids) > 0:
        future_to_request = {executor.submit(retrieve_results, request_id): request_id for request_id in request_ids}
        for future in concurrent.futures.as_completed(future_to_request):
            result, request_id = future.result()
            if result:
                results += result
                request_ids.remove(request_id)
            else:
                time.sleep(1)


runtime = time.time() - start_time
print(f"INFO - Completed {len(results)} calculation requests in {runtime:.2f} seconds")

# print margin for each account
for i in results:
    print(i["account_code"], i["initial_margin"])

# Response example:

# INFO - Completed 50 calculation requests in 4.27 seconds
# portfolio_31 7301838.230624532
# portfolio_2 469912818.103117
# portfolio_7 151389689.68354484
# portfolio_47 94659182.63841921
# portfolio_24 53711644.072457135
# portfolio_23 178820530.34986588
# portfolio_5 55229561.14187917
# portfolio_32 321820439.07420903
# portfolio_43 174963903.78877634
# portfolio_41 426156672.24238616
# portfolio_20 105547975.43338552
# portfolio_40 172525798.08481967
# portfolio_16 222804771.9016962
# portfolio_37 218499769.13073406
# portfolio_39 270817808.1082067
# portfolio_44 221896500.06314653
# portfolio_42 32352678.005083535
# portfolio_8 229594023.1214126
# portfolio_10 307348072.54272044
# portfolio_3 75363297.26383144
# portfolio_6 53453618.66619651
# portfolio_38 312991264.73289007
# portfolio_25 329974656.91142446
# portfolio_36 128226576.95167807
# portfolio_45 183152456.60792318
# portfolio_48 384951284.4961773
# portfolio_15 180328479.27230865
# portfolio_22 152886343.65330416
# portfolio_4 43098584.521383576
# portfolio_33 141347477.10053322
# portfolio_14 346047144.8345047
# portfolio_1 210136818.6648911
# portfolio_34 44683718.310606875
# portfolio_49 347539509.72470504
# portfolio_9 211510944.4251123
# portfolio_30 130958675.20613052
# portfolio_29 136792597.01763776
# portfolio_12 234491222.1389605
# portfolio_27 38716124.78365793
# portfolio_13 88115469.90352057
# portfolio_17 254276141.92330724
# portfolio_0 248208841.46131626
# portfolio_35 71355463.78612651
# portfolio_28 155917602.34038156
# portfolio_11 132721564.42981203
# portfolio_21 102654623.62781543
# portfolio_46 466136705.7743893
# portfolio_26 90631522.12851015
# portfolio_18 292342323.58610654
# portfolio_19 54351374.38289547
