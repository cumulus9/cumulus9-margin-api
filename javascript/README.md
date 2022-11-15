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
        "status": "done",
        "initial_margin": 15503342,
        "option_liquidation_value": 13378080,
        "margin_by_ccp": [
            {
                "fxrate": 1,
                "clearing_org": "CME",
                "currency_code": "USD",
                "initial_margin": 13288944,
                "option_liquidation_value": 13378080
            },
            {
                "fxrate": 0.96581031450278,
                "clearing_org": "ICE",
                "currency_code": "EUR",
                "initial_margin": 2138688,
                "option_liquidation_value": 0
            }
        ],
        "margin_by_span": [
            {
                "fxrate": 1,
                "cc_code": "ED",
                "exchange": "CME",
                "scenario": 1,
                "clearing_org": "CME",
                "currency_code": "USD",
                "scanning_risk": 0,
                "initial_margin": 0,
                "prompt_date_charge": 0,
                "intra_spread_charge": 0,
                "short_option_charge": 0,
                "intercontract_credit": 0,
                "strategy_spread_charge": 0,
                "option_liquidation_value": 0
            },
            {
                "fxrate": 1,
                "cc_code": "SR3",
                "exchange": "CME",
                "scenario": 11,
                "clearing_org": "CME",
                "currency_code": "USD",
                "scanning_risk": 150000,
                "initial_margin": 150000,
                "prompt_date_charge": 0,
                "intra_spread_charge": 0,
                "short_option_charge": 0,
                "intercontract_credit": 0,
                "strategy_spread_charge": 0,
                "option_liquidation_value": 0
            },
            {
                "fxrate": 1,
                "cc_code": "NY-CL",
                "exchange": "NYM",
                "scenario": 14,
                "clearing_org": "CME",
                "currency_code": "USD",
                "scanning_risk": 13138944,
                "initial_margin": 13138944,
                "prompt_date_charge": 0,
                "intra_spread_charge": 0,
                "short_option_charge": 0,
                "intercontract_credit": 0,
                "strategy_spread_charge": 0,
                "option_liquidation_value": 13378080
            },
            {
                "fxrate": 0.96581031450278,
                "cc_code": "I",
                "exchange": "L",
                "scenario": 11,
                "clearing_org": "ICE",
                "currency_code": "EUR",
                "scanning_risk": 2138688,
                "initial_margin": 2138688,
                "prompt_date_charge": 0,
                "intra_spread_charge": 0,
                "short_option_charge": 0,
                "intercontract_credit": 0,
                "strategy_spread_charge": 0,
                "option_liquidation_value": 0
            }
        ],
        "exceptions": null
    }
}
```
