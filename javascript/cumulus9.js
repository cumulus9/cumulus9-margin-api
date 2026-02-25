// Cumulus9 - All rights reserved.

'use-strict'

const axios = require('axios')

exports.postPorfolio = (portfolioJson) => {
    return new Promise((res, rej) => {
        const config = {
            method: 'post',
            url: `${process.env.C9_API_ENDPOINT}/portfolios`,
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${process.env.C9_API_SECRET}`,
            },
            data: portfolioJson,
        }
        axios(config)
            .then((r) => {
                res(r.data)
            })
            .catch((e) => {
                rej(`Cumulus9 API - ${e.message || e}`)
            })
    })
}
