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

## Public endpoints

`open-api-schema.yaml` is the canonical external contract. The public surface is
limited to the operations below.

### Calculations and results

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/portfolios` | Calculate margin and analytics synchronously |
| `POST` | `/portfolios/optimize` | Optimize eligible CME rates futures between listed and cleared-rates margin |
| `POST` | `/portfolios/batch` | Submit a large portfolio for background processing |
| `GET` | `/portfolios/batch/{batch_id}` | Poll batch status and progress |
| `GET` | `/portfolios/batch/{batch_id}/results` | Fetch every account calculated by a batch |
| `GET` | `/results` | Fetch the full drill-down for one calculation |
| `GET` | `/results/accounts` | Fetch the latest live result for each visible account |

### Stress scenarios

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/stress-test/scenarios` | List built-in and caller-owned scenarios |
| `POST` | `/stress-test/scenarios` | Create or replace caller-owned scenarios |
| `DELETE` | `/stress-test/scenarios` | Delete one caller-owned scenario |

### Contract discovery and validation

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/validation-reference/exchanges` | List enabled exchanges |
| `GET` | `/validation-reference/contracts/{exchange_code}` | List contracts for an exchange |
| `GET` | `/validation-reference/contract-type/{exchange_code}/{contract_code}` | List contract types |
| `GET` | `/validation-reference/expiries/{exchange_code}/{contract_code}/{contract_type}` | List expiries |
| `GET` | `/validation-reference/strikes/{exchange_code}/{contract_code}/{contract_type}/{expiry}` | List option strikes |
| `GET` | `/validation-reference/fi-reference` | Get fixed-income reference values |
| `GET` | `/validation-reference/irs-reference` | Get cleared-rates reference values |
| `GET` | `/validation-reference/ladder-reference` | Get rates delta-ladder reference values |
| `GET` | `/validation-reference/fx-symbols` | List currency codes supported in FX pairs |
| `POST` | `/validation-reference/portfolios` | Validate and standardise a portfolio without calculating it |

### Event-market discovery

These endpoints are available only when the requested event-market exchange is
enabled on your licence. An unlicensed request returns `403` with
`EVENT_MARKET_NOT_LICENSED`.

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/validation-reference/events/search` | Search active event markets |
| `GET` | `/validation-reference/events/contracts` | List active event-market contracts |

