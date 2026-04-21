# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.
#
# ---------------------------------------------------------------------------
# Stress testing sample
# ---------------------------------------------------------------------------
# This script walks through the full stress testing flow:
#
#   1. Delete any client-defined scenarios left over from previous runs.
#   2. Upload a fresh batch of scenario definitions     (POST /stress-test/scenarios).
#   3. Submit a portfolio and request stress results    (POST /portfolios).
#   4. Flatten the response into a single tidy DataFrame with one row per
#      (account, position, scenario) combination.
#
# Anatomy of a scenario_definition
# --------------------------------
# A scenario_definition is a JSON object that can declare shocks at four
# levels of granularity. For each position the engine picks the *most
# specific* match and applies the shocks declared at that level:
#
#     expiry   >   underlying   >   sub_sector   >   sector
#
# Each shock block carries an `underlying` number (shock applied to the
# underlying price) and a `volatility` number (shock applied to the implied
# vol). At the `underlying` and `expiry` levels you can additionally set
# `type` to either "Relative" or "Absolute", and `override: True` to force
# the shock to take precedence over broader levels.
#
#   sector      -> applies to every position whose contract sector matches
#                  (e.g. "Equity", "Energy", "Metals").
#   sub_sector  -> narrower than sector (e.g. "Index", "Crude Oil").
#   underlying  -> a specific underlying name (e.g. "S&P 500 Index").
#   expiry      -> a specific underlying AND a specific expiry month (YYYYMM).
#
# All shocks are expressed as fractions: -0.10 means a 10 percent drop when
# type = Relative, or -10 raw units when type = Absolute.
# ---------------------------------------------------------------------------

import requests
import pandas as pd
from tabulate import tabulate

# Credentials -- contact support@cumulus9.com to obtain these.
C9_API_ENDPOINT = "xxxxxxxxxxxxxxxxxx"
C9_API_SECRET = "sk-xxxxxxxxxxxxxxxxxx"

HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {C9_API_SECRET}"}


def post(url: str, data: dict) -> requests.Response:
    response = requests.post(f"{C9_API_ENDPOINT}{url}", headers=HEADERS, json=data)
    response.raise_for_status()
    return response


def get(url: str, params: dict = None) -> requests.Response:
    response = requests.get(f"{C9_API_ENDPOINT}{url}", headers=HEADERS, params=params)
    response.raise_for_status()
    return response


def delete(url: str, params: dict = None) -> requests.Response:
    response = requests.delete(f"{C9_API_ENDPOINT}{url}", headers=HEADERS, params=params)
    response.raise_for_status()
    return response


# ---------------------------------------------------------------------------
# 1. Delete any existing client scenarios
# ---------------------------------------------------------------------------
# GET /stress-test/scenarios returns the merged list of client-defined
# scenarios and Cumulus9 built-in scenarios. DELETE only affects rows owned
# by the caller, so iterating over every id is safe - built-in scenarios
# are untouched and the call is a no-op for them.

existing_scenarios = get("/stress-test/scenarios").json()
for scenario in existing_scenarios:
    delete("/stress-test/scenarios", params={"scenario_id": scenario["scenario_id"]})
print(f"Deleted {len(existing_scenarios)} pre-existing scenarios")


# ---------------------------------------------------------------------------
# 2. Define and upload new scenarios
# ---------------------------------------------------------------------------
# The examples below demonstrate each level of granularity.

