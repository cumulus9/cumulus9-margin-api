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
    "vendor_used": "clearing",
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
            "net_position": "500",
            "account_type": "H"
        },
        {
            "account_code": "Account 001",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "Future",
            "contract_expiry": "DEC-25",
            "contract_strike": "",
            "net_position": "500",
            "account_type": "H"
        },
        {
            "account_code": "Account 001",
            "exchange_code": "NYMEX",
            "contract_code": "LO",
            "contract_type": "CALL",
            "contract_expiry": "202512",
            "contract_strike": "50.1",
            "net_position": "-1000",
            "account_type": "H"
        },
        {
            "account_code": "Account 002",
            "exchange_code": "EUREX",
            "contract_code": "FDAX",
            "contract_type": "FUT",
            "contract_expiry": "202612",
            "contract_strike": "",
            "net_position": "-50",
            "account_type": "H"
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
        },
        {
            "valuation_date": "16/06/2023",
            "end_date": "18/09/2023",
            "account_code": "Fund1_1234",
            "im_model": "SIMM",
            "trade_id": 2.0,
            "product_class": "RatesFX",
            "risk_type": "Risk_IRCurve",
            "qualifier": "USD",
            "bucket": "1",
            "label1": "15Y",
            "label2": "OIS",
            "collect_regulations": "CFTC,ESA",
            "post_regulations": "NONREG,CFTC,ESA",
            "amount": 0.737256516,
            "amount_currency": "USD",
            "amount_usd": 0.737256516
        }
    ]
}
```

The API currently supports ETD and Fixed Income Cash contracts and ISDA’s Common Risk Interchange Format (CRIF) positions. For each type, the required fields are as follows:

-   ETD contracts colums: `account_code, exchange_code, contract_code, contract_type, contract_expiry, contract_strike, net_position, account_type`
-   Fixed Income Cash contracts colums: `account_code, exchange_code, contract_code, contract_type, contract_expiry, contract_strike, net_position`
-   CRIF colums: `valuation_date, end_date, account_code, im_model, trade_id, product_class, risk_type, qualifier, bucket, label1, label2, collect_regulations, post_regulations, amount, amount_currency, amount_usd`

On ETD contracts columns, account_type: `H` for hedge, `S` for speculative

Calculation Parameters:

-   `calculation_type`: `margins`, `analytics`, `all` | default: `all`
-   `use_closest_match`: `false`, `true` | default: `true`
-   `execution_mode`: `sync`, `async` | default: `sync`
-   `vendor_symbology`: `ion`, `clearing`, `bloomberg`, `gmi`, `tt_new` | default: `clearing`
-   `cme_symbology`: `globex`, `clearing`
-   `bdate`: date in format YYYYMMDD | default: calculation date
-   `request_id`: UUID | default: random uuid
-   `pnl_details`: `false`, `true` | default: `false` (create cache data for the entire pnl vector)

-   `risk_metrics`:

    ```json
    {
        "lookback": 1000, # lookback period
        "ci": 99, # confidence interval
        "method": "expected-shortfall",  # expected-shortfall | value-at-risk,
        "mpor": 1 # margin period of risk
    }
    ```

-   `simm_metrics`:

    ```json
    {
        "version": "2_6_5", # SIMM version using underscore instead of dots, e.g. 2_6_5 for 2.6.5
        "holding_period": 10 # holding period in days, either 1 or 10 days
    }
    ```

-   `stress_sensitivities`

    ```json
        {
            "underlying_shocks": [-0.2, -0.1, -0.05, -0.01, 0.01, 0.05, 0.1, 0.2] # shocks for underlying,
            "volatility_shock": [0, 0, 0, 0, 0, 0, 0, 0] # shocks for volatility
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

## IRM, SPAN and SPAN 2 Account Types

| account_type | description                              |
| ------------ | ---------------------------------------- |
| S            | Speculator                               |
| H            | Hedger                                   |
| M            | Member                                   |
| HRP          | Heightened Risk Profile (SPAN2 only)     |
| NHRP         | Non-Heightened Risk Profile (SPAN2 only) |

The CME Group's [Advisory 20-404](https://www.cmegroup.com/notices/clearing/2020/10/Chadv20-404.pdf) outlines changes to account classifications in response to revised CFTC regulations effective January 27, 2021.

The traditional `Speculator` (S) and `Hedger` (H) categories are being redefined to `Heightened Risk Profile` (HRP) and `Non-Heightened Risk Profile` (NHRP) accounts, respectively, affecting margin requirements and reporting formats.

## KRX Account Types

| account_type | description        |
| ------------ | ------------------ |
| C            | Customer Margin    |
| M            | Maintenance Margin |
| H            | Member Margin      |

## Performances

DEMO users on a free trial can process up to 100 portfolios per minute.

PRO users can handle up to 1,000 portfolios per second.

Enterprise users can process more than 1,000 portfolios per second, with additional fees for scaling through parallel instances to manage the increased load.

## [About Us](https://cumulus9.com)

-   [Privacy Policy](https://cumulus9.com/privacy-policy)
-   [Terms and Conditions](https://cumulus9.com/terms-and-conditions)
