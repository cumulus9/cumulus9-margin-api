// Cumulus9 - All rights reserved.

'use-strict'

require('dotenv').config()
const cumulus9 = require('./cumulus9.js')

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

cumulus9
    .postPorfolio(portfolioJson)
    .then((r) => {
        console.log(JSON.stringify(r))
    })
    .catch((e) => console.log(e))