scenarios = [
    # ----- sector-level ---------------------------------------------------
    # Applies a -10% underlying shock and a +20% vol shock to every Equity
    # position, and a -5% / +10% shock to every Energy position.
    {
        "scenario_name": "Broad risk-off (sector)",
        "scenario_definition": {
            "sector": {
                "Equity": {"underlying": -0.10, "volatility": 0.20},
                "Energy": {"underlying": -0.05, "volatility": 0.10},
            }
        },
    },
    # ----- sub_sector-level ----------------------------------------------
    # Narrower than sector. `override: True` makes the sub_sector shock
    # take precedence over any matching sector shock for the same position.
    {
        "scenario_name": "Equity index crash (sub_sector)",
        "scenario_definition": {
            "sector": {"Equity": {"underlying": -0.05, "volatility": 0.10}},
            "sub_sector": {"Index": {"override": True, "underlying": -0.20, "volatility": 0.40}},
        },
    },
    # ----- underlying-level ----------------------------------------------
    # Most specific shock that applies regardless of expiry. `type` picks
    # relative (percentage) vs absolute (raw units) shocks.
    {
        "scenario_name": "S&P 500 -15% / vol +50% (underlying)",
        "scenario_definition": {
            "underlying": {
                "S&P 500 Index": {"type": "Relative", "override": True, "underlying": -0.15, "volatility": 0.50}
            }
        },
    },
    # ----- expiry-level (most specific) ----------------------------------
    # Shocks keyed by underlying -> expiry (YYYYMM). Only positions whose
    # underlying AND expiry match are impacted.
    {
        "scenario_name": "S&P 500 Dec-2030 tail event (expiry)",
        "scenario_definition": {
            "expiry": {
                "S&P 500 Index": {
                    "203012": {"type": "Relative", "override": True, "underlying": -0.30, "volatility": 1.00}
                }
            }
        },
    },
]

scenarios_response = post("/stress-test/scenarios", scenarios)
scenarios_ids = scenarios_response.json().get("scenario_ids", [])
print(f"Uploaded {len(scenarios_ids)} scenarios: {scenarios_ids}")


# ---------------------------------------------------------------------------
# 3. Submit the portfolio and request stress tests
# ---------------------------------------------------------------------------
# `stress_test_enabled: True` runs every scenario available to the caller
# (built-in + client-defined). `stress_test_details_enabled: True` asks
# the engine to return the per-position detail block used below.

portfolio = [
    {
        "account_code": "Account 1",
        "exchange_code": "NYMEX",
        "contract_code": "ES",
        "contract_type": "CALL",
        "contract_expiry": "203012",
        "contract_strike": "7000",
        "net_position": 1000,
    },
    {
        "account_code": "Account 1",
        "exchange_code": "NYMEX",
        "contract_code": "CL",
        "contract_type": "FUT",
        "contract_expiry": "203012",
        "net_position": 1000,
    },
]

event = {
    "calculation_type": "all",
    "portfolio": portfolio,
    "use_closest_active": True,
    "stress_test_enabled": True,
    "stress_test_details_enabled": True,
    "free_risk_rate": 0.05,
}

response = post("/portfolios", event)
response_json = response.json()
print("Portfolio response status:", response.status_code)


# ---------------------------------------------------------------------------
# 4. Flatten the response into the target DataFrame
# ---------------------------------------------------------------------------
# Target columns:
#   account_code, position_id, exch_acronym, contract_code, contract_type,
#   expiry, strike, net_position,
#   scenario_name, shock_type, underlying_price, volatility,
#   days_to_maturity, free_risk_rate, underlying_shock, volatility_shock,
#   price_revalued, price_stressed, stress_loss
#
# Data sources per account in the response:
#   account_results["account_code"]              -> top-level account id
#   account_results["portfolio"]                 -> one row per position
#   account_results["stress_tests"]["scenarios"] -> scenario_id -> name map
#   account_results["stress_tests"]["details"]   -> one row per (position, scenario)

POSITION_COLS = ["position_id", "exch_acronym", "contract_code", "contract_type", "expiry", "strike", "net_position"]

DETAIL_COLS = [
    "position_id",
    "scenario_id",
    "shock_type",
    "underlying_price",
    "volatility",
    "days_to_maturity",
    "free_risk_rate",
    "underlying_shock",
    "volatility_shock",
    "price_revalued",
    "price_stressed",
    "stress_loss",
]

FINAL_COLS = [
    "scenario_name",
    "account_code",
    "position_id",
    "exch_acronym",
    "contract_code",
    "contract_type",
    "expiry",
    "strike",
    "net_position",
    "shock_type",
    "underlying_price",
    "volatility",
    "days_to_maturity",
    "free_risk_rate",
    "underlying_shock",
    "volatility_shock",
    "price_revalued",
    "price_stressed",
    "stress_loss",
]