### Staged What-If

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/portfolios/stage` | Validate and save a changed portfolio |
| `POST` | `/portfolios/stage/submit` | Compare the stage with a stored baseline |

---

## POST `/portfolios`

Submit one or more accounts with positions and receive margin calculations synchronously.

### Request Parameters

All parameters are set at the top level of the JSON request body alongside the `portfolio` array.

| Parameter                     | Type            | Default               | Description                                                                                                                                    |
| ----------------------------- | --------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `portfolio`                   | `array`         | _required_            | Array of position objects (see [Position Types](#position-types))                                                                              |
| `calculation_type`            | `string`        | `"all"`               | Calculation modes: `"margins"`, `"analytics"`, `"simm"`, `"all"`. Combine with commas, e.g. `"margins,analytics"`                              |
| `vendor_symbology`            | `string`        | `"clearing"`          | Position symbology format: `"clearing"`, `"globex"`, `"ion"`, `"gmi"`, `"tt_new"`. `"globex"` reads CME Group positions from their Globex codes and every other venue from clearing |
| `cme_symbology`               | `string`        | `"clearing"`          | **Deprecated.** `"globex"` here does what `vendor_symbology: "globex"` does; send that instead. Still honoured |
| `currency_code`               | `string`        | `"USD"`               | Base currency for aggregated results (ISO 4217). Supported: `USD`, `EUR`, `GBP`, `JPY`, `CHF`, `AUD`, `CAD`, `BRL`, `CNH`, `HKD`, `INR`, `NZD` |
| `bdate`                       | `integer`       | previous business day | Calculation date in `YYYYMMDD` format                                                                                                          |
| `price_date`                  | `integer`       | previous business day | Price date in `YYYYMMDD` format                                                                                                                |
| `cycle_code`                  | `string`        | —                     | Exchange cycle code                                                                                                                            |
| `use_closest_match`           | `boolean`       | `true`                | Auto-correct minor errors in expiry or strike by matching to the nearest valid contract                                                        |
| `use_closest_active`          | `boolean`       | `true`                | Restrict that substitution to expiries the venue is still quoting. Modifies `use_closest_match`; has no effect when it is `false` |
| `pnl_details`                 | `boolean`       | `false`               | Cache the full historical P&L vector for downstream analysis                                                                                   |
| `in_memory`                   | `boolean`       | `false`               | Process the request in-memory without persisting results                                                                                       |
| `is_live`                     | `boolean`       | `true`                | Mark this as a live portfolio                                                                                                                  |
| `risk_free_rate`              | `number`        | validated ETD rate, otherwise `0.01` | Optional portfolio-wide analytics override. When omitted, validated ETD options retain their maturity-matched rate. `free_risk_rate` is accepted as a deprecated alias until 2026-12-05                              |
| `request_id`                  | `string` (UUID) | auto-generated        | User-defined UUID to track the request                                                                                                         |
| `memo`                        | `string`        | —                     | Free-text memo attached to the request                                                                                                         |
| `risk_metrics`                | `object`        | —                     | Configuration for analytics calculations (see below)                                                                                           |
| `simm_metrics`                | `object`        | —                     | Configuration for SIMM calculations (see below)                                                                                                |
| `stress_sensitivities`        | `object`        | —                     | Configuration for stress scenario analysis (see below)                                                                                         |
| `stress_test_enabled`         | `boolean`       | `false`               | Enable stress testing on the portfolio                                                                                                         |
| `stress_test_details_enabled` | `boolean`       | `false`               | Include detailed stress test drill-down                                                                                                        |
| `pricing`                     | `object`        | —                     | Deprecated and ignored. Live pricing follows the environment's Market Data licence, not a per-portfolio flag; the key is still accepted   |
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
| `option_pnl_method`               | `string`  | `"delta"`         | How a vanilla option's historical P&L is built: `"delta"` scales each historical move of the underlying by today's delta; `"historical-revaluation"` reprices today's option under each date's historical underlying and implied-volatility move, so gamma and vega count. Options without a usable volatility history keep the delta approximation and are listed in the response's `option_pnl_provenance` |
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

## POST `/portfolios/optimize`

Run CME rates cross-margin optimization for one or more accounts. The request uses the same shape as `POST /portfolios`, but at least one eligible CME listed-rates future must include `"cross_margin": true`. Cleared-rates exposure can be supplied as trade-level IRS positions or as a signed DV01 ladder. The cmerates engine must be enabled on the client's licence.

The response reports three comparable totals for each account:

| Field | Description |
| ----- | ----------- |
| `baseline` | Listed futures remain in the listed margin model |
| `all_candidates_to_seq` | Every eligible future is allocated to cleared rates |
| `optimized` | Lowest-margin allocation found by the optimizer |
| `legs` | Per-future recommended allocation, including lots moved and lots left in listed margin |
| `net_ladder` | Net cleared-rates ladder used in the calculation |

Each total contains `seg_span`, `seq_hvar`, and `total`. The candidate and optimized totals also contain `saving` and `saving_pct` relative to baseline. See [the trade-level IRS example](python/12_cme_etd_cleared_rates_optimization.py) and [the delta-ladder example](python/13_cme_delta_ladder_optimization.py).

---

## Batch Processing

For large portfolios or high-volume workloads, use the batch endpoint. It accepts the same payload as `POST /portfolios` and processes it in the background instead of holding a request open for the length of the calculation.

The flow is four steps:

1. `POST /portfolios/batch` -- returns `202` with a `batch_id`
2. `GET /portfolios/batch/{batch_id}` -- poll until `status` is terminal
3. `GET /portfolios/batch/{batch_id}/results` -- every account the batch calculated
4. `GET /results` -- optional, the full drill-down for one account

### How it works

`POST /portfolios/batch` does not calculate anything. It stores your payload, queues a job and answers `202` immediately, which is why the response carries a `batch_id` and nothing else.

A worker then picks the job up and splits the portfolio into chunks by account. Chunk sizes are not fixed: the platform divides available worker memory by the response sizes each margin engine has actually been producing, so the same portfolio may be three chunks on one run and forty on the next. Each chunk is calculated independently and stored under its own internal `request_id`.

Two consequences matter to a caller:

- **Chunking is invisible, and you should keep it that way.** `GET /portfolios/batch/{batch_id}/results` answers at the level you submitted, so you never need to know how the portfolio was divided.
- **A `request_id` sent in the payload is not used.** `POST /portfolios` honours one; `POST /portfolios/batch` assigns its own to each chunk. Track your submission by `batch_id`.

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

### GET `/portfolios/batch/{batch_id}`

Poll the status of a batch job.

**Response**:

```json
{
    "batch_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "completed",
    "created_at": "2025-01-03T09:31:14Z",
    "completed_at": "2025-01-03T09:33:02Z",
    "runtime_ms": 108431,
    "completed_pct": 100,
    "request_ids": ["1f0a...", "6c42...", "b7d9..."]
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
| `request_ids`    | `string[]`| The IDs the batch's results are stored under, one per chunk. Present only once `status` is terminal. Needed only for the drill-down described below |

### GET `/portfolios/batch/{batch_id}/results`

Every account the batch calculated, in one call.

`POST /portfolios/batch` splits a portfolio into chunks and calculates each independently. Chunk sizes are chosen from engine response sizes and worker memory, so the same portfolio may be three chunks today and forty tomorrow. This endpoint answers at the level you submitted -- the batch -- and returns the account-level figures for all of it.

| Parameter | Type      | Default | Description                                        |
| --------- | --------- | ------- | ---------------------------------------------------- |
| `limit`   | `integer` | `5000`  | Maximum accounts to return. Capped at 20,000       |
| `offset`  | `integer` | `0`     | Accounts to skip, for paging through a large book  |

**Response**:

```json
{
    "batch_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "completed",
    "total": 1284,
    "limit": 5000,
    "offset": 0,
    "results": [
        {
            "account_code": "Account 001",
            "portfolio_id": "12a09fb7c8e61a6a7201938225ce71e9",
            "request_id": "af59a90f-f294-4080-8a36-1d16358ca8d3",
            "submitted_time": "2025-01-03T09:33:01Z",
            "status": "live",
            "source": "live",
            "initial_margin": 225110.06,
            "requirement": 225110.06,
            "gross_margin": 225110.06,
            "gross_requirement": 225110.06,
            "option_liquidation_value": 0,
            "additional_margin": 0,
            "value_at_risk": 0,
            "stress_loss": 0,
            "exceptions": 0,
            "closest_matches": 0
        }
    ]
}
```

`total` is the account count for the whole batch, before `limit` and `offset` are applied. Page until `offset + len(results)` reaches it.

`source` says where a row's figures came from, and it matters:

| `source`    | Meaning                                                                                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `"live"`    | The account still carries this batch's calculation, so every field above is populated                                                                      |
| `"history"` | A later calculation has replaced the account's current figures. The durable record keeps `initial_margin`, `option_liquidation_value`, `additional_margin`, `value_at_risk`, `stress_loss`, `exceptions` and `closest_matches`; `requirement`, `gross_margin` and `gross_requirement` come back `null` rather than as a zero you would read as a real number |

In practice a batch fetched after it finishes is entirely `live`. Rows turn `history` when you re-read an older batch whose accounts have since been recalculated.

### Drill-down: `GET /results`

The endpoint above returns account totals. For the full calculation detail of one account -- the per-engine breakdowns, the priced positions, the exceptions -- use `GET /results`:

| Parameter      | Type     | Required | Description                                                                          |
| -------------- | -------- | -------- | ------------------------------------------------------------------------------------ |
| `request_id`   | `string` | yes      | The `request_id` on the account's row above, or any id from the status response's `request_ids` |
| `portfolio_id` | `string` | --       | One account: the `portfolio_id` on its row above, which is `md5(account_code)` (`md5(account_code + sub_account_code)` for a sub-account). Omit to get every account calculated under that `request_id` |

The response is the same per-account result object `POST /portfolios` returns synchronously.

Pass `portfolio_id` whenever you want a single account. Omitting it returns the whole chunk, which for a large book can be tens of megabytes.

A `request_id` supplied in the request body is honoured by `POST /portfolios` but not by `POST /portfolios/batch`, which assigns its own to each chunk.

### Reading a book rather than a batch

`GET /results/accounts` returns one row per live account you own, with the same headline figures, reflecting each account's most recent calculation whatever batch produced it. Use it to read current state; use the batch endpoint to read the output of one submission.

---

## Stress Scenarios

Use `GET /stress-test/scenarios` to list the built-in and caller-owned scenarios
available to your API key. Create one or more caller-owned scenarios with
`POST /stress-test/scenarios`:

```json
[
    {
        "scenario_name": "Equity risk-off",
        "scenario_definition": {
            "sector": {
                "Equity": { "underlying": -0.10, "volatility": 0.20 }
            }
        }
    }
]
```

The response contains the assigned IDs:

```json
{ "scenario_ids": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"] }
```

Pass one ID as `scenario_id` to `DELETE /stress-test/scenarios`. Built-in
scenarios cannot be deleted. To run the available scenarios, set
`stress_test_enabled: true` on `POST /portfolios`. Set
`stress_test_details_enabled: true` when you also need position-level detail.

Scenario rules may target `sector`, `sub_sector`, `underlying`, or `expiry`.
The most specific matching rule wins.

---

## Contract Discovery and Validation

Build valid portfolio rows from the reference endpoints instead of hard-coding
contract values:

1. List exchanges with `GET /validation-reference/exchanges`.
2. Select a contract with `GET /validation-reference/contracts/{exchange_code}`.
3. Select its type, expiry, and option strike from the corresponding endpoints.
4. Send the completed payload to `POST /validation-reference/portfolios` for
   strict validation before calculating it.

Path values must be URL encoded. Expiry and contract formats can differ by
venue, so use the values returned by the API unchanged.

The specialised reference endpoints provide accepted values for fixed income,
cleared interest-rate swaps, rates delta ladders, and FX:

```text
GET /validation-reference/fi-reference
GET /validation-reference/irs-reference
GET /validation-reference/ladder-reference
GET /validation-reference/fx-symbols
```

### Event-market discovery

Event markets are licence-gated by exchange. Search the enabled venue before
building the position:

```bash
curl -sS "$C9_API_ENDPOINT/validation-reference/events/search?exchange=KALSHI&q=Apple&limit=20" \
  -H "Authorization: Bearer $C9_API_SECRET"
```

Use `GET /validation-reference/events/contracts?exchange=KALSHI` when you want
up to 200 active contracts without a search term. Both endpoints return `403`
with `EVENT_MARKET_NOT_LICENSED` when the venue is not enabled on your licence.

---

## Position Types

The `portfolio` array supports eight position types. You can mix different types within a single request across multiple accounts.

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
| `contract_type`    | `string`         | yes      | `"FUT"` / `"F"` / `"Future"` for futures, `"CALL"` for call options, `"PUT"` for put options, `"CASH"` for a cash contract (a single stock, ETF or index at OCC, TMX, Eurex, Euronext …) |
| `contract_expiry`  | `string`         | futures and options | Expiry date. Accepts `YYYYMM`, `YYYYMMDD`, or `MMM-YY` formats. Omit for a cash contract, which has none |
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
| `cross_margin`     | `boolean`        | no       | Elect an eligible CME listed-rates future for `/portfolios/optimize`                          |
| `cross_margin_dv01`| `string\|number` | no       | Optional per-lot DV01 override for optimization                                               |
| `cross_margin_tenor` | `string\|number` | no     | Optional cleared-rates tenor override                                                         |

```json
{
    "account_code": "Account 001",
    "exchange_code": "NYMEX",
    "contract_code": "CL",
    "contract_type": "FUT",
    "contract_expiry": "202712",
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
| `contract_type`    | `string`         | no       | Typically `"BOND"`. Use `"UST"` for FICC-eligible USD Treasuries |
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

### Event Markets

Binary event contracts from supported event exchanges. Use `side` and `quantity`, or provide a signed `net_position`. Event margin and analytics are returned together when `calculation_type` includes `margins`. Discovery, validation, and calculation are available only when the requested exchange is enabled on your licence.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `account_code` | `string` | yes | Internal account identifier |
| `market_type` | `string` | one venue signal | `"EVENT"` |
| `exchange_code` | `string` | one venue signal | `"KALSHI"` or `"FORECASTEX"` |
| `ticker` | `string` | yes | Exchange event ticker |
| `side` | `string` | with `quantity` | `"YES"` or `"NO"` |
| `quantity` | `number` | with `side` | Number of contracts |
| `net_position` | `number` | alternative | Signed contracts, positive for yes and negative for no |
| `price_dollars` | `number` | no | Optional mark between 0 and 1 dollars |
| `netting_enabled` | `boolean` | no | Enable supported event netting |
| `currency_code` | `string` | no | Result currency, normally `"USD"` |

### Cleared Interest Rate Swaps

Trade-level cleared swaps used by the CME cleared-rates margin model.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `account_code` | `string` | yes | Internal account identifier |
| `clearing_house` | `string` | yes | Clearing house, for example `"CME"` |
| `trade_id` | `string` | no | External trade identifier |
| `type` | `string` | no | `"VANILLA"`, `"OIS"`, `"ZERO_COUPON"`, `"BASIS"`, or `"FRA"` |
| `direction` | `string` | yes | `"PAY"` or `"RECEIVE"` fixed |
| `notional` | `number` | yes | Trade notional |
| `currency` | `string` | no | Trade currency, normally `"USD"` |
| `effective_date` | `string` | yes | Effective date in `YYYYMMDD` format |
| `maturity_date` | `string` | yes | Maturity date in `YYYYMMDD` format |
| `fixed_rate` | `number` | yes | Fixed rate as a percentage, for example `3.5` for 3.5 percent |
| `float_index` | `string` | yes | Floating index, for example `"USD-SOFR-COMPOUND"` |
| `pay_frequency` | `string` | no | Fixed payment frequency, for example `"6M"` |

### Rates Delta Ladder

A cleared-rates exposure supplied directly as signed DV01 buckets instead of trade-level swaps.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `account_code` | `string` | yes | Internal account identifier |
| `index` | `string` | yes | Curve index, for example `"USD_SOFR_1D_ERS"` |
| `tenor` | `string` | yes | Bucket tenor as a day count, for example `"1826D"` |
| `dv01` | `number` | yes | Signed currency amount per basis point |

### FX Positions

Foreign exchange positions.

| Field           | Type     | Required | Description                                         |
| --------------- | -------- | -------- | --------------------------------------------------- |
| `account_code`  | `string` | yes      | Internal account identifier                         |
| `currency_pair` | `string` | yes      | Currency pair (e.g. `"EUR_USD"`, `"GBP_JPY"`)       |
| `contract_type` | `string` | yes      | `"FX"`                                             |
| `expiry`        | `string` | yes      | Maturity date                                       |
| `amount`        | `number` | yes      | Notional amount (positive = long, negative = short) |

```json
{
    "account_code": "Account 003",
    "currency_pair": "EUR_USD",
    "contract_type": "FX",
    "expiry": "20271231",
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

### OCC Accounts

| Code | Description |
| ---- | ----------- |
| `REGT` | Strategy-based Reg T margin. Recognised strategies receive fixed formulas and requirements are added together |
| `C` | Customer portfolio margin using risk-based TIMS scenarios and portfolio offsets |

Reg T and TIMS are mutually exclusive within an account. To compare them consistently, submit the same OCC cash and options book under two account codes, as shown in [the Python comparison](python/09_reg_t_vs_portfolio_margin.py). Account eligibility and any broker house requirement remain outside the calculation request.

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
| `delivery_margin`              | `number`  | ICE Clear Europe delivery-margin component in result currency      |
| `cvm`                          | `number`  | Contingent variation margin component in result currency           |
| `sellers_security`             | `number`  | Seller's security component in result currency                     |
| `buyers_security`              | `number`  | Buyer's security component in result currency                      |
| `value_at_risk`                | `number`  | Portfolio Value-at-Risk (when analytics requested)                |
| `vm_at_risk`                   | `number`  | Worst expected variation-margin outflow over the MPOR at the configured confidence level (the P&L VaR) |
| `im_at_risk`                   | `number?` | Worst expected initial-margin increase over the MPOR at the configured confidence level, under the environment's selected methodology |
| `stress_im`                    | `number?` | The same figure under the worst move observed in the window rather than the confidence-level quantile; always at or above `im_at_risk` |
| `im_at_risk_basis`             | `string?` | Methodology behind `im_at_risk`: `var_scaling`, `scan_elasticity`, `margin_history`, or `engine_replay_unavailable`; `null` when no figure is available |
| `im_at_risk_breakdown`         | `array?`  | Per venue group and currency contribution to `im_at_risk` (`var_scaling` / `scan_elasticity` only) |
| `im_at_risk_excluded`          | `array?`  | Margin carrying no scaling factor, and therefore excluded from `im_at_risk`, listed rather than dropped |
| `stress_loss`                  | `number`  | Worst historical daily loss (when analytics requested)            |
| `option_pnl_provenance`        | `object?` | How each vanilla option's historical P&L was built under `risk_metrics.option_pnl_method`: `requested_method`, `historical_positions`, `direct_positions` (own volatility history), `proxy_positions` (a curated proxy's history, listed in `proxy_contracts`), `delta_fallback_positions` and `fallbacks` (`position_id`, `contract_id`, `reason` in `missing_volatility_history`, `insufficient_volatility_history`, `invalid_revaluation_input`). A fallback is a priced position, not an error. Absent on results calculated before the field existed |
| `dv01`                         | `number`  | Dollar value of a basis point (when analytics requested)          |
| `additional_margin`            | `number`  | Add-on charges, including converted delivery-period components     |
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
| `margin_by_cmerates`           | `array`   | CME cleared-rates margin and net-ladder detail                    |
| `margin_by_events`             | `array`   | Event-market margin by event contract                             |
| `event_risk`                   | `object`  | Event VaR, expected shortfall, stress, scenarios, probability shocks, and coverage |
| `risk_components`              | `object`  | Reconciliation of event and conventional risk components          |
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
| `venue_group_code`         | `string` | Venue group the margin was charged for (e.g. `"CBOT"`, `"NYMEX"`, `"ICE.EU"`). Added 2026-07; rows are grouped at this granularity, so a CME Group portfolio reports separate `CBOT` / `CME` / `COMEX` / `NYMEX` rows where it previously reported one. Summed figures across rows are unchanged |
| `clearing_org`             | `string` | Clearing house code (e.g. `"CME"`, `"ICE"`, `"EUREX"`). Equal to `venue_group_code` unless the clearing house is a separate entity from the venue (`"LCH"` clears `FMX`, `"ECC"` clears `EEX`, `"FICC"` has no listing venue) |
| `result_type`              | `string` | Margin model used (e.g. `"span"`, `"span2"`, `"eurexpme"`) |
| `currency_code`            | `string` | Local currency of the clearing house                       |
| `fxrate`                   | `number\|null` | FX rate used for USD conversion. `null` means the rate is unavailable and this row contributes zero to converted aggregates |
| `initial_margin`           | `number` | Margin requirement for this CCP                            |
| `option_liquidation_value` | `number` | Option liquidation value at this CCP                       |
| `delivery_margin`          | `number` | ICE Clear Europe delivery-margin component in row currency  |
| `cvm`                      | `number` | Contingent variation margin component in row currency       |
| `sellers_security`         | `number` | Seller's security component in row currency                 |
| `buyers_security`          | `number` | Buyer's security component in row currency                  |
| `cross_model_offset`       | `number` | Cross-model offset credit, if applicable                   |

`margin_by_contract` rows use the same nullable `fxrate` convention while
retaining their native-currency margin figures.

### `margin_by_irm2_3_delivery` Element

| Field                    | Type     | Description                                     |
| ------------------------ | -------- | ----------------------------------------------- |
| `result_type`            | `string` | Margin model, `"irm2_3"`                        |
| `clearing_org`           | `string` | Clearing house, `"ICE.EU"`                      |
| `currency_code`          | `string` | Engine/result currency                          |
| `delivery_currency_code` | `string` | Raw component currency before conversion        |
| `exchange`               | `string` | Exchange code                                   |
| `contract_code`          | `string` | Contract code                                   |
| `contract_name`          | `string` | Contract description                            |
| `sector`                 | `string` | Sector                                          |
| `sub_sector`             | `string` | Sub-sector                                      |
| `delivery_margin`        | `number` | Raw ICE Clear Europe delivery-margin component  |
| `cvm`                    | `number` | Raw contingent variation margin component       |
| `sellers_security`       | `number` | Raw seller's security component                 |
| `buyers_security`        | `number` | Raw buyer's security component                  |

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

## What-If Analysis

Compare a modified portfolio against one you have already submitted, without
disturbing the original. Stage the changed portfolio, then submit it naming the
earlier `request_id` as the baseline.

### POST `/portfolios/stage`

The stage endpoint accepts the same tabular row shape as the portfolio loader.
For a simple ETD comparison, each row is ordered as:

```text
line_id, account_code, exchange_code, contract_code, contract_type,
contract_expiry, contract_strike, net_position, account_type
```

```json
{
    "type": "etd",
    "data": [
        ["0", "WHAT_IF_ACCOUNT", "ICE.EU", "B", "FUT", "DEC-27", "", "120", "H"]
    ],
    "idx": [0],
    "errors": [],
    "vendor_symbology": "clearing"
}
```

The API validates the rows, saves the caller's stage, and returns the standardised
rows plus any cell error coordinates:

```json
{
    "request_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "data": [["0", "WHAT_IF_ACCOUNT", "ICE.EU", "B", "FUT", "DEC-27", "", "120", "H"]],
    "errors": []
}
```

Inspect `errors` before submitting the comparison. Calling this endpoint again
for the same loader type replaces that section of your current stage.
An event-market stage is available only when its exchange is enabled on your
licence. An unlicensed event stage returns `403` with `EVENT_MARKET_NOT_LICENSED`.

### POST `/portfolios/stage/submit`

```json
{
    "action": "what-if",
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "portfolio_id": "PF-1"
}
```

| Field          | Type     | Description                                                              |
| -------------- | -------- | ------------------------------------------------------------------------ |
| `action`       | `string` | Must be `"what-if"` for a comparison                                      |
| `request_id`   | `string` | The earlier submission to compare against. This is the "before" side      |
| `portfolio_id` | `string` | Which portfolio of that submission to compare                            |

The staged portfolio is calculated synchronously and diffed against the stored
results of `request_id`. Throughout the response, `_1` is the baseline and `_2`
is the staged portfolio.

```json
{
    "what_if": {
        "summary": {
            "currency_code": "USD",
            "gross_requirement_1": 1250000, "gross_requirement_2": 1310000,
            "gross_margin_1": 1400000,      "gross_margin_2": 1465000,
            "option_liquidation_value_1": 150000, "option_liquidation_value_2": 155000,
            "additional_margin_1": 20000,   "additional_margin_2": 22000,
            "value_at_risk_1": 310000,      "value_at_risk_2": 330000,
            "dv01_1": 4200,                 "dv01_2": 4550
        },
        "margin_by_contract": [
            {
                "clearing_org": "CME", "result_type": "span", "exchange": "CBOT",
                "cc_code": "ZC", "cc_name": "Corn", "sector": "Agriculture",
                "sub_sector": "Grains", "currency_code": "USD",
                "im_usd_1": 210000, "im_usd_2": 245000,
                "olv_usd_1": 0, "olv_usd_2": 0
            }
        ],
        "portfolio": []
    }
}
```

`summary` is the portfolio-level before/after pair. `margin_by_contract` is keyed
on clearing organisation, exchange and contract code, **converted to USD** so the
two sides are comparable, and carries a row for every contract on either side — a
contract only in the baseline reports `im_usd_2: 0`, and one only in the staged
portfolio reports `im_usd_1: 0`, so positions opened and closed both show up.
`portfolio` is the same comparison at position level.

**Authorisation.** The stored baseline must be visible to the authenticated API
key and within its permitted account codes.

| Status | Meaning                                                                        |
| ------ | ------------------------------------------------------------------------------ |
| `403`  | You are not authorised to run a what-if on that portfolio                      |
| `409`  | The baseline results have aged out of storage — re-submit the portfolio first   |

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
            "contract_expiry": "DEC-27",
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

# Fetch every account the batch calculated, in one call
results = requests.get(
    f"{C9_API_ENDPOINT}/portfolios/batch/{batch_id}/results",
    headers=HEADERS
).json()

for account in results["results"]:
    print(f"{account['account_code']}: ${account['initial_margin']:,.2f}")

# Full drill-down for one account
detail = requests.get(
    f"{C9_API_ENDPOINT}/results",
    headers=HEADERS,
    params={
        "request_id": results["results"][0]["request_id"],
        "portfolio_id": results["results"][0]["portfolio_id"],
    }
).json()
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
            "contract_expiry": "DEC-27",
            "net_position": "100",
            "account_type": "H"
        }
    ]
}'
```

See the language-specific directories for complete runnable examples:

| Directory     | Examples                                                                                            |
| ------------- | --------------------------------------------------------------------------------------------------- |
| `python/`     | Basic margin, ageing, batch, SIMM, stress, Reg T vs TIMS, event risk, fixed income and FICC, CME rates optimization |
| `javascript/` | Basic margin, batch processing                                                                      |
| `curl/`       | Basic margin, batch processing                                                                      |
| `csharp/`     | Basic margin                                                                                        |
| `r/`          | Basic margin                                                                                        |

The focused Python analytics examples are:

| File | Demonstrates |
| ---- | ------------ |
| [`09_reg_t_vs_portfolio_margin.py`](python/09_reg_t_vs_portfolio_margin.py) | Identical OCC cash and options books under Reg T and TIMS |
| [`10_event_market_analytics.py`](python/10_event_market_analytics.py) | Event margin, VaR, expected shortfall, settlement stress, scenarios, and probability shocks |
| [`11_fixed_income_analytics_and_ficc.py`](python/11_fixed_income_analytics_and_ficc.py) | Treasury VaR, DV01, sensitivity stress, configured stress tests, and FICC margin |
| [`12_cme_etd_cleared_rates_optimization.py`](python/12_cme_etd_cleared_rates_optimization.py) | CME listed rates plus trade-level cleared swaps, margin and optimization |
| [`13_cme_delta_ladder_optimization.py`](python/13_cme_delta_ladder_optimization.py) | CME listed rates plus a DV01 ladder, margin and optimization |

Replace the `C9_API_ENDPOINT` and `C9_API_SECRET` placeholders at the top of an example, then run it directly:

```bash
python3 python/09_reg_t_vs_portfolio_margin.py
```

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
        "mode": "absolute",
        "option_pnl_method": "delta"
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
            "contract_expiry": "DEC-27",
            "net_position": "500",
            "account_type": "H"
        },
        {
            "account_code": "Account 001",
            "exchange_code": "NYMEX",
            "contract_code": "LO",
            "contract_type": "CALL",
            "contract_expiry": "DEC-27",
            "contract_strike": "50.1",
            "net_position": "-1000",
            "account_type": "H"
        },
        {
            "account_code": "Account 002",
            "exchange_code": "EUREX",
            "contract_code": "FDAX",
            "contract_type": "FUT",
            "contract_expiry": "17-DEC-27",
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
            "contract_type": "FX",
            "expiry": "20271231",
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
