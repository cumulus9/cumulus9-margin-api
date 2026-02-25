#!/bin/zsh

# Cumulus9 - All rights reserved.

# please contact support@cumulus9.com to receive the below credentials
c9_api_endpoint="xxxxxxxxxxxxxxxxxx"
c9_api_secret="xxxxxxxxxxxxxxxxxx"

# example of portfolio payload
portfolio_payload='
{
    "vendor_symbology": "clearing",
    "calculation_type": "margins",
    "execution_mode": "sync",
    "portfolio": [
        {
            "account_code": "Account 001",
            "exchange_code": "ASX",
            "contract_code": "XT",
            "contract_type": "F",
            "contract_expiry": "DEC-25",
            "contract_strike": "",
            "net_position": "500"
        },
        {
            "account_code": "Account 001",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "Future",
            "contract_expiry": "DEC-25",
            "contract_strike": "",
            "net_position": "500"
        },
        {
            "account_code": "Account 001",
            "exchange_code": "NYMEX",
            "contract_code": "LO",
            "contract_type": "CALL",
            "contract_expiry": "202512",
            "contract_strike": "50.1",
            "net_position": "-1000"
        },
        {
            "account_code": "Account 002",
            "exchange_code": "EUREX",
            "contract_code": "FDAX",
            "contract_type": "FUT",
            "contract_expiry": "202612",
            "contract_strike": "",
            "net_position": "-50"
        }
    ]
}'

# post portfolio
headers=("Content-Type: application/json" "Authorization: Bearer $c9_api_secret")
response=$(curl -s -X POST "$c9_api_endpoint/portfolios" -H "${headers[1]}" -H "${headers[2]}" -d "$portfolio_payload" | jq)

echo $response

