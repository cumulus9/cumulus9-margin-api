# Cumulus9 Margin API

The Cumulus9 Margin API calculates initial margin requirements across all major clearing houses, including SPAN, SPAN2, PRISMA, TIMS, NODAL VaR, IRM 2.0, JPX VaR, KRX, B3 Core, and more. It also provides portfolio analytics (VaR, Greeks, P&L, stress testing) and ISDA SIMM calculations.

Submit a portfolio of positions via a single POST request and receive margin results with full calculation drill-downs.

---

## Authentication

All requests require an API key sent as a Bearer token.

```
Authorization: Bearer <your_api_secret>
Content-Type: application/json
```

API keys use the `sk-...` prefix format. To obtain credentials (`C9_API_ENDPOINT` and `C9_API_SECRET`), contact **support@cumulus9.com**.

---

## Endpoints

| Method | Path                            | Description                                                 |
| ------ | ------------------------------- | ----------------------------------------------------------- |
| `POST` | `/portfolios`                   | Submit a portfolio and receive margin results synchronously |
| `POST` | `/portfolios/batch`             | Submit a large portfolio for background processing          |
| `GET`  | `/portfolios/batch/:batch_id`   | Poll batch job status and progress                          |
| `GET`  | `/healthcheck/analytics-engine` | Check engine status and available margin parameters         |

---

## POST `/portfolios`

Submit one or more accounts with positions and receive margin calculations synchronously.

### Request Parameters

All parameters are set at the top level of the JSON request body alongside the `portfolio` array.

