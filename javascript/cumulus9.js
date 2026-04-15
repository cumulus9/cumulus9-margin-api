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