# response:
# {
#   "request_id": "90938bba-02b3-42bf-a22e-f4c0ad6ebc61",
#   "data": [
#     {
#       "request_id": "90938bba-02b3-42bf-a22e-f4c0ad6ebc61",
#       "portfolio_id": "13fcacf076f925f0309e70bb2929b4a3",
#       "submitted_time": "2023-08-24T15:44:43.801589",
#       "account_code": "Account 001",
#       "status": "done",
#       "access_level": null,
#       "initial_margin": 5801138,
#       "option_liquidation_value": -24530000,
#       "value_at_risk": 0,
#       "stress_loss": 0,
#       "additional_margin": 0,
#       "margin_by_ccp": [
#         {
#           "clearing_org": "CME",
#           "currency_code": "USD",
#           "fxrate": 1,
#           "initial_margin": 3190000,
#           "option_liquidation_value": -24530000
#         },
#         {
#           "clearing_org": "ASXCLF",
#           "currency_code": "AUD",
#           "fxrate": 1.564,
#           "initial_margin": 1925500,
#           "option_liquidation_value": 0
#         },
#         {
#           "clearing_org": "ICE",
#           "currency_code": "USD",
#           "fxrate": 1,
#           "initial_margin": 1380000,
#           "option_liquidation_value": 0
#         }
#       ],
#       "margin_by_span": [
#         {
#           "clearing_org": "ASXCLF",
#           "exchange": "SFE",
#           "cc_code": "XT",
#           "currency_code": "AUD",
#           "fxrate": 1.564,
#           "initial_margin": 1925500,
#           "intercontract_credit": 0,
#           "intra_spread_charge": 0,
#           "prompt_date_charge": 0,
#           "scanning_risk": 1925500,
#           "scenario": 13,
#           "short_option_charge": 0,
#           "strategy_spread_charge": 0,
#           "option_liquidation_value": 0
#         },
#         {
#           "clearing_org": "CME",
#           "exchange": "NYM",
#           "cc_code": "NY-CL",
#           "currency_code": "USD",
#           "fxrate": 1,
#           "initial_margin": 3190000,
#           "intercontract_credit": 0,
#           "intra_spread_charge": 0,
#           "prompt_date_charge": 0,
#           "scanning_risk": 3190000,
#           "scenario": 11,
#           "short_option_charge": 30000,
#           "strategy_spread_charge": 0,
#           "option_liquidation_value": -24530000
#         },
#         {
#           "clearing_org": "ICE",
#           "exchange": "I",
#           "cc_code": "BRN",
#           "currency_code": "USD",
#           "fxrate": 1,
#           "initial_margin": 1380000,
#           "intercontract_credit": 0,
#           "intra_spread_charge": 0,
#           "prompt_date_charge": 0,
#           "scanning_risk": 1380000,
#           "scenario": 13,
#           "short_option_charge": 0,
#           "strategy_spread_charge": 0,
#           "option_liquidation_value": 0
#         }
#       ],
#       "margin_by_eurexpme": null,
#       "margin_by_eurexpme_drilldown": null,
#       "margin_by_occ_tims": null,
#       "additional_margin_details": null,
#       "exceptions": null
#     },
#     {
#       "request_id": "90938bba-02b3-42bf-a22e-f4c0ad6ebc61",
#       "portfolio_id": "910d938911f13d8c347fdba1e3dcc5d5",
#       "submitted_time": "2023-08-24T15:44:43.801589",
#       "account_code": "Account 002",
#       "status": "done",
#       "access_level": null,
#       "initial_margin": 1702552,
#       "option_liquidation_value": 0,
#       "value_at_risk": 0,
#       "stress_loss": 0,
#       "additional_margin": 0,
#       "margin_by_ccp": [
#         {
#           "clearing_org": "EUREX_P",
#           "currency_code": "EUR",
#           "fxrate": 0.9186,
#           "initial_margin": 1563964.71,
#           "option_liquidation_value": 0
#         }
#       ],
#       "margin_by_span": null,
#       "margin_by_eurexpme": [
#         {
#           "request_id": "90938bba-02b3-42bf-a22e-f4c0ad6ebc61",
#           "portfolio_id": "910d938911f13d8c347fdba1e3dcc5d5",
#           "result_type": "eurexpme",
#           "clearing_org": "EUREX_P",
#           "currency_code": "EUR",
#           "fxrate": 0.9186,
#           "liquidation_group": "PEQ01",
#           "liquidation_group_split": "PEQ01_HP3",
#           "initial_margin": 1563964.71,
#           "market_risk": 1562520.08,
#           "liquidity_addon": 1444.63,
#           "long_option_credit": 0,
#           "time_to_expiry_adjustment": 0,
#           "premium_margin": 0,
#           "drilldowns": [
#             {
#               "iid": 62518917,
#               "line_no": 3,
#               "maturity": 202606,
#               "product_id": "FDAX",
#               "call_put_flag": "",
#               "contract_date": 20260619,
#               "exercise_price": 0,
#               "net_ls_balance": -50,
#               "premium_margin": 0,
#               "version_number": "0",
#               "component_margin": 1563964.7094382464,
#               "liquidation_group": "PEQ01",
#               "liquidation_group_split": "PEQ01_HP3",
#               "premium_margin_currency": "EUR",
#               "component_margin_currency": "EUR"
#             }
#           ]
#         }
#       ],
#       "margin_by_eurexpme_drilldown": [
#         {
#           "request_id": "90938bba-02b3-42bf-a22e-f4c0ad6ebc61",
#           "portfolio_id": "910d938911f13d8c347fdba1e3dcc5d5",
#           "result_type": "eurexpme",
#           "clearing_org": "EUREX_P",
#           "currency": "EUR",
#           "fxrate": 0.9186,
#           "liquidation_group": "PEQ01",
#           "liquidation_group_split": "PEQ01_HP3",
#           "product_id": "FDAX",
#           "maturity": "202606",
#           "contract_date": "20260619",
#           "call_put_flag": "",
#           "exercise_price": "0",
#           "net_ls_balance": "-50",
#           "premium_margin": 0,
#           "component_margin": 1563964.71
#         }
#       ],
#       "margin_by_occ_tims": null,
#       "additional_margin_details": null,
#       "exceptions": null
#     }
#   ]
# }
