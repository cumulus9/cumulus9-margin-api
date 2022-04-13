# Cumulus9 Margin API (Python)

Trial the Cumulus9 Margin API with Python 3

## How it works (TL;DR)

Python 3 Package Requirements: `requests`, `base64` and `pandas`

Open `example.py` and update the API credentials received after emailing support@cumulus9.com.

You can then run `example.py` to test the Cumulus Margin API.

You can change `example.py` and adapt it to your workflow.

## Details

You can post the portfolio in either verbose or minified format.

Note that the `position_id` has to be a unique identifier, e.g. row index.

Portfolio verbose format:

```python
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
```

Portfolio minified format:

```python
portfolioJson = [
    ["0", "Company ABC", "CME", "ED", "FUT", "202212", "", "10000"],
    ["1", "Company ABC", "CME", "SR3", "FUT", "202212", "", "-10000"],
    ["2", "Company ABC", "ICE.IFLL", "I", "FUT", "202212", "", "-2256"],
]
```

Response example:

```json
{
    "Company ABC": {
        "results": {
            "marginDetails": [
                {
                    "fxRateUsd": 0.9170946439356291,
                    "marginType": "span",
                    "clearingOrg": "ICE",
                    "currencyCode": "EUR",
                    "marginStatus": "done",
                    "initialMargin": 1290996,
                    "marginDetails": [
                        {
                            "ccCode": "I",
                            "exchange": "L",
                            "scenario": "11",
                            "currencyCode": "EUR",
                            "scanningRisk": "1290996",
                            "initialMargin": "1290996",
                            "promptDateCharge": "0",
                            "intraSpreadCharge": "0",
                            "shortOptionCharge": "0",
                            "intercontractCredit": "0",
                            "strategySpreadCharges": "0",
                            "optionLiquidationValue": "0"
                        }
                    ],
                    "optionLiquidationValue": 0
                },
                {
                    "fxRateUsd": 1,
                    "marginType": "span",
                    "clearingOrg": "CME",
                    "currencyCode": "USD",
                    "marginStatus": "done",
                    "initialMargin": 4875000,
                    "marginDetails": [
                        {
                            "ccCode": "ED",
                            "exchange": "CME",
                            "scenario": "13",
                            "currencyCode": "USD",
                            "scanningRisk": "7750000",
                            "initialMargin": "2437500",
                            "promptDateCharge": "0",
                            "intraSpreadCharge": "0",
                            "shortOptionCharge": "0",
                            "intercontractCredit": "5312500",
                            "strategySpreadCharges": "0",
                            "optionLiquidationValue": "0"
                        },
                        {
                            "ccCode": "SR3",
                            "exchange": "CME",
                            "scenario": "11",
                            "currencyCode": "USD",
                            "scanningRisk": "7750000",
                            "initialMargin": "2437500",
                            "promptDateCharge": "0",
                            "intraSpreadCharge": "0",
                            "shortOptionCharge": "0",
                            "intercontractCredit": "5312500",
                            "strategySpreadCharges": "0",
                            "optionLiquidationValue": "0"
                        }
                    ],
                    "optionLiquidationValue": 0
                }
            ],
            "initialMarginUSD": 6282702
        },
        "exceptions": null
    }
}
```
