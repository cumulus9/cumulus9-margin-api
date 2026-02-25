# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.

import datetime
import json
import os
import pandas
import requests
from dotenv import load_dotenv

"""
A proof-of-concept that can be used to estimate changes in portfolio margin as contracts near their maturity date.
This method involves decreasing the 'contract_expiry' value by a certain number of days and then recalculating the portfolio margin.
You can use this as a basis to develop a more sophisticated margin ageing process.
"""

load_dotenv()

# please contact support@cumulus9.com to receive the below credentials
c9_api_endpoint = os.getenv("C9_API_ENDPOINT")
c9_api_secret = os.getenv("C9_API_SECRET")

# -----------------------------------------------------------------------------
# REST API function to post portfolio
# -----------------------------------------------------------------------------


def post(url, data):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + c9_api_secret,
        }
        return requests.post(
            c9_api_endpoint + url,
            headers=headers,
            json=data,
        )
    except Exception as error:
        raise ValueError("Cumulus9 API - " + str(error)) from error


# -----------------------------------------------------------------------------
# Create the portfolio payload and post it to Cumulus9 API
# -----------------------------------------------------------------------------

# read sample portfolio ./sample_portfolio.csv
df_portfolio = pandas.read_csv("./sample_portfolio.csv", dtype=str, na_filter=False)


# function for adjusting a date by a specified offset of days
def get_date_offset(input_date, offset):
    # add day to input_date if missing, e.g. for monthly expiries
    if len(input_date) == 6 or input_date[-2:] == "00":
        input_date = input_date[0:6] + "28"
    input_date_obj = datetime.datetime.strptime(input_date, "%Y%m%d").date()
    input_date_obj_with_offset = input_date_obj + datetime.timedelta(days=offset)
    return input_date_obj_with_offset.strftime("%Y%m%d")


# function to check if a contract_expiry is expiried
def is_expired(contract_expiry):
    # add day to contract_expiry if missing, e.g. for monthly expiries
    if len(contract_expiry) == 6 or contract_expiry[-2:] == "00":
        contract_expiry = contract_expiry[0:6] + "28"
    contract_expiry_obj = datetime.datetime.strptime(contract_expiry, "%Y%m%d").date()
    today = datetime.datetime.today().date()
    return today > contract_expiry_obj


# function to age a portfolio by decrementing the 'contract_expiry' value by a specified number of days
def age_portfolio(df_portfolio, days):
    df_portfolio_aged = df_portfolio.copy()
    # decrement the 'contract_expiry' value by the specified number of days
    df_portfolio_aged["contract_expiry"] = df_portfolio_aged["contract_expiry"].apply(
        lambda x: get_date_offset(str(x), -days)
    )
    # create 'is_expired' to mark expired contracts
    df_portfolio_aged["is_expired"] = df_portfolio_aged["contract_expiry"].apply(lambda x: is_expired(str(x)))
    # drop expired contracts
    df_portfolio_aged = df_portfolio_aged[df_portfolio_aged["is_expired"] is False]
    # drop the 'is_expired' column
    df_portfolio_aged = df_portfolio_aged.drop(columns=["is_expired"])
    return df_portfolio_aged


# calculate portfolio margin for given portfolio
def calculate_portfolio_margin(df_portfolio):
    # create portfolio payload
    portfolio_payload = {
        "vendor_symbology": "clearing",
        "calculation_type": "margins",
        "execution_mode": "sync",
        "portfolio": json.loads(df_portfolio.to_json(orient="records")),
    }
    # post portfolio and receive the margin results in json format
    results_json = post("/portfolios", portfolio_payload).json()
    # sum the initial margin for all portfolios
    total_margin = 0
    for i in results_json["data"]:
        total_margin += i["initial_margin"]
    # return the total margin
    return total_margin


# margin for the original portfolio
margin_portfolio = calculate_portfolio_margin(df_portfolio)

# portfolio aged by 30 days
df_portfolio_30d = age_portfolio(df_portfolio, 30)
df_portfolio_30d["account_code"] = df_portfolio_30d["account_code"] + "_aged_by_30d"
margin_portfolio_30d = calculate_portfolio_margin(df_portfolio_30d)

# portfolio aged by 90 days
df_portfolio_90d = age_portfolio(df_portfolio, 90)
df_portfolio_90d["account_code"] = df_portfolio_90d["account_code"] + "_aged_by_90d"
margin_portfolio_90d = calculate_portfolio_margin(df_portfolio_90d)

# portfolio aged by 120 days
df_portfolio_120d = age_portfolio(df_portfolio, 120)
df_portfolio_120d["account_code"] = df_portfolio_120d["account_code"] + "_aged_by_120d"
margin_portfolio_120d = calculate_portfolio_margin(df_portfolio_120d)

# basic report for priting to console
margin_report = f"""
now:\t${margin_portfolio:,}
30d:\t${margin_portfolio_30d:,}
90d:\t${margin_portfolio_90d:,}
120d:\t${margin_portfolio_120d:,}
"""

print(margin_report)
# now:	$148,716,004
# 30d:	$125,466,092
# 90d:	$89,294,688
# 120d:	$117,910,106