| Parameter                     | Type            | Default               | Description                                                                                                                                    |
| ----------------------------- | --------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `portfolio`                   | `array`         | _required_            | Array of position objects (see [Position Types](#position-types))                                                                              |
| `calculation_type`            | `string`        | `"all"`               | Calculation modes: `"margins"`, `"analytics"`, `"simm"`, `"all"`. Combine with commas, e.g. `"margins,analytics"`                              |
| `vendor_symbology`            | `string`        | `"clearing"`          | Position symbology format: `"clearing"`, `"ion"`, `"gmi"`, `"tt_new"`                                                                          |
| `cme_symbology`               | `string`        | `"clearing"`          | CME-specific symbology: `"clearing"` or `"globex"`                                                                                             |
| `currency_code`               | `string`        | `"USD"`               | Base currency for aggregated results (ISO 4217). Supported: `USD`, `EUR`, `GBP`, `JPY`, `CHF`, `AUD`, `CAD`, `BRL`, `CNH`, `HKD`, `INR`, `NZD` |
| `bdate`                       | `integer`       | previous business day | Calculation date in `YYYYMMDD` format                                                                                                          |
| `price_date`                  | `integer`       | previous business day | Price date in `YYYYMMDD` format                                                                                                                |
| `cycle_code`                  | `string`        | —                     | Exchange cycle code                                                                                                                            |
| `use_closest_match`           | `boolean`       | `true`                | Auto-correct minor errors in expiry or strike by matching to the nearest valid contract                                                        |
| `use_closest_active`          | `boolean`       | `true`                | Use the closest active contract when the exact match is not available                                                                          |
| `pnl_details`                 | `boolean`       | `false`               | Cache the full historical P&L vector for downstream analysis                                                                                   |
| `in_memory`                   | `boolean`       | `false`               | Process the request in-memory without persisting results                                                                                       |
| `is_live`                     | `boolean`       | `true`                | Mark this as a live portfolio                                                                                                                  |
| `free_risk_rate`              | `number`        | `0.01`                | Risk-free rate used in analytics calculations                                                                                                  |
| `request_id`                  | `string` (UUID) | auto-generated        | User-defined UUID to track the request                                                                                                         |
| `memo`                        | `string`        | —                     | Free-text memo attached to the request                                                                                                         |
| `risk_metrics`                | `object`        | —                     | Configuration for analytics calculations (see below)                                                                                           |
| `simm_metrics`                | `object`        | —                     | Configuration for SIMM calculations (see below)                                                                                                |
| `stress_sensitivities`        | `object`        | —                     | Configuration for stress scenario analysis (see below)                                                                                         |
| `stress_test_enabled`         | `boolean`       | `false`               | Enable stress testing on the portfolio                                                                                                         |
| `stress_test_details_enabled` | `boolean`       | `false`               | Include detailed stress test drill-down                                                                                                        |
| `pricing`                     | `object`        | —                     | `{ "enabled": true }` to include live pricing                                                                                                  |
| `position_limits_enabled`     | `boolean`       | `false`               | Enable position limit checks                                                                                                                   |
| `fx_margin_parameters`        | `object`        | —                     | FX margin rate overrides, keyed by currency pair (e.g. `{ "EUR_USD": 0.02 }`)                                                                  |

### `risk_metrics` Object

Used when `calculation_type` includes `"analytics"`.

| Field                             | Type      | Default           | Description                                                       |
| --------------------------------- | --------- | ----------------- | ----------------------------------------------------------------- |
| `lookback`                        | `integer` | `250`             | Historical lookback period in business days                       |
| `ci`                              | `number`  | `99`              | Confidence interval (e.g. `99` for 99%)                           |
| `method`                          | `string`  | `"value-at-risk"` | Risk method: `"value-at-risk"` or `"expected-shortfall"`          |
| `mpor`                            | `integer` | `1`               | Margin period of risk in days                                     |
| `mode`                            | `string`  | `"absolute"`      | Returns mode: `"absolute"` or `"relative"`                        |
| `bond_pricing_version`            | `integer` | `1`               | Bond pricing model version                                        |
| `bond_use_continuous_compounding` | `boolean` | `true`            | `true` for continuous compounding, `false` for annual compounding |

### `simm_metrics` Object

Used when `calculation_type` includes `"simm"`.

| Field            | Type      | Default | Description                                                    |
| ---------------- | --------- | ------- | -------------------------------------------------------------- |
| `version`        | `string`  | latest  | ISDA SIMM version with underscores (e.g. `"2_6_5"` for v2.6.5) |
| `holding_period` | `integer` | `10`    | Holding period in days: `1` or `10`                            |

### `stress_sensitivities` Object

Used when `calculation_type` includes `"analytics"`. Defines stress scenarios applied to the portfolio.

| Field                  | Type       | Default                                        | Description                                                          |
| ---------------------- | ---------- | ---------------------------------------------- | -------------------------------------------------------------------- |
| `underlying_shocks`    | `number[]` | `[-4, -3, -2, -1, 1, 2, 3, 4]`                 | Shocks applied to the underlying price                               |
| `volatility_shocks`    | `number[]` | `[-0.8, -0.5, -0.3, -0.1, 0.1, 0.3, 0.5, 0.8]` | Corresponding volatility shocks (same length as `underlying_shocks`) |
| `shock_type`           | `string`   | `"absolute"`                                   | Shock interpretation: `"absolute"` or `"relative"`                   |
| `use_std_dev`          | `boolean`  | `true`                                         | Scale shocks by standard deviation                                   |
| `std_dev_lookback`     | `integer`  | `2500`                                         | Lookback period for standard deviation calculation                   |
| `std_dev_mpor`         | `integer`  | `1`                                            | Margin period of risk for standard deviation scaling                 |
| `generate_full_report` | `boolean`  | `false`                                        | Generate a full stress test report                                   |

---

## Batch Processing

For large portfolios or high-volume workloads, use the batch endpoint. It accepts the same payload as `POST /portfolios` and processes it asynchronously in the background with automatic chunking and progress tracking.

### POST `/portfolios/batch`

Submit a portfolio for background processing.

**Request body**: Same JSON payload as `POST /portfolios`.

**Request headers**:

| Header              | Values                                  | Default  | Description                                                                                 |
| ------------------- | --------------------------------------- | -------- | ------------------------------------------------------------------------------------------- |
| `x-processing-mode` | `"fifo"`, `"priority"`, `"replace_all"` | `"fifo"` | Queue behavior: FIFO ordering, priority promotion, or replace all queued jobs for this user |

**Response**: `202 Accepted`

```json
{
    "batch_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Limits**: Maximum payload size is 500 MB.

### GET `/portfolios/batch/:batch_id`

Poll the status of a batch job.

**Response**:

```json
{
    "batch_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "processing",
    "queue_position": 0,
    "created_at": "2025-01-03T09:31:14Z",
    "completed_at": null,
    "runtime_ms": 4523,
    "completed_pct": 67.5
}
```

| Field            | Type      | Description                                                                         |
| ---------------- | --------- | ----------------------------------------------------------------------------------- |
| `batch_id`       | `string`  | UUID of the batch job                                                               |
| `status`         | `string`  | `"queued"`, `"processing"`, `"completed"`, `"failed"`, or `"completed_with_errors"` |
| `queue_position` | `integer` | Position in queue (present only when `status` is `"queued"`)                        |
| `created_at`     | `string`  | ISO 8601 submission timestamp                                                       |
| `completed_at`   | `string`  | ISO 8601 completion timestamp (`null` while in progress)                            |
| `runtime_ms`     | `integer` | Elapsed time in milliseconds                                                        |
| `completed_pct`  | `number`  | Completion percentage (0--100)                                                      |

---

## Position Types

The `portfolio` array supports five position types. You can mix different types within a single request across multiple accounts.

### Exchange-Traded Derivatives (ETD)

Standard listed futures and options.

| Field              | Type             | Required | Description                                                                                  |
| ------------------ | ---------------- | -------- | -------------------------------------------------------------------------------------------- |
| `account_code`     | `string`         | yes      | Internal account identifier                                                                  |
| `account_name`     | `string`         | —        | Display name for the account                                                                 |
| `sub_account_code` | `string`         | —        | Sub-account identifier                                                                       |
| `sub_account_name` | `string`         | —        | Sub-account display name                                                                     |
| `exchange_code`    | `string`         | yes      | Exchange acronym (e.g. `"NYMEX"`, `"ICE.EU"`, `"EUREX"`, `"ASX"`)                            |
| `contract_code`    | `string`         | yes      | Contract symbol (e.g. `"CL"`, `"B"`, `"FDAX"`)                                               |
| `contract_type`    | `string`         | yes      | `"FUT"` / `"F"` / `"Future"` for futures, `"CALL"` for call options, `"PUT"` for put options |
| `contract_expiry`  | `string`         | yes      | Expiry date. Accepts `YYYYMM`, `YYYYMMDD`, or `MMM-YY` formats                               |
| `contract_strike`  | `string`         | —        | Strike price. Required for options, omit or leave empty for futures                          |
| `net_position`     | `string\|number` | yes      | Position size (positive = long, negative = short)                                            |
| `account_type`     | `string`         | —        | Margin account classification (see [Account Types](#account-types)). Default: `"H"`          |
| `omnibus_ind`      | `string`         | —        | Omnibus indicator                                                                            |
| `position_id`      | `string`         | —        | External position identifier                                                                 |
| `long_qty`         | `string\|number` | —        | Long quantity                                                                                |
| `short_qty`        | `string\|number` | —        | Short quantity                                                                               |
| `sod_qty`          | `string\|number` | —        | Start-of-day quantity                                                                        |
| `open_qty`         | `string\|number` | —        | Open quantity                                                                                |
| `close_qty`        | `string\|number` | —        | Close quantity                                                                               |
| `avg_buy`          | `string\|number` | —        | Average buy price                                                                            |
| `avg_sell`         | `string\|number` | —        | Average sell price                                                                           |
| `itd_volume`       | `string\|number` | —        | Intraday traded volume                                                                       |

```json
{
    "account_code": "Account 001",
    "exchange_code": "NYMEX",
    "contract_code": "CL",
    "contract_type": "FUT",
    "contract_expiry": "202512",
    "net_position": "500",
    "account_type": "H"
}
```

### Fixed Income (Bonds)

Cash bond positions for analytics and margin calculations.

| Field              | Type             | Required | Description                                          |
| ------------------ | ---------------- | -------- | ---------------------------------------------------- |
| `account_code`     | `string`         | yes      | Internal account identifier                          |
| `currency`         | `string`         | —        | Bond currency (ISO 4217)                             |
| `contract_type`    | `string`         | —        | Typically `"BOND"`                                   |
| `maturity`         | `string`         | yes      | Maturity date in `YYYYMMDD` format                   |
| `coupon_rate`      | `string\|number` | —        | Annual coupon rate as a percentage (e.g. `6` for 6%) |
| `coupon_frequency` | `string\|number` | —        | Coupon payments per year (e.g. `2` for semi-annual)  |
| `notional`         | `string\|number` | yes      | Face value (positive = long, negative = short)       |

```json
{
    "account_code": "Account 002",
    "currency": "USD",
    "contract_type": "BOND",
    "maturity": "20461021",
    "coupon_rate": 6,
    "coupon_frequency": 2,
    "notional": 1000000
}
```

### FX Positions

Foreign exchange positions.

| Field           | Type     | Required | Description                                         |
| --------------- | -------- | -------- | --------------------------------------------------- |
| `account_code`  | `string` | yes      | Internal account identifier                         |
| `currency_pair` | `string` | yes      | Currency pair (e.g. `"EUR_USD"`, `"GBP_JPY"`)       |
| `contract_type` | `string` | —        | Contract type                                       |
| `expiry`        | `string` | —        | Expiry date                                         |
| `amount`        | `number` | yes      | Notional amount (positive = long, negative = short) |

```json
{
    "account_code": "Account 003",
    "currency_pair": "EUR_USD",
    "amount": 5000000
}
```

### Fixed Income by CUSIP

Bond positions identified by CUSIP rather than individual terms.

| Field          | Type             | Required | Description                                    |
| -------------- | ---------------- | -------- | ---------------------------------------------- |
| `account_code` | `string`         | yes      | Internal account identifier                    |
| `cusip`        | `string`         | yes      | CUSIP identifier                               |
| `notional`     | `string\|number` | yes      | Face value (positive = long, negative = short) |

```json
{
    "account_code": "Account 004",
    "cusip": "912828ZT6",
    "notional": 1000000
}
```

### ISDA CRIF (SIMM Positions)

Positions formatted according to ISDA's Common Risk Interchange Format for SIMM margin calculations.

| Field                 | Type     | Required | Description                                                            |
| --------------------- | -------- | -------- | ---------------------------------------------------------------------- |
| `account_code`        | `string` | yes      | Internal account identifier                                            |
| `product_class`       | `string` | yes      | ISDA product class: `"RatesFX"`, `"Credit"`, `"Equity"`, `"Commodity"` |
| `risk_type`           | `string` | yes      | ISDA risk type (e.g. `"Risk_IRCurve"`, `"Risk_FX"`, `"Risk_CreditQ"`)  |
| `qualifier`           | `string` | yes      | Risk qualifier (e.g. currency code, issuer)                            |
| `bucket`              | `string` | yes      | ISDA bucket identifier                                                 |
| `label1`              | `string` | yes      | Tenor or maturity label (e.g. `"15Y"`, `"30Y"`)                        |
| `label2`              | `string` | yes      | Sub-curve label (e.g. `"OIS"`, `"Libor3m"`)                            |
| `amount_usd`          | `number` | —        | Sensitivity amount in USD                                              |
| `amount`              | `number` | —        | Sensitivity amount in local currency                                   |
| `amount_currency`     | `string` | —        | Currency of the `amount` field                                         |
| `im_model`            | `string` | —        | Set to `"SIMM"`                                                        |
| `trade_id`            | `string` | —        | Trade identifier                                                       |
| `valuation_date`      | `string` | —        | Valuation date (`DD/MM/YYYY`)                                          |
| `end_date`            | `string` | —        | End date (`DD/MM/YYYY`)                                                |
| `collect_regulations` | `string` | —        | Comma-separated regulation codes (e.g. `"CFTC,ESA"`)                   |
| `post_regulations`    | `string` | —        | Comma-separated regulation codes (e.g. `"NONREG,CFTC,ESA"`)            |

```json
{
    "account_code": "Fund1_1234",
    "im_model": "SIMM",
    "product_class": "RatesFX",
    "risk_type": "Risk_IRCurve",
    "qualifier": "USD",
    "bucket": "1",
    "label1": "15Y",
    "label2": "OIS",
    "amount_usd": 1000000
}
```

---

## Account Types

### SPAN, SPAN2, and IRM Exchanges

| Code   | Description                              |
| ------ | ---------------------------------------- |
| `H`    | Hedger (default)                         |
| `S`    | Speculator                               |
| `M`    | Member                                   |
| `HRP`  | Heightened Risk Profile (SPAN2 only)     |
| `NHRP` | Non-Heightened Risk Profile (SPAN2 only) |

> CME Group's [Advisory 20-404](https://www.cmegroup.com/notices/clearing/2020/10/Chadv20-404.pdf) redefined the traditional Speculator/Hedger categories to HRP/NHRP effective January 27, 2021.

### KRX Exchange

| Code | Description        |
| ---- | ------------------ |
| `C`  | Customer Margin    |
| `M`  | Maintenance Margin |
| `H`  | Member Margin      |

---

## Response Schema

### Synchronous Response (`POST /portfolios`)

A successful request returns:

```json
{
    "request_id": "5c09862d-8d69-0f8d-821b-47762ef06a6f",
    "username": "user@cumulus9.com",
    "status": "success",
    "data": [ ... ],
    "runtime": 114,
    "parameters": {
        "span": { "ICE": "20250106", "LME": "20250106" }
    },
    "memo": "optional memo text"
}
```

| Field        | Type      | Description                                                    |
| ------------ | --------- | -------------------------------------------------------------- |
| `request_id` | `string`  | UUID identifying this request                                  |
| `username`   | `string`  | Username associated with the API credentials                   |
| `status`     | `string`  | `"success"`, `"failed"`, or `"loading"`                        |
| `data`       | `array`   | Array of per-account result objects (see below)                |
| `runtime`    | `integer` | Processing time in milliseconds                                |
| `parameters` | `object`  | Margin model parameters and file dates used in the calculation |
| `memo`       | `string`  | Memo from the request, if provided                             |
| `error`      | `object`  | Error details, if status is `"failed"`                         |

### Per-Account Result Object

Each element in the `data` array contains:

| Field                          | Type      | Description                                                       |
| ------------------------------ | --------- | ----------------------------------------------------------------- |
| `request_id`                   | `string`  | UUID of the parent request                                        |
| `portfolio_id`                 | `string`  | UUID identifying this account's calculation                       |
| `submitted_time`               | `string`  | ISO 8601 timestamp of submission                                  |
| `account_code`                 | `string`  | Account identifier from the input                                 |
| `status`                       | `string`  | `"done"` on success                                               |
| `price_date`                   | `integer` | Calculation date (`YYYYMMDD`)                                     |
| `currency_code`                | `string`  | Base currency for aggregated results                              |
| `initial_margin`               | `number`  | Total initial margin requirement                                  |
| `gross_margin`                 | `number`  | Gross margin before offsets                                       |
| `requirement`                  | `number`  | Net margin requirement                                            |
| `gross_requirement`            | `number`  | Gross margin requirement                                          |
| `option_liquidation_value`     | `number`  | Net option liquidation value                                      |
| `delivery_margin`              | `number`  | ICE Clear Europe delivery-margin component                        |
| `cvm`                          | `number`  | Contingent variation margin component                             |
| `sellers_security`             | `number`  | Seller's security component                                       |
| `buyers_security`              | `number`  | Buyer's security component                                        |
| `value_at_risk`                | `number`  | Portfolio Value-at-Risk (when analytics requested)                |
| `stress_loss`                  | `number`  | Worst historical daily loss (when analytics requested)            |
| `dv01`                         | `number`  | Dollar value of a basis point (when analytics requested)          |
| `additional_margin`            | `number`  | Add-on charges, including delivery-period components              |
| `pnl`                          | `number`  | P&L                                                               |
| `itd_volume`                   | `number`  | Intraday traded volume                                            |
| `margin_by_ccp`                | `array`   | Margin breakdown by clearing house                                |
| `margin_by_contract`           | `array`   | Margin breakdown by individual contract                           |
| `margin_by_span`               | `array`   | SPAN drill-down (scanning risk, spread charges, etc.)             |
| `margin_by_span2`              | `array`   | SPAN2 drill-down                                                  |
| `margin_by_eurexpme`           | `array`   | Eurex PRISMA drill-down                                           |
| `margin_by_eurexpme_drilldown` | `array`   | Eurex PRISMA per-instrument component margins                     |
| `margin_by_simm`               | `array`   | ISDA SIMM drill-down                                              |
| `margin_by_fx`                 | `array`   | FX margin drill-down                                              |
| `margin_by_jpxvar`             | `array`   | JPX VaR drill-down                                                |
| `margin_by_krx`                | `array`   | KRX margin drill-down                                             |
| `margin_by_nodal`              | `array`   | Nodal VaR drill-down                                              |
| `margin_by_irm2_3`             | `array`   | IRM 2.3 drill-down                                                |
| `margin_by_irm2_3_delivery`    | `array`   | IRM 2.3 delivery-margin component breakdown                       |
| `margin_by_euronextvar`        | `array`   | Euronext VaR drill-down                                           |
| `margin_by_dce`                | `array`   | DCE margin drill-down                                             |
| `margin_by_shfe`               | `array`   | SHFE margin drill-down                                            |
| `margin_by_zce`                | `array`   | ZCE margin drill-down                                             |
| `pnl_vector`                   | `array`   | Historical P&L vector (when `pnl_details` is `true`)              |
| `pnl_vector_pct`               | `array`   | Historical P&L vector as percentages                              |
| `scenario_analysis`            | `object`  | Scenario analysis results                                         |
| `stress_tests`                 | `object`  | Stress test results (when `stress_test_enabled` is `true`)        |
| `position_limits`              | `object`  | Position limit results (when `position_limits_enabled` is `true`) |
| `exceptions`                   | `array`   | Positions excluded from calculations with reason                  |
| `closest_matches`              | `array`   | Positions auto-corrected when `use_closest_match` is `true`       |
| `portfolio`                    | `array`   | Enriched position records with resolved contract details          |

### `margin_by_ccp` Element

| Field                      | Type     | Description                                                |
| -------------------------- | -------- | ---------------------------------------------------------- |
| `clearing_org`             | `string` | Clearing house code (e.g. `"CME"`, `"ICE"`, `"EUREX_P"`)   |
| `result_type`              | `string` | Margin model used (e.g. `"span"`, `"span2"`, `"eurexpme"`) |
| `currency_code`            | `string` | Local currency of the clearing house                       |
| `fxrate`                   | `number` | FX rate used to convert to the base currency               |
| `initial_margin`           | `number` | Margin requirement for this CCP                            |
| `option_liquidation_value` | `number` | Option liquidation value at this CCP                       |
| `delivery_margin`          | `number` | ICE Clear Europe delivery-margin component                 |
| `cvm`                      | `number` | Contingent variation margin component                      |
| `sellers_security`         | `number` | Seller's security component                                |
| `buyers_security`          | `number` | Buyer's security component                                 |
| `cross_model_offset`       | `number` | Cross-model offset credit, if applicable                   |

### `margin_by_irm2_3_delivery` Element

| Field               | Type     | Description                                |
| ------------------- | -------- | ------------------------------------------ |
| `result_type`       | `string` | Margin model, `"irm2_3"`                   |
| `clearing_org`      | `string` | Clearing house, `"ICE.EU"`                 |
| `currency_code`     | `string` | Local currency                             |
| `exchange`          | `string` | Exchange code                              |
| `contract_code`     | `string` | Contract code                              |
| `contract_name`     | `string` | Contract description                       |
| `sector`            | `string` | Sector                                     |
| `sub_sector`        | `string` | Sub-sector                                 |
| `delivery_margin`   | `number` | ICE Clear Europe delivery-margin component |
| `cvm`               | `number` | Contingent variation margin component      |
| `sellers_security`  | `number` | Seller's security component                |
| `buyers_security`   | `number` | Buyer's security component                 |

### `margin_by_span` Element

| Field                      | Type     | Description                     |
| -------------------------- | -------- | ------------------------------- |
| `clearing_org`             | `string` | Clearing house code             |
| `exchange`                 | `string` | Exchange code                   |
| `cc_code`                  | `string` | Combined commodity code         |
| `cc_name`                  | `string` | Combined commodity name         |
| `currency_code`            | `string` | Local currency                  |
| `fxrate`                   | `number` | FX rate to base currency        |
| `scenario`                 | `string` | SPAN scenario number            |
| `initial_margin`           | `number` | Total margin for this commodity |
| `scanning_risk`            | `number` | Scanning risk component         |
| `prompt_date_charge`       | `number` | Prompt date charge              |
| `intra_spread_charge`      | `number` | Intra-commodity spread charge   |
| `short_option_charge`      | `number` | Short option minimum charge     |
| `intercontract_credit`     | `number` | Inter-commodity spread credit   |
| `strategy_spread_charge`   | `number` | Strategy spread charge          |
| `option_liquidation_value` | `number` | Option liquidation value        |

---

## Error Responses

| Status | Description                                                         |
| ------ | ------------------------------------------------------------------- |
| `400`  | Bad Request -- invalid payload structure or missing required fields |
| `401`  | Unauthorized -- invalid or expired API key                          |
| `413`  | Payload Too Large -- batch payload exceeds 500 MB                   |
| `429`  | Too Many Requests -- rate limit exceeded                            |
| `500`  | Internal Server Error                                               |

### Validation Errors (400)

When a request fails validation, the response body contains a description of the issue:

```json
{
    "error": "\"portfolio[0].exchange_code\" is required"
}
```

### Exceptions and Closest Matches

Even when a request succeeds (`200`), individual positions may fail validation. These are reported in the per-account result rather than causing the entire request to fail.

**`exceptions`** -- positions excluded from the calculation:

```json
{
    "exceptions": [
        {
            "position_id": "5",
            "engine": "validation",
            "exception": "Invalid `expiry` on position ICE.EU | B - Brent Crude Futures | FUT | 202501 | 0"
        }
    ]
}
```

**`closest_matches`** -- positions auto-corrected when `use_closest_match` is `true`. The original position is replaced with the nearest valid contract and the correction is logged:

```json
{
    "closest_matches": [
        {
            "position_id": "3",
            "engine": "validation",
            "exception": "Applied closest matching expiry instead of loaded 202501 on position ICE.EU | B - Brent Crude Futures | FUT | 20250300 | 0"
        }
    ]
}
```

Always check both arrays in your integration to detect positions that were dropped or modified.

---

## Rate Limits

-   Maximum of **100 unique account codes** per `POST /portfolios` request.
-   Per-user rate limiting is enforced on a **60-second sliding window**. The exact throughput depends on your license tier.
-   Contact support@cumulus9.com to discuss rate limit adjustments.

---

## Quick Start Examples

### Python

```python
import requests

C9_API_ENDPOINT = "https://your-endpoint.cumulus9.com"
C9_API_SECRET = "sk-your-api-secret"

payload = {
    "calculation_type": "margins",
    "vendor_symbology": "clearing",
    "portfolio": [
        {
            "account_code": "Account 001",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "FUT",
            "contract_expiry": "202512",
            "net_position": "100",
            "account_type": "H"
        }
    ]
}

response = requests.post(
    f"{C9_API_ENDPOINT}/portfolios",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {C9_API_SECRET}"
    },
    json=payload
)

results = response.json()
for account in results["data"]:
    print(f"{account['account_code']}: ${account['initial_margin']:,.2f}")
```

### Batch submission (Python)

```python
import time
import requests

C9_API_ENDPOINT = "https://your-endpoint.cumulus9.com"
C9_API_SECRET = "sk-your-api-secret"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {C9_API_SECRET}"
}

