# Cumulus9 Margin API (Python)

Trial the Cumulus9 Margin API with Python 3

## How it works (TL;DR)

Python 3 Package Requirements: `requests`, `base64` and `pandas`

Open `example.py` and update the API credentials received after emailing support@cumulus9.com.

You can then run `example.py` to test the Cumulus Margin API.

You can change `example.py` and adapt it to your workflow.

## Details

You can post the portfolio in either verbose or minified format.

Note that the `position_id` has to be an integer identifier, e.g. row index.

Portfolio verbose format:

```python
portfolioJson = [
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
```
