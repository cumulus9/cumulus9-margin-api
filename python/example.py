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
portfolio_payload = [
    {
        "position_id": "1",
        "account_code": "Company ABC",
        "exchange_code": "NYMEX",
        "contract_code": "LO",
        "contract_type": "CALL",
        "contract_expiry": "202312",
        "contract_strike": "50",
        "net_position": "1000",
    },
    {
        "position_id": "2",
        "account_code": "Company ABC",
        "exchange_code": "EUREX",
        "contract_code": "FDAX",
        "contract_type": "FUT",
        "contract_expiry": "202312",
        "contract_strike": "",
        "net_position": "-50",
    },
    {
        "position_id": "3",
        "account_code": "Company ABC",
        "exchange_code": "ICE.EU",
        "contract_code": "B",
        "contract_type": "CALL",
        "contract_expiry": "202312",
        "contract_strike": "50",
        "net_position": "1000",
    },
    {
        "position_id": "4",
        "account_code": "Company EFG",
        "exchange_code": "ICE.IFLL",
        "contract_code": "I",
        "contract_type": "FUT",
        "contract_expiry": "202312",
        "contract_strike": "",
        "net_position": "-112",
    },
    {
        "position_id": "5",
        "account_code": "Company EFG",
        "exchange_code": "CME",
        "contract_code": "SR3",
        "contract_type": "FUT",
        "contract_expiry": "202309",
        "contract_strike": "",
        "net_position": "-100",
    },
    {
        "position_id": "6",
        "account_code": "Company EFG",
        "exchange_code": "ICE.IFLL",
        "contract_code": "I",
        "contract_type": "FUT",
        "contract_expiry": "202309",
        "contract_strike": "",
        "net_position": "-2256",
    },
]

# post portfolio and receive the margin results in json format
# you should inspect this json to retrieve a drilldown of the margin calculations and margin offsets applied
results_json = cumulus9.postPorfolio(portfolio_payload).json()

# extract the margin figure from results_json
results = []
for acct in results_json:
    results.append([acct, results_json[acct]["initial_margin"], results_json[acct]["option_liquidation_value"]])

# transform results into a dataframe for better visualization
results_df = pandas.DataFrame(
    results,
    columns=["Account", "Initial Margin USD", "Option Liquidation Value USD"],
)

print(results_df)

# extract the margin figure at ccp level from results_json
results_by_ccp = []
for acct in results_json:
    for ccp in results_json[acct]["margin_by_ccp"]:
        results_by_ccp.append(
            [
                acct,
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


# extract the span margin drilldown from results_json
results_by_span = []
for acct in results_json:
    for ccp in results_json[acct]["margin_by_span"]:
        results_by_span.append(
            [
                acct,
                ccp["clearing_org"],
                ccp["exchange"],
                ccp["cc_code"],
                ccp["currency_code"],
                ccp["fxrate"],
                ccp["initial_margin"],
                ccp["scanning_risk"],
                ccp["intra_spread_charge"],
                ccp["short_option_charge"],
                ccp["intercontract_credit"],
                ccp["strategy_spread_charge"],
                ccp["prompt_date_charge"],
                ccp["option_liquidation_value"],
                ccp["scenario"],
            ]
        )

# transform results_by_ccp into a dataframe for better visualization
results_by_span_df = pandas.DataFrame(
    results_by_span,
    columns=[
        "Account",
        "CCP",
        "Exchange",
        "CC Code",
        "Currency",
        "FX Rate USD",
        "Initial Margin",
        "Scanning Margin",
        "Intra Spread Charge",
        "Short Option Charge",
        "Intercontract Credit",
        "Strategy Spread Charge",
        "Prompt Date Charge",
        "Option Liquidation Value",
        "SPAN Scenario",
    ],
)

print(results_by_ccp_df)

# extract the margin exceptions from results_json
exceptions = []
for acct in results_json:
    if results_json[acct]["exceptions"]:
        for exception in results_json[acct]["exceptions"]:
            exceptions.append([acct, exception])

# transform exceptions into a dataframe for better visualization
exceptions_df = pandas.DataFrame(
    exceptions,
    columns=["Account", "Exception"],
)

print(exceptions_df)
