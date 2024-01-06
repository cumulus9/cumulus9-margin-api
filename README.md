# Cumulus9 Analytics API

A quick start guide to use the Cumulus9 Analytics API with your favorite programming language.

## Description

The Cumulus9 Analytics API is a Restful Web Service replicating the same Clearing Houses margin algorithms of all major derivatives exchanges, including SPAN, SPAN2, PRISMA, TIMS, NODAL VaR, IRM 2.0 and B3 Core.

The API also includes a comprehensive set of analytics, including Greeks, VaR, PnL, and more.

The API allows you to load a portfolio of contracts and receive the margin and calculation drill-down explaining the offsets applied.

![cumulus9-margin-api](https://raw.githubusercontent.com/cumulus9/cumulus9-margin-api/main/.github/images/instructions.gif)

## How to get started (TL;DR)

To access the Cumulus9 Analytics API, please send an email to `support@cumulus9.com` requesting credentials.

Once you receive the credentials, navigate to your preferred programming language folder, such as `python`, and begin.

If you prefer a different language, please email us and we will add it as an option.

## How it works

The Cumulus9 Analytics API is a user-friendly RESTful API that can be accessed from any programming language. The API is secured with OAuth2.

You can easily utilize this API by sending a POST request to obtain an access token, which you can then use to POST your portfolios and receive the margin results almost instantaneously.

Once you obtain from `support@cumulus9.com` your credentials: `c9_api_endpoint`, `c9_api_auth_endpoint`, `c9_api_client_id`, `c9_api_client_secret`, you can start using the API.

### Step 1: POST Request to Obtain an Access Token

Post Request:

```txt
Headers: `Authorization: Basic BASE64(${c9_api_client_id}:${c9_api_client_secret})`
Content-Type: `application/x-www-form-urlencoded`
Data: `grant_type=client_credentials&scope=riskcalc%2Fget`
Request: `POST ${c9_api_auth_endpoint}`
```

### Step 2: POST Request to Submit Your Portfolio and Receive Analytics Results

Sample portfolio payload (change only the portfolio section as needed):

```json
{
    "vendor_symbology": "clearing",
    "calculation_type": "margins",
    "execution_mode": "sync",
    "cme_symbology": "clearing",
    "portfolio": [
        {
            "account_code": "Account 001",
            "exchange_code": "ASX",
            "contract_code": "XT",
            "contract_type": "F",
            "contract_expiry": "DEC-25",
            "contract_strike": "",
            "net_position": "500"
        },
        {
            "account_code": "Account 001",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "Future",
            "contract_expiry": "DEC-25",
            "contract_strike": "",
            "net_position": "500"
        },
        {
            "account_code": "Account 001",
            "exchange_code": "NYMEX",
            "contract_code": "LO",
            "contract_type": "CALL",
            "contract_expiry": "202512",
            "contract_strike": "50.1",
            "net_position": "-1000"
        },
        {
            "account_code": "Account 002",
            "exchange_code": "EUREX",
            "contract_code": "FDAX",
            "contract_type": "FUT",
            "contract_expiry": "202612",
            "contract_strike": "",
            "net_position": "-50"
        },
        {
            "account_code": "Account 002",
            "currency": "USD",
            "contract_type": "BOND",
            "maturity": "20461021",
            "coupon_payment_pct": "6",
            "coupon_frequency": "2",
            "notional": "1000000"
        },
        {
            "account_code": "Account 002",
            "currency": "USD",
            "contract_type": "BOND",
            "maturity": "20361021",
            "coupon_payment_pct": "4",
            "coupon_frequency": "2",
            "notional": "-1000000"
        }
    ]
}
```

The API currently supports both ETD contracts and Fixed Income Cash contracts. For each contract type, the required fields are as follows:

-   ETD contracts colums: `account_code, exchange_code, contract_code, contract_type, contract_expiry, contract_strike, net_position`
-   Fixed Income Cash contracts colums: `account_code, exchange_code, contract_code, contract_type, contract_expiry, contract_strike, net_position`

Calculation Parameters:

-   `vendor_symbology`: `ion`, `clearing`, `bloomberg`, `gmi` | default: `clearing`
-   `calculation_type`: `margins`, `analytics`, `all` | default: `all`
-   `cme_symbology`: `globex`, `clearing`
-   `execution_mode`: `sync`, `async` | default: `sync`
-   `request_id`: UUID | default: random uuid
-   `bdate`: date in format YYYYMMDD | default: today
-   `pnl_details`: `false`, `true` | default: `false` (create cache data for the entire pnl vector)

Post Request:

```txt
Headers: `Authorization: Use the format Bearer ${access_token}`
Content-Type: `application/json`
Data: `portfolio payload`
Request: `POST ${c9_api_endpoint}/portfolios`
```

You will receive the margin in the response and calculation drill-down explaining the offsets applied.

## [About Us](https://cumulus9.com)

-   [Privacy Policy](https://cumulus9.com/privacy-policy)
-   [Terms and Conditions](https://cumulus9.com/terms-and-conditions)
