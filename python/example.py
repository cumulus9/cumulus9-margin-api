# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.

import os
import pandas
import cumulus9

# please contact support@cumulus9.com to receive the below credentials
c9_api_endpoint = "xxxxxxxxxxxxxxxxxx"
c9_api_auth_endpoint = "xxxxxxxxxxxxxxxxxx"
c9_api_client_id = "xxxxxxxxxxxxxxxxxx"
c9_api_client_secret = "xxxxxxxxxxxxxxxxxx"

# store the cumulus9 margin api credential as environment variables
os.environ["C9_API_ENDPOINT"] = c9_api_endpoint
os.environ["C9_API_AUTH_ENDPOINT"] = c9_api_auth_endpoint
os.environ["C9_API_CLIENT_ID"] = c9_api_client_id
os.environ["C9_API_CLIENT_SECRET"] = c9_api_client_secret

# portfolio in verbose format
portfolio_payload = {
    "vendor_symbology": "clearing",
    "access_level": "public",
    "portfolio": [
        {
            "position_id": "1",
            "account_code": "Company ABC",
            "exchange_code": "ICE.EU",
            "contract_code": "BCO",
            "contract_type": "F",
            "contract_expiry": "DEC-23",
            "contract_strike": "",
            "net_position": "500",
        },
        {
            "position_id": "2",
            "account_code": "Company ABC",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "Future",
            "contract_expiry": "DEC-23",
            "contract_strike": "",
            "net_position": "500",
        },
        {
            "position_id": "3",
            "account_code": "Company ABC",
            "exchange_code": "NYMEX",
            "contract_code": "LO",
            "contract_type": "CALL",
            "contract_expiry": "202312",
            "contract_strike": "50.1",
            "net_position": "-1000",
        },
        {
            "position_id": "4",
            "account_code": "Company ABC - Sub Account 001",
            "exchange_code": "EUREX",
            "contract_code": "FDAX",
            "contract_type": "FUT",
            "contract_expiry": "202312",
            "contract_strike": "",
            "net_position": "-50",
        },
    ],
}

# post portfolio and receive the margin results in json format
# you should inspect this json to retrieve a drilldown of the margin calculations and margin offsets applied
results_json = cumulus9.postPorfolio(portfolio_payload).json()

# extract the margin figure from results_json
results = []
for acct in results_json:
    results.append([acct["account_code"], acct["initial_margin"], acct["option_liquidation_value"], acct["value_at_risk"]])

# transform results into a dataframe for better visualization
results_df = pandas.DataFrame(
    results,
    columns=["Account", "Initial Margin USD", "Option Liquidation Value USD", "H-VaR 250d 99pct USD"],
)

print(results_df)

# extract the margin figure at ccp level from results_json
results_by_ccp = []
for acct in results_json:
    for ccp in acct["margin_by_ccp"]:
        results_by_ccp.append(
            [
                acct["account_code"],
                ccp["clearing_org"],
                ccp["currency_code"],
                ccp["fxrate"],
                ccp["initial_margin"],
                ccp["option_liquidation_value"],
            ]
        )

# transform results_by_ccp into a dataframe for better visualization
results_by_ccp_df = pandas.DataFrame(
    results_by_ccp,
    columns=["Account", "CCP", "Currency", "FX Rate USD", "Initial Margin", "Option Liquidation Value"],
)

print(results_by_ccp_df)

# extract the margin exceptions from results_json
exceptions = []
for acct in results_json:
    if acct["exceptions"]:
        for exception in acct["exceptions"]:
            exceptions.append([acct["account_code"], exception])

# transform exceptions into a dataframe for better visualization
exceptions_df = pandas.DataFrame(
    exceptions,
    columns=["Account", "Exception"],
)

print(exceptions_df)
