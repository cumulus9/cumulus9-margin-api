// Cumulus9 - All rights reserved.

'use-strict'

const axios = require('axios')
const qs = require('qs')

const getAccessToken = () => {
    const basicAuthorization = Buffer.from(
        `${process.env.C9_API_CLIENT_ID}:${process.env.C9_API_CLIENT_SECRET}`,
    ).toString('base64')
    return new Promise((res, rej) => {
        let data = qs.stringify({
            grant_type: 'client_credentials',
            scope: 'riskcalc/get',
        })
        let config = {
            method: 'post',
            url: process.env.C9_API_AUTH_ENDPOINT,
            headers: {
                Authorization: `Basic ${basicAuthorization}`,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data: data,
        }
        axios(config)
            .then(function (r) {
                res(r.data)
            })
            .catch((e) => {
                rej(`${e.message || e}`)
            })
    })
}

exports.postPorfolio = (portfolioJson) => {
    return new Promise((res, rej) => {
        getAccessToken()
            .then((auth) => {
                const config = {
                    method: 'post',
                    url: `${process.env.C9_API_ENDPOINT}/portfolios`,
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: 'Bearer ' + auth.access_token,
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
            .catch((e) => {
                rej(`Cumulus9 API Token Validation - ${e.message || e}`)
            })
    })
}
