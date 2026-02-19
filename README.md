# Cumulus9 Analytics API

The Cumulus9 Analytics and Margin API is a RESTful service that replicates clearing house margin methodologies across all derivatives markets and provides portfolio-level risk analytics.

## How to get started (TL;DR)

To access the Cumulus9 Analytics API, please send an email to `support@cumulus9.com` requesting credentials.

Once you receive the credentials, navigate to your preferred programming language folder, such as python, and begin.

If you prefer a different language, please email us and we will add it as an option.

## Supported margin methodologies

-   SPAN and SPAN 2
-   PRISMA
-   OCC
-   IRM 2.0 and IRM 2.3
-   NODAL VaR
-   B3 Core
-   Eurex Prisma Margin Estimator
-   Euronext VAR
-   SIMM
-   KRX PC-COMS
-   Portfolio Margin
-   Major Chinese CCP margin frameworks, including DCE, SHFE, ZCE, and others

This list is continuously expanding. Cumulus9 maintains active coverage of new clearing houses, regulatory changes, and model upgrades in order to preserve comprehensive global margin coverage across listed and OTC markets.

## Supported asset classes

-   Exchange Traded Derivatives (ETD)
-   Fixed Income cash instruments
-   Foreign Exchange (FX)
-   SIMM CRIF formatted sensitivities

## The API response

-   Initial margin
-   Margin requirement net of option value
-   Option liquidation value
-   Additional margin add-ons
-   Margin by CCP
-   Margin by contract
-   Full analytics including Greeks, VaR, stress metrics
-   Validation errors and closest match adjustments

## 2. Authentication

Cumulus9 uses a static API secret for authentication.

All requests must include the following HTTP header: `Authorization: Bearer <C9_API_SECRET>`

Where:

-   `C9_API_SECRET` is the secret key issued by Cumulus9.
-   The secret must be kept secure and stored server side only.

All portfolio submissions and API calls are authenticated using this header.

Cumulus9 operates a production grade security architecture built on modern enterprise security controls and hardened infrastructure protection mechanisms.

For detailed information regarding the platform’s security framework, governance model, and compliance posture, please contact `info@cumulus9.com` directly.

## 3. Portfolio Submission

Cumulus9 supports both synchronous portfolio submission and batch processing.

### Standard Portfolio Submission

Used for single portfolio calculations or real time requests.

Endpoint: `POST` `${C9_API_ENDPOINT}/portfolios`

This endpoint supports both synchronous and asynchronous execution via the execution_mode parameter.

### Batch Processing

Used for high volume portfolio processing and large scale workloads.

Endpoint: `POST` `${C9_API_ENDPOINT}/portfolios/batch`

Batch requests are queued and processed asynchronously. A `batch_id` is returned and can be used to retrieve processing status and results.

Batch processing is recommended for large portfolios, multi account submissions, or high throughput environments.

## 4. Request Payload Structure

### Top-Level Parameters

| Field             | Type     | Description                   |
| ----------------- | -------- | ----------------------------- |
| portfolio         | array    | List of positions             |
| calculation_type  | string   | margins, analytics, simm, all |
| execution_mode    | string   | sync or async                 |
| vendor_symbology  | string   | clearing, ion, gmi, tt_new    |
| cme_symbology     | string   | clearing or globex            |
| currency_code     | string   | Reporting currency            |
| bdate             | YYYYMMDD | Business date                 |
| request_id        | UUID     | Optional custom ID            |
| use_closest_match | boolean  | Default true                  |

Default behavior:

-   calculation_type: all
-   execution_mode: sync
-   currency_code: USD
-   use_closest_match: true

## 5. Supported Position Types

### 5.1 Exchange Traded Derivatives

Required fields:

-   account_code
-   exchange_code
-   contract_code
-   contract_type
-   contract_expiry
-   net_position

Optional:

-   contract_strike
-   account_type
-   long_qty
-   short_qty

Account types vary by CCP.

### 5.2 Fixed Income

Required:

-   account_code
-   currency
-   contract_type
-   maturity
-   coupon_rate
-   coupon_frequency
-   notional

### 5.3 FX

Required:

-   account_code
-   currency_pair
-   contract_type
-   expiry
-   amount

### 5.4 SIMM CRIF

Required:

