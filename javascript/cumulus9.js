// Cumulus9 - All rights reserved.

'use strict'

const axios = require('axios')

const HEADERS = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${process.env.C9_API_SECRET}`,
}

/**
 * POST a portfolio payload to the Cumulus9 API (synchronous).
 * @param {object} payload - Portfolio request body.
 * @returns {Promise<object>} Parsed JSON response.
 */
exports.postPortfolio = async (payload) => {
    const response = await axios.post(`${process.env.C9_API_ENDPOINT}/portfolios`, payload, {
        headers: HEADERS,
    })
    return response.data
}

/**
 * Submit a portfolio for batch processing.
 * @param {object} payload - Portfolio request body.
 * @param {string} [processingMode='fifo'] - Queue mode: 'fifo', 'priority', or 'replace_all'.
 * @returns {Promise<{batch_id: string}>} Batch ID for polling.
 */
exports.submitBatch = async (payload, processingMode = 'fifo') => {
    const response = await axios.post(`${process.env.C9_API_ENDPOINT}/portfolios/batch`, payload, {
        headers: { ...HEADERS, 'x-processing-mode': processingMode },
    })
    return response.data
}

/**
 * Poll batch job status.
 * @param {string} batchId - The batch_id returned from submitBatch.
 * @returns {Promise<object>} Batch status object.
 */
exports.getBatchStatus = async (batchId) => {
    const response = await axios.get(`${process.env.C9_API_ENDPOINT}/portfolios/batch/${batchId}`, {
        headers: HEADERS,
    })
    return response.data
}

/**
 * Fetch every account a batch calculated, in one call.
 * @param {string} batchId - The batch_id returned from submitBatch.
 * @param {number} [limit=5000] - Maximum accounts to return (capped at 20000).
 * @param {number} [offset=0] - Accounts to skip, for paging a large book.
 * @returns {Promise<object>} {batch_id, status, total, limit, offset, results}.
 */
exports.getBatchResults = async (batchId, limit = 5000, offset = 0) => {
    const response = await axios.get(`${process.env.C9_API_ENDPOINT}/portfolios/batch/${batchId}/results`, {
        headers: HEADERS,
        params: { limit, offset },
    })
    return response.data
}

/**
 * Full calculation detail for one account: per-engine breakdowns, priced
 * positions, exceptions. Always pass portfolioId — without it you get every
 * account in that chunk, which for a large book can be tens of megabytes.
 * @param {string} requestId - The request_id on the account's row.
 * @param {string} [portfolioId] - One account: md5(account_code).
 * @returns {Promise<object[]>} Account results with the full drill-down.
 */
exports.getResults = async (requestId, portfolioId) => {
    const response = await axios.get(`${process.env.C9_API_ENDPOINT}/results`, {
        headers: HEADERS,
        params: portfolioId ? { request_id: requestId, portfolio_id: portfolioId } : { request_id: requestId },
    })
    return response.data
}
