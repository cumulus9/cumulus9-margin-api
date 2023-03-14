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

Note that the `position_id` has to be an integer identifier, e.g. row index.

Portfolio verbose format:

```javascript
// portfolio in verbose format
const portfolio_payload = {
    vendor_symbology: 'clearing',
    access_level: 'public',
    portfolio: [
        {
            position_id: '1',
            account_code: 'Company ABC',
            exchange_code: 'NYMEX',
            contract_code: 'LO',
            contract_type: 'CALL',
            contract_expiry: '202312',
            contract_strike: '50',
            net_position: '1000',
        },
        {
            position_id: '2',
            account_code: 'Company ABC',
            exchange_code: 'EUREX',
            contract_code: 'FDAX',
            contract_type: 'FUT',
            contract_expiry: '202312',
            contract_strike: '',
            net_position: '-50',
        },
        {
            position_id: '3',
            account_code: 'Company ABC',
            exchange_code: 'ICE.EU',
            contract_code: 'B',
            contract_type: 'CALL',
            contract_expiry: '202312',
            contract_strike: '50',
            net_position: '1000',
        },
        {
            position_id: '4',
            account_code: 'Company EFG',
            exchange_code: 'ICE.IFLL',
            contract_code: 'I',
            contract_type: 'FUT',
            contract_expiry: '202312',
            contract_strike: '',
            net_position: '-112',
        },
        {
            position_id: '5',
            account_code: 'Company EFG',
            exchange_code: 'CME',
            contract_code: 'SR3',
            contract_type: 'FUT',
            contract_expiry: '202309',
            contract_strike: '',
            net_position: '-100',
        },
        {
            position_id: '6',
            account_code: 'Company EFG',
            exchange_code: 'ICE.IFLL',
            contract_code: 'I',
            contract_type: 'FUT',
            contract_expiry: '202309',
            contract_strike: '',
            net_position: '-2256',
        },
    ],
}
```
