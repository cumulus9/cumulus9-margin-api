# Cumulus9 Margin API (JavaScript)

Trial the Cumulus9 Margin API with JavaScript.

The example provided here uses Node.js.

## How it works (TL;DR)

Create a `.env` file having the same structure as `.env.example` and update the API credentials received after emailing support@cumulus9.com.

Install node modules `npm install`.

You can then run `node example.js` to test the Cumulus Margin API.

You can change `example.js` and adapt it to your workflow.

## Details

You can post the portfolio in either verbose or minified format.

Note that the `position_id` has to be a unique identifier, e.g. row index.

Portfolio verbose format:

```javascript
const portfolioJson = [
    {
        position_id: '0',
        account_code: 'Company ABC',
        exchange_code: 'CME',
        contract_code: 'ED',
        contract_type: 'FUT',
        contract_expiry: '202212',
        contract_strike: '',
        net_position: '10000',
    },
    {
        position_id: '1',
        account_code: 'Company ABC',
        exchange_code: 'CME',
        contract_code: 'SR3',
        contract_type: 'FUT',
        contract_expiry: '202212',
        contract_strike: '',
        net_position: '-10000',
    },
    {
        position_id: '2',
        account_code: 'Company ABC',
        exchange_code: 'ICE.IFLL',
        contract_code: 'I',
        contract_type: 'FUT',
        contract_expiry: '202212',
        contract_strike: '',
        net_position: '-2256',
    },
]
```

Portfolio minified format:

```javascript
const portfolioJson = [
    ['0', 'Company ABC', 'CME', 'ED', 'FUT', '202212', '', '10000'],
    ['1', 'Company ABC', 'CME', 'SR3', 'FUT', '202212', '', '-10000'],
    ['2', 'Company ABC', 'ICE.IFLL', 'I', 'FUT', '202212', '', '-2256'],
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
