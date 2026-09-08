import contextlib
import copy
import io
import os
import pathlib
import runpy
import unittest
from unittest.mock import patch


PYTHON_DIR = pathlib.Path(__file__).resolve().parents[1]


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        pass

    def json(self):
        return self.body


def run_example(filename, replies):
    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, copy.deepcopy(kwargs["json"])))
        return FakeResponse(replies[len(calls) - 1])

    output = io.StringIO()
    with patch("requests.post", side_effect=fake_post), contextlib.redirect_stdout(output):
        runpy.run_path(PYTHON_DIR / filename)
    return calls, output.getvalue()


class AnalyticsExamplesTest(unittest.TestCase):
    def test_reporting_currency_example_converts_without_a_gbp_instrument(self):
        response = {"data": [{"currency_version": 1, "currency_code": "GBP", "reporting_fxrate": 0.8,
            "initial_margin": 1600, "margin_by_ccp": [
                {"clearing_org": "CME", "currency_code": "USD", "fxrate": 1, "initial_margin": 1000},
                {"clearing_org": "EUREX", "currency_code": "EUR", "fxrate": 0.9, "initial_margin": 900},
            ]}]}
        with patch.dict(os.environ, {"C9_API_ENDPOINT": "https://example.test", "C9_API_SECRET": "test"}):
            calls, output = run_example("14_reporting_currency.py", [response])
        self.assertEqual(calls[0][1]["currency_code"], "GBP")
        self.assertIn("Initial margin: GBP 1,600.00", output)
        self.assertIn("EUREX: GBP 800.00 (native EUR 900.00)", output)
        self.assertIn("CME: GBP 800.00 (native USD 1,000.00)", output)

    def test_reporting_currency_example_refuses_an_unversioned_response(self):
        with patch.dict(os.environ, {"C9_API_ENDPOINT": "https://example.test", "C9_API_SECRET": "test"}):
            with self.assertRaisesRegex(RuntimeError, "staging reporting-currency version 1"):
                run_example("14_reporting_currency.py", [{"data": [{"currency_code": "GBP", "initial_margin": 800}]}])

    def test_occ_example_posts_identical_books_and_prints_comparison(self):
        response = {
            "data": [
                {"account_code": "OCC_REG_T", "initial_margin": 18500.0},
                {"account_code": "OCC_PORTFOLIO_MARGIN", "initial_margin": 12900.0},
            ]
        }
        calls, output = run_example("09_reg_t_vs_portfolio_margin.py", [response])
        positions = calls[0][1]["portfolio"]
        reg_t = [row for row in positions if row["account_code"] == "OCC_REG_T"]
        tims = [row for row in positions if row["account_code"] == "OCC_PORTFOLIO_MARGIN"]

        self.assertEqual(len(calls), 1)
        self.assertEqual({row["account_type"] for row in reg_t}, {"REGT"})
        self.assertEqual({row["account_type"] for row in tims}, {"C"})
        for left, right in zip(reg_t, tims):
            self.assertEqual(
                {key: value for key, value in left.items() if key not in {"account_code", "account_type"}},
                {key: value for key, value in right.items() if key not in {"account_code", "account_type"}},
            )
        self.assertIn("Reg T initial margin: $18,500.00", output)
        self.assertIn("TIMS minus Reg T: -$5,600.00", output)

    def test_event_example_prints_event_analytics(self):
        response = {
            "data": [{
                "initial_margin": 425.0,
                "event_risk": {
                    "value_at_risk": 120.0,
                    "expected_shortfall": 175.0,
                    "stress_loss": 425.0,
                    "stress_scenario": "full_settlement",
                    "coverage": {"positions_modelled": 2},
                    "scenarios": [{"name": "full_settlement", "pnl": -425.0}],
                    "probability_shocks": {"portfolio": [{"shock": -0.1, "pnl": -80.0}]},
                },
            }]
        }
        calls, output = run_example("10_event_market_analytics.py", [response])

        self.assertEqual(len(calls), 1)
        self.assertEqual({row["currency_code"] for row in calls[0][1]["portfolio"]}, {"USD"})
        self.assertIn("Event initial margin: $425.00", output)
        self.assertIn("Value at risk: $120.00", output)
        self.assertIn("Expected shortfall: $175.00", output)
        self.assertIn("full_settlement", output)

    def test_fixed_income_example_prints_analytics_and_ficc_margin(self):
        response = {
            "data": [{
                "initial_margin": 230000.0,
                "value_at_risk": 210000.0,
                "stress_loss": 315000.0,
                "dv01": 9800.0,
                "margin_by_ccp": [{"result_type": "ficc", "initial_margin": 125000.0}],
                "scenario_analysis": {"summary": [-315000.0, 85000.0]},
                "stress_tests": {
                    "scenarios": [{"scenario_id": "rates-up", "scenario_name": "Rates up"}],
                    "values": [{"scenario_id": "rates-up", "stress_loss": -42000.0}],
                },
            }]
        }
        calls, output = run_example("11_fixed_income_analytics_and_ficc.py", [response])
        payload = calls[0][1]

        self.assertEqual(payload["calculation_type"], "margins,analytics")
        self.assertTrue(payload["stress_test_enabled"])
        self.assertEqual({row["contract_type"] for row in payload["portfolio"]}, {"UST"})
        self.assertIn("FICC initial margin: $125,000.00", output)
        self.assertIn("Value at risk: $210,000.00", output)
        self.assertIn("DV01: $9,800.00 per bp", output)

    def test_cleared_rates_example_posts_margin_then_optimization(self):
        margin = {"data": [{"initial_margin": 750000.0}]}
        optimization = {"data": [{
            "baseline": {"total": 800000.0},
            "optimized": {"total": 610000.0, "saving": 190000.0, "saving_pct": 23.75},
            "legs": [{
                "contract_code": "SR3",
                "lots_to_seq": 150,
                "lots_left_in_seg": 100,
                "recommendation": "MOVE_TO_SEQ",
            }],
        }]}
        calls, output = run_example("12_cme_etd_cleared_rates_optimization.py", [margin, optimization])
        margin_positions = calls[0][1]["portfolio"]
        optimizer_positions = calls[1][1]["portfolio"]

        self.assertEqual([url.rsplit("/", 1)[-1] for url, _ in calls], ["portfolios", "optimize"])
        self.assertTrue(any("clearing_house" in row for row in margin_positions))
        self.assertFalse(any(row.get("cross_margin") is True for row in margin_positions))
        self.assertTrue(any(row.get("cross_margin") is True for row in optimizer_positions))
        self.assertIn("Combined initial margin: $750,000.00", output)
        self.assertIn("Optimized total: $610,000.00", output)

    def test_delta_ladder_example_posts_margin_then_optimization(self):
        margin = {"data": [{"initial_margin": 690000.0}]}
        optimization = {"data": [{
            "baseline": {"total": 720000.0},
            "optimized": {"total": 540000.0, "saving": 180000.0, "saving_pct": 25.0},
            "legs": [{
                "contract_code": "SR3",
                "lots_to_seq": 200,
                "lots_left_in_seg": 50,
                "recommendation": "MOVE_TO_SEQ",
            }],
        }]}
        calls, output = run_example("13_cme_delta_ladder_optimization.py", [margin, optimization])
        margin_positions = calls[0][1]["portfolio"]
        optimizer_positions = calls[1][1]["portfolio"]

        self.assertEqual([url.rsplit("/", 1)[-1] for url, _ in calls], ["portfolios", "optimize"])
        self.assertGreaterEqual(sum("index" in row and "dv01" in row for row in margin_positions), 2)
        self.assertFalse(any("clearing_house" in row for row in margin_positions))
        self.assertFalse(any(row.get("cross_margin") is True for row in margin_positions))
        self.assertTrue(any(row.get("cross_margin") is True for row in optimizer_positions))
        self.assertIn("Combined initial margin: $690,000.00", output)
        self.assertIn("Optimized total: $540,000.00", output)


if __name__ == "__main__":
    unittest.main()
