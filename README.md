# Cumulus9 Margin API

A quick start guide to trial the Cumulus9 Margin API with your favorite programming language.

## How to get started (TL;DR)

To access the Cumulus9 Margin API, please send an email to `support@cumulus9.com` requesting credentials.

Once you receive the credentials, navigate to your preferred programming language folder, such as `python`, and begin.

If you prefer a different language, please email us and we will add it as an option.

## How it works

The Cumulus9 Margin API is a user-friendly RESTful API that can be accessed from any programming language. The API is secured with OAuth2.

You can easily utilize this API by sending a POST request to obtain an access token, which you can then use to POST your portfolios and receive the margin results almost instantaneously.

Once you obtain from `support@cumulus9.com` your credentials: `c9_api_endpoint`, `c9_api_auth_endpoint`, `c9_api_client_id`, `c9_api_client_secret`, you can start using the API.

### Step 1: POST REQUEST To Retrieve Access Token

Post Request:

```txt
Headers: `Authorization: Basic BASE64(${c9_api_client_id}:${c9_api_client_secret})`
Content-Type: `application/x-www-form-urlencoded`
Data: `grant_type=client_credentials&scope=riskcalc%2Fget`
Request: `POST ${c9_api_auth_endpoint}`
```

### Step 3: POST REQUEST To send your portfolios to receive the margin

Sample portfolio payload (change only the portfolio section as needed):

```json
{
    "vendor_symbology": "clearing",
    "calculation_type": "margins",
    "execution_mode": "sync",
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
        }
    ]
}
```

Post Request:

```txt
Headers: `Authorization: Use the format Bearer ${access_token}`
Content-Type: `application/json`
Data: `portfolio payload`
Request: `POST ${c9_api_endpoint}/portfolios`
```

You will receive the margin in the response and calculation drill-down explaining the offsets applied.

## Description

The Cumulus9 Margin API is a Restful Web Service replicating the same Clearing Houses margin algorithms of all major derivatives exchanges, including SPAN, SPAN2, PRISMA, TIMS, NODAL VaR, IRM 2.0 and B3 Core.
The API allows you to load a portfolio of derivatives and receive within milliseconds the margin and calculation drill-down explaining the offsets applied.

## [About Us](https://cumulus9.com)

* [Privacy Policy](https://cumulus9.com/privacy-policy)
* [Terms and Conditions](https://cumulus9.com/terms-and-conditions)
