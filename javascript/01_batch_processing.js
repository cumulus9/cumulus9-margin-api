// Cumulus9 - All rights reserved.
// Batch processing: submit a large portfolio for background calculation
// and poll for completion.

'use strict'

require('dotenv').config()
const cumulus9 = require('./cumulus9.js')

// ---------------------------------------------------------------------------
// Build a large portfolio (multiple accounts)
// ---------------------------------------------------------------------------

const portfolio = []
for (let i = 0; i < 200; i++) {
    portfolio.push({
        account_code: `account_${String(i).padStart(4, '0')}`,
        exchange_code: 'ICE.EU',
        contract_code: 'B',
        contract_type: 'FUT',
        contract_expiry: '202512',
        net_position: String(100 * (i + 1)),
        account_type: 'H',
    })
}

const payload = {
    calculation_type: 'margins',
    vendor_symbology: 'clearing',
    portfolio,
}

// ---------------------------------------------------------------------------
// Submit and poll
// ---------------------------------------------------------------------------

async function main() {
    // Step 1: Submit the batch
    // processingMode options: 'fifo' (default), 'priority', 'replace_all'
    const { batch_id } = await cumulus9.submitBatch(payload, 'fifo')
    console.log(`Batch submitted: ${batch_id}`)

    // Step 2: Poll for completion
    while (true) {
        const status = await cumulus9.getBatchStatus(batch_id)
        console.log(`  [${status.status}] ${status.completed_pct.toFixed(1)}% complete (${status.runtime_ms}ms elapsed)`)

        if (['completed', 'failed', 'completed_with_errors'].includes(status.status)) {
            console.log(`\nBatch ${status.status} in ${status.runtime_ms}ms`)
            break
        }

        await new Promise((resolve) => setTimeout(resolve, 5000))
    }
}

main().catch((err) => {
    console.error('Error:', err.message || err)
    process.exit(1)
})
