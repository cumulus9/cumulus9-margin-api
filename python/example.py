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
portfolioJson = [
    {
        "position_id": "0",
        "account_code": "Company ABC",
        "exchange_code": "CME",
        "contract_code": "ED",
        "contract_type": "FUT",
        "contract_expiry": "202212",
        "contract_strike": "",
        "net_position": "10000",
    },
    {
        "position_id": "1",
        "account_code": "Company ABC",
        "exchange_code": "CME",
        "contract_code": "SR3",
        "contract_type": "FUT",
        "contract_expiry": "202212",
        "contract_strike": "",
        "net_position": "-10000",
    },
    {
        "position_id": "2",
        "account_code": "Company ABC",
        "exchange_code": "ICE.IFLL",
        "contract_code": "I",
        "contract_type": "FUT",
        "contract_expiry": "202212",
        "contract_strike": "",
        "net_position": "-2256",
    },
]

# portfolio in minified format (alternative, the API accepts portfolios in both formats)
# portfolioJson = [
#     ["0", "Company ABC", "CME", "ED", "FUT", "202212", "", "10000"],
#     ["1", "Company ABC", "CME", "SR3", "FUT", "202212", "", "-10000"],
#     ["2", "Company ABC", "ICE.IFLL", "I", "FUT", "202212", "", "-2256"],
# ]

# post portfolio and receive the margin results in json format
# you should inspect this json to retrieve a drilldown of the margin calculations and margin offsets applied
results_json = cumulus9.postPorfolio(portfolioJson).json()

# extract the margin figure from the results in json format
results = []
for acct in results_json:
    results.append([acct, results_json[acct]["results"]["initialMarginUSD"]])

# extract the margin figure at ccp level from the results in json format
results_by_ccp = []
exceptions = []
for acct in results_json:
    for ccp in results_json[acct]["results"]["marginDetails"]:
        results_by_ccp.append(
            [
                acct,
                ccp["clearingOrg"],
                ccp["currencyCode"],
                ccp["initialMargin"],
            ]
        )
    # also extract the margin exceptions, if any
    if results_json[acct]["exceptions"] is not None:
        for exc in results_json[acct]["exceptions"]:
            exceptions.append(
                [
                    acct,
                    exc["marginType"],
                    exc["positionId"],
                    exc["errorFields"],
                    exc["closestMatch"],
                    exc["closestMatchUsed"],
                ]
            )

# transform results into a dataframe for better visualization
results_df = pandas.DataFrame(
    results,
    columns=["Account", "Initial Margin USD"],
)

# transform results into a dataframe for better visualization
results_by_ccp_df = pandas.DataFrame(
    results_by_ccp,
    columns=["Account", "Exchange", "Currency", "Initial Margin"],
)

# transform results into a dataframe for better visualization
exceptions_df = pandas.DataFrame(
    exceptions,
    columns=[
        "Account",
        "Margin Type",
        "Position ID",
        "Error",
        "Closest Match",
        "Closest Match",
    ],
)

print(results_df)
# print(results_by_ccp_df)
# print(exceptions_df)