-   account_code
-   product_class
-   risk_type
-   qualifier
-   bucket
-   label1
-   label2

Optional:

-   collect_regulations
-   amount_usd

## 6. Calculation Parameters

### 6.1 Risk Metrics

```json
{
    "lookback": 250,
    "ci": 99,
    "method": "value-at-risk",
    "mpor": 1,
    "mode": "absolute",
    "bond_pricing_version": 1,
    "bond_use_continuous_compounding": true
}
```

### 6.2 SIMM Metrics

```json
{
    "version": "2_6_5",
    "holding_period": 10
}
```

### 6.3 Stress Sensitivities

```json
{
    "underlying_shocks": [-0.2, -0.1, 0.1, 0.2],
    "volatility_shocks": [0, 0, 0, 0]
}
```

## 7. Response Structure

The API returns a ResultsData object.

### Core Portfolio-Level Fields

| Field                    | Description                       |
| ------------------------ | --------------------------------- |
| initial_margin           | Total initial margin              |
| requirement              | Net requirement after offsets     |
| gross_margin             | Gross margin before offsets       |
| option_liquidation_value | Net option value                  |
| additional_margin        | Add-ons and concentration charges |
| value_at_risk            | Portfolio VaR                     |
| stress_loss              | Stress scenario loss              |
| dv01                     | Interest rate sensitivity         |
| pnl                      | Mark to market PnL                |

### 7.1 Margin Breakdown

#### margin_by_ccp

Aggregated margin by clearing organization.

Fields include:

-   clearing_org
-   currency_code
-   initial_margin
-   option_liquidation_value
-   requirement
-   cross_model_offset

#### margin_by_contract

Granular breakdown by contract or product group.

Fields include:

-   clearing_org
-   exchange
-   cc_code
-   cc_name
-   sector
-   sub_sector
-   currency_code
-   fxrate
-   initial_margin
-   option_liquidation_value

#### Engine Specific Breakdowns

The response may include:

-   margin_by_span
-   margin_by_span2
-   margin_by_eurexpme
-   margin_by_euronextvar
-   margin_by_occtims
-   margin_by_irm2
-   margin_by_irm2_3
-   margin_by_jpxvar
-   margin_by_b3core
-   margin_by_simm
-   margin_by_fx
-   margin_by_swapclear
-   margin_by_dce
-   margin_by_zce
-   margin_by_shfe
-   margin_by_krx
-   margin_by_jse
-   margin_by_nodal

Each reflects native CCP output normalized into a consistent structure.

## 8. Validation and Exceptions

Response includes:

### exceptions

Positions rejected by validation or margin engines.

Fields:

-   position_id
-   engine
-   exception

### closest_matches

When use_closest_match=true, adjusted fields are reported separately.

## 9. What-If Analysis

Endpoint behavior supports before and after portfolio comparison.

Returns:

-   summary delta of margin metrics
-   margin_by_contract comparison in USD
-   position level comparison

Fields include:

-   im_usd_1
-   im_usd_2
-   olv_usd_1
-   olv_usd_2

## 10. Execution Modes

### sync

-   Immediate calculation
-   Returns full results

### async

-   Returns request_id
-   Results available via batch endpoints

## 11. Account Types

| Code | Description                 |
| ---- | --------------------------- |
| S    | Speculator                  |
| H    | Hedger                      |
| HRP  | Heightened Risk Profile     |
| NHRP | Non Heightened Risk Profile |

## 12. Performance

-   Demo: up to 100 portfolios per request and approximately 10,000 positions per minute
-   Pro: up to 1,000 portfolios per request and approximately 100,000 positions per minute
-   Enterprise: scalable to any volume with custom SLAs and dedicated infrastructure

Batch mode and worker scaling are available for high throughput workloads.

## 13. Error Handling

HTTP Status Codes:

-   `200` `OK`
-   `202` `Accepted for async`
-   `400` `Invalid payload`
-   `401` `Unauthorized`
-   `413` `Payload too large`
-   `500` `Internal error`

All errors return structured JSON.

## 14. Contact

For credentials and enterprise onboarding: [support@cumulus9.com](mailto:support@cumulus9.com)

## [About Us](https://cumulus9.com)

-   [Privacy Policy](https://cumulus9.com/privacy-policy)
-   [Terms and Conditions](https://cumulus9.com/terms-and-conditions)