def build_stress_dataframe(response_json: dict) -> pd.DataFrame:
    frames = []
    for account_results in response_json["data"]:
        account_code = account_results.get("account_code")
        stress_tests = account_results.get("stress_tests") or {}
        details = stress_tests.get("details") or []
        scenarios = stress_tests.get("scenarios") or []
        if not details:
            continue

        positions_df = pd.DataFrame(account_results["portfolio"])[POSITION_COLS]
        positions_df["position_id"] = positions_df["position_id"].astype(str)
        positions_df["account_code"] = account_code

        scenarios_df = pd.DataFrame(scenarios)  # scenario_id, scenario_name

        details_df = pd.DataFrame(details)[DETAIL_COLS]
        details_df["position_id"] = details_df["position_id"].astype(str)

        merged = details_df.merge(scenarios_df, on="scenario_id", how="left").merge(
            positions_df, on="position_id", how="left"
        )
        # filter to only the scenarios we uploaded (i.e. exclude pre-existing ones in the system)
        merged = merged[merged["scenario_id"].isin(scenarios_ids)]
        frames.append(merged)

    if not frames:
        return pd.DataFrame(columns=FINAL_COLS)
    return pd.concat(frames, ignore_index=True)[FINAL_COLS]


df = build_stress_dataframe(response_json)
summary_df = (
    df.groupby(["scenario_name", "account_code"], as_index=False)["stress_loss"]
    .sum()
    .sort_values(["scenario_name", "account_code"])
)

print("\nSummary of stress losses by scenario and account:")
print(tabulate(summary_df, headers="keys", tablefmt="grid", showindex=False, floatfmt=".6f"))

# Summary of stress losses by scenario and account:
# +--------------------------------------+----------------+-----------------+
# | scenario_name                        | account_code   |     stress_loss |
# +======================================+================+=================+
# | Broad risk-off (sector)              | Account 1      |  9332542.336585 |
# +--------------------------------------+----------------+-----------------+
# | Equity index crash (sub_sector)      | Account 1      | 18835460.909509 |
# +--------------------------------------+----------------+-----------------+
# | S&P 500 -15% / vol +50% (underlying) | Account 1      | -9718137.407361 |
# +--------------------------------------+----------------+-----------------+
# | S&P 500 Dec-2030 tail event (expiry) | Account 1      |        0.000000 |
# +--------------------------------------+----------------+-----------------+

print("\nDetailed stress test results by scenario, account, and position:")
print(tabulate(df, headers="keys", tablefmt="grid", showindex=False, floatfmt=".6f"))

