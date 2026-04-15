// Cumulus9 - All rights reserved.
// Basic synchronous margin calculation for an ETD portfolio.

'use strict'

require('dotenv').config()
const cumulus9 = require('./cumulus9.js')

const payload = {
    vendor_symbology: 'clearing',
    calculation_type: 'margins',
    portfolio: [
        {
            account_code: 'Account 001',
            exchange_code: 'ASX',
            contract_code: 'XT',
            contract_type: 'F',
            contract_expiry: 'DEC-25',
            contract_strike: '',
            net_position: '500',
            account_type: 'H',
        },
        {
            account_code: 'Account 001',
            exchange_code: 'ICE.EU',
            contract_code: 'B',
            contract_type: 'Future',
            contract_expiry: 'DEC-25',
            contract_strike: '',
            net_position: '500',
            account_type: 'H',
        },
        {
            account_code: 'Account 001',
            exchange_code: 'NYMEX',
            contract_code: 'LO',
            contract_type: 'CALL',
            contract_expiry: '202512',
            contract_strike: '50.1',
            net_position: '-1000',
            account_type: 'H',
        },
        {
            account_code: 'Account 002',
            exchange_code: 'EUREX',
            contract_code: 'FDAX',
            contract_type: 'FUT',
            contract_expiry: '202612',
            contract_strike: '',
            net_position: '-50',
            account_type: 'H',
        },
    ],
}

cumulus9
    .postPortfolio(payload)
    .then((results) => {
        for (const account of results.data) {
            console.log(`${account.account_code}: initial_margin = $${account.initial_margin.toLocaleString()}`)
        }
        console.log(JSON.stringify(results, null, 2))
    })
    .catch((err) => {
        console.error('Error:', err.message || err)
        process.exit(1)
    })
