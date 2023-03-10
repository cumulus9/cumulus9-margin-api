// Cumulus9 - All rights reserved.

'use-strict'

require('dotenv').config()
const cumulus9 = require('./cumulus9.js')

const payload = {
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

cumulus9
    .postPorfolio(payload)
    .then((r) => {
        console.log(JSON.stringify(r))
    })
    .catch((e) => console.log(e))
