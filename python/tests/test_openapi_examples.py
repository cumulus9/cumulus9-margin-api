import pathlib
import unittest

import jsonschema
import yaml


ROOT = pathlib.Path(__file__).resolve().parents[2]
OPENAPI = yaml.safe_load((ROOT / "open-api-schema.yaml").read_text())


def validate(schema_name, value):
    schema = {**OPENAPI, "$ref": f"#/components/schemas/{schema_name}"}
    jsonschema.validate(value, schema)


class OpenApiExamplesTest(unittest.TestCase):
    def test_stress_scenario_supports_underlying_shock_types(self):
        validate(
            "StressScenarioInput",
            {
                "scenario_name": "S&P 500 shock",
                "scenario_definition": {
                    "underlying": {
                        "S&P 500 Index": {
                            "type": "Relative",
                            "volatility_type": "Absolute",
                            "override": True,
                            "underlying": -0.15,
                            "volatility": 0.50,
                        }
                    }
                },
            },
        )

    def test_stress_scenario_supports_expiry_nested_under_underlying(self):
        validate(
            "StressScenarioInput",
            {
                "scenario_name": "S&P 500 expiry shock",
                "scenario_definition": {
                    "expiry": {
                        "S&P 500 Index": {
                            "203012": {
                                "type": "Relative",
                                "override": True,
                                "underlying": -0.30,
                                "volatility": 1.00,
                            }
                        }
                    }
                },
            },
        )

    def test_etd_position_accepts_numeric_option_strike(self):
        validate(
            "ETDPosition",
            {
                "account_code": "OCC_REG_T",
                "exchange_code": "OCC",
                "contract_code": "AAPL",
                "contract_type": "CALL",
                "contract_expiry": "20271217",
                "contract_strike": 340,
                "net_position": -1,
                "account_type": "REGT",
            },
        )

    def test_event_stage_documents_licence_failure(self):
        responses = OPENAPI["paths"]["/portfolios/stage"]["post"]["responses"]
        self.assertEqual(
            responses["403"]["$ref"],
            "#/components/responses/EventMarketNotLicensed",
        )


if __name__ == "__main__":
    unittest.main()
