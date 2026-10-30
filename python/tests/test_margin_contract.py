import contextlib
import io
import pathlib
import runpy
import unittest

from test_openapi_examples import OPENAPI, validate
from test_analytics_examples import FakeResponse, run_example
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]


class MarginContractTest(unittest.TestCase):
    def test_public_results_declare_the_trio_and_provenance(self):
        for name in ['AccountResult', 'MarginByCCP', 'MarginByContract', 'MarginBySpan', 'BatchResultRow']:
            fields = OPENAPI['components']['schemas'][name]['properties']
            for key in ['initial_margin', 'maintenance_margin', 'margin', 'margin_contract_version', 'margin_basis', 'margin_availability']:
                self.assertIn(key, fields, (name, key))
            for selected in [0, None, 125]:
                validate(name, {'initial_margin': 110, 'maintenance_margin': 100, 'margin': selected,
                                'margin_contract_version': 2, 'margin_basis': 'custom',
                                'margin_availability': {'maintenance_margin': {'status': 'available'}}})

    def test_example_preserves_selected_zero_null_and_legacy_values(self):
        example = runpy.run_path(ROOT / 'python/15_margin_fields.py')
        selected = example['selected_margin']
        self.assertEqual(selected({'initial_margin': 110}), 110)
        self.assertEqual(selected({'initial_margin': 110, 'margin': 100}), 100)
        self.assertEqual(selected({'initial_margin': 110, 'margin': 0}), 0)
        self.assertIsNone(selected({'initial_margin': 110, 'margin': None}))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            example['print_margins']({'account_code': 'Example', 'currency_code': 'USD',
                'initial_margin': 110, 'maintenance_margin': 0, 'margin': 125,
                'margin_contract_version': 2, 'margin_availability': {
                    'maintenance_margin': {'status': 'unavailable', 'reason': 'Native model does not supply maintenance.'}}})
        self.assertIn('Applicable margin: USD 125.00', output.getvalue())
        self.assertIn('Initial margin: USD 110.00', output.getvalue())
        self.assertIn('Maintenance margin: unavailable', output.getvalue())
        self.assertNotIn('Maintenance margin: USD 0.00', output.getvalue())

    def test_batch_total_does_not_substitute_initial_for_zero_or_null(self):
        base = {'currency_code': 'USD', 'request_id': 'request', 'portfolio_id': 'portfolio', 'source': 'live', 'status': 'done'}
        rows = [{**base, 'account_code': 'Zero', 'initial_margin': 110, 'margin': 0},
                {**base, 'account_code': 'Unknown', 'initial_margin': 110, 'margin': None}]
        output = io.StringIO()
        replies = [FakeResponse({'status': 'completed', 'completed_pct': 100, 'runtime_ms': 1}),
                   FakeResponse({'results': rows, 'total': 2}), FakeResponse([rows[0]])]
        with patch('requests.post', return_value=FakeResponse({'batch_id': 'batch'})), \
             patch('requests.get', side_effect=replies), contextlib.redirect_stdout(output):
            runpy.run_path(ROOT / 'python/02_batch_processing.py')
        self.assertIn('Total applicable margin across batch: USD unavailable', output.getvalue())
        self.assertIn('Zero: USD 0.00', output.getvalue())
        self.assertNotIn('110.00', output.getvalue())

    def test_gross_net_example_compares_selected_charge(self):
        _, output = run_example('07_sub_accounts_and_gross_margin.py', [{'data': [
            {'account_code': 'Example', 'portfolio_id': 'example', 'initial_margin': 110,
             'margin': 125, 'gross_margin': 250}]}])
        self.assertIn('125.00', output)
        self.assertNotIn('offset=$      140.00', output)


if __name__ == '__main__':
    unittest.main()