# Detailed stress test results by scenario, account, and position:
# +--------------------------------------+----------------+---------------+----------------+-----------------------------+-----------------+----------+-------------+----------------+--------------+--------------------+--------------+--------------------+------------------+--------------------+--------------------+------------------+------------------+-----------------+
# | scenario_name                        | account_code   |   position_id | exch_acronym   | contract_code               | contract_type   |   expiry |      strike |   net_position | shock_type   |   underlying_price |   volatility |   days_to_maturity |   free_risk_rate |   underlying_shock |   volatility_shock |   price_revalued |   price_stressed |     stress_loss |
# +======================================+================+===============+================+=============================+=================+==========+=============+================+==============+====================+==============+====================+==================+====================+====================+==================+==================+=================+
# | Broad risk-off (sector)              | Account 1      |             0 | CME            | ES - E-mini S&P 500 Options | CALL            |   203012 | 7000.000000 |           1000 |              |        8287.250000 |     0.197774 |               1220 |         0.050000 |          -0.100000 |           0.200000 |      1611.529734 |      1799.180581 |  9382542.336585 |
# +--------------------------------------+----------------+---------------+----------------+-----------------------------+-----------------+----------+-------------+----------------+--------------+--------------------+--------------+--------------------+------------------+--------------------+--------------------+------------------+------------------+-----------------+
# | Broad risk-off (sector)              | Account 1      |             1 | NYMEX          | CL - Crude Oil Futures      | FUT             |   203012 |  nan        |           1000 |              |          63.810000 |   nan        |               1198 |         0.050000 |          -0.050000 |           0.100000 |        63.810000 |        63.760000 |   -50000.000000 |
# +--------------------------------------+----------------+---------------+----------------+-----------------------------+-----------------+----------+-------------+----------------+--------------+--------------------+--------------+--------------------+------------------+--------------------+--------------------+------------------+------------------+-----------------+
# | Equity index crash (sub_sector)      | Account 1      |             0 | CME            | ES - E-mini S&P 500 Options | CALL            |   203012 | 7000.000000 |           1000 |              |        8287.250000 |     0.197774 |               1220 |         0.050000 |          -0.200000 |           0.400000 |      1611.529734 |      1988.238953 | 18835460.909509 |
# +--------------------------------------+----------------+---------------+----------------+-----------------------------+-----------------+----------+-------------+----------------+--------------+--------------------+--------------+--------------------+------------------+--------------------+--------------------+------------------+------------------+-----------------+
# | Equity index crash (sub_sector)      | Account 1      |             1 | NYMEX          | CL - Crude Oil Futures      | FUT             |   203012 |  nan        |           1000 | relative     |          63.810000 |   nan        |               1198 |         0.050000 |           0.000000 |           0.000000 |        63.810000 |        63.810000 |        0.000000 |
# +--------------------------------------+----------------+---------------+----------------+-----------------------------+-----------------+----------+-------------+----------------+--------------+--------------------+--------------+--------------------+------------------+--------------------+--------------------+------------------+------------------+-----------------+
# | S&P 500 -15% / vol +50% (underlying) | Account 1      |             0 | CME            | ES - E-mini S&P 500 Options | CALL            |   203012 | 7000.000000 |           1000 | relative     |        8287.250000 |     0.197774 |               1220 |         0.050000 |          -0.150000 |           0.500000 |      1611.529734 |      1417.166986 | -9718137.407361 |
# +--------------------------------------+----------------+---------------+----------------+-----------------------------+-----------------+----------+-------------+----------------+--------------+--------------------+--------------+--------------------+------------------+--------------------+--------------------+------------------+------------------+-----------------+
# | S&P 500 -15% / vol +50% (underlying) | Account 1      |             1 | NYMEX          | CL - Crude Oil Futures      | FUT             |   203012 |  nan        |           1000 | relative     |          63.810000 |   nan        |               1198 |         0.050000 |           0.000000 |           0.000000 |        63.810000 |        63.810000 |        0.000000 |
# +--------------------------------------+----------------+---------------+----------------+-----------------------------+-----------------+----------+-------------+----------------+--------------+--------------------+--------------+--------------------+------------------+--------------------+--------------------+------------------+------------------+-----------------+
# | S&P 500 Dec-2030 tail event (expiry) | Account 1      |             0 | CME            | ES - E-mini S&P 500 Options | CALL            |   203012 | 7000.000000 |           1000 | relative     |        8287.250000 |     0.197774 |               1220 |         0.050000 |           0.000000 |           0.000000 |      1611.529734 |      1611.529734 |        0.000000 |
# +--------------------------------------+----------------+---------------+----------------+-----------------------------+-----------------+----------+-------------+----------------+--------------+--------------------+--------------+--------------------+------------------+--------------------+--------------------+------------------+------------------+-----------------+
# | S&P 500 Dec-2030 tail event (expiry) | Account 1      |             1 | NYMEX          | CL - Crude Oil Futures      | FUT             |   203012 |  nan        |           1000 | relative     |          63.810000 |   nan        |               1198 |         0.050000 |           0.000000 |           0.000000 |        63.810000 |        63.810000 |        0.000000 |
# +--------------------------------------+----------------+---------------+----------------+-----------------------------+-----------------+----------+-------------+----------------+--------------+--------------------+--------------+--------------------+------------------+--------------------+--------------------+------------------+------------------+-----------------+