# Submit batch
payload = {
    "calculation_type": "margins",
    "vendor_symbology": "clearing",
    "portfolio": [ ... ]  # large portfolio
}

response = requests.post(
    f"{C9_API_ENDPOINT}/portfolios/batch",
    headers={**HEADERS, "x-processing-mode": "fifo"},
    json=payload
)
batch_id = response.json()["batch_id"]

# Poll for completion
while True:
    status = requests.get(
        f"{C9_API_ENDPOINT}/portfolios/batch/{batch_id}",
        headers=HEADERS
    ).json()
    print(f"{status['completed_pct']:.1f}% complete")
    if status["status"] in ("completed", "failed", "completed_with_errors"):
        break
    time.sleep(5)
```

### cURL

```bash
curl -X POST "$C9_API_ENDPOINT/portfolios" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $C9_API_SECRET" \
  -d '{
    "calculation_type": "margins",
    "vendor_symbology": "clearing",
    "portfolio": [
        {
            "account_code": "Account 001",
            "exchange_code": "ICE.EU",
            "contract_code": "B",
            "contract_type": "FUT",
            "contract_expiry": "202512",
            "net_position": "100",
            "account_type": "H"
        }
    ]
}'
```

See the language-specific directories for complete runnable examples:

| Directory     | Examples                                                                                            |
| ------------- | --------------------------------------------------------------------------------------------------- |
| `python/`     | Basic margin, margin ageing, batch processing, healthcheck, SIMM impact analysis, multi-asset-class |
| `javascript/` | Basic margin, batch processing                                                                      |
| `curl/`       | Basic margin, batch processing                                                                      |
| `csharp/`     | Basic margin                                                                                        |
| `r/`          | Basic margin                                                                                        |

---

## Full Payload Example

A multi-account, multi-asset-class request combining ETD, Fixed Income, FX, and CRIF positions with analytics and stress testing:

```json
{
    "calculation_type": "margins,analytics,simm",
    "vendor_symbology": "clearing",
    "currency_code": "USD",
    "use_closest_match": true,
    "risk_metrics": {
        "lookback": 250,
        "ci": 99,
        "method": "value-at-risk",
        "mpor": 1,
        "mode": "absolute"
    },
    "simm_metrics": {
        "version": "2_6_5",
        "holding_period": 10
    },
    "stress_sensitivities": {
        "underlying_shocks": [-4, -3, -2, -1, 1, 2, 3, 4],
        "volatility_shocks": [-0.8, -0.5, -0.3, -0.1, 0.1, 0.3, 0.5, 0.8],
        "shock_type": "absolute",
        "use_std_dev": true
    },
    "stress_test_enabled": true,
    "portfolio": [
        {
            "account_code": "Account 001",
            "exchange_code": "NYMEX",
            "contract_code": "CL",
            "contract_type": "FUT",
            "contract_expiry": "202512",
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
            "net_position": "-50",
            "account_type": "H"
        },
        {
            "account_code": "Account 003",
            "currency": "USD",
            "contract_type": "BOND",
            "maturity": "20461021",
            "coupon_rate": 6,
            "coupon_frequency": 2,
            "notional": 1000000
        },
        {
            "account_code": "Account 004",
            "currency_pair": "EUR_USD",
            "amount": 5000000
        },
        {
            "account_code": "Account 005",
            "im_model": "SIMM",
            "product_class": "RatesFX",
            "risk_type": "Risk_IRCurve",
            "qualifier": "USD",
            "bucket": "1",
            "label1": "15Y",
            "label2": "OIS",
            "amount_usd": 1000000
        }
    ]
}
```

---

## Links

-   [Cumulus9](https://cumulus9.com)
-   [Privacy Policy](https://cumulus9.com/privacy-policy)
-   [Terms and Conditions](https://cumulus9.com/terms-and-conditions)
-   Support: support@cumulus9.com
