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
        contract_expiry: 'DEC-27',
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
    let status
    while (true) {
        status = await cumulus9.getBatchStatus(batch_id)
        console.log(`  [${status.status}] ${status.completed_pct.toFixed(1)}% complete (${status.runtime_ms}ms elapsed)`)

        if (['completed', 'failed', 'completed_with_errors'].includes(status.status)) {
            console.log(`\nBatch ${status.status} in ${status.runtime_ms}ms`)
            break
        }

        await new Promise((resolve) => setTimeout(resolve, 5000))
    }

    if (status.status === 'failed') return

    // Step 3: Fetch results
    // One call for the whole batch, paged for a large book.
    const accounts = []
    let offset = 0
    for (;;) {
        const page = await cumulus9.getBatchResults(batch_id, 5000, offset)
        accounts.push(...page.results)
        offset += page.results.length
        if (page.results.length === 0 || offset >= page.total) break
    }

    console.log(`\nFetched ${accounts.length} account results`)

    const totalIm = accounts.reduce((sum, a) => sum + (a.initial_margin || 0), 0)
    console.log(`Total initial margin across batch: ${totalIm.toLocaleString()}`)

    // Step 4: Drill down into one account. The call above returns totals; this
    // returns the full calculation detail for a single account.
    const first = accounts[0]
    const detail = await cumulus9.getResults(first.request_id, first.portfolio_id)
    console.log(`\n${first.account_code}: ${(detail[0].portfolio || []).length} positions`)
}

main().catch((err) => {
    console.error('Error:', err.message || err)
    process.exit(1)
})
