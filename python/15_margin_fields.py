"""Read selected and typed margins without mistaking unavailable zero for evidence."""
import os
import requests


def selected_margin(row):
    return row['margin'] if 'margin' in row else row.get('initial_margin')


def print_margins(account):
    currency = account.get('currency_code', 'currency unavailable')
    print(account.get('account_code', 'Account'))
    for field, label in [('margin', 'Applicable margin'), ('initial_margin', 'Initial margin'),
                         ('maintenance_margin', 'Maintenance margin')]:
        value = selected_margin(account) if field == 'margin' else account.get(field)
        availability = (account.get('margin_availability') or {}).get(field, {})
        if field != 'margin' and account.get('margin_contract_version') != 2:
            print(f'{label}: legacy typed amount unavailable')
        elif availability.get('status') in ['unavailable', 'not_applicable', 'legacy'] or value is None:
            print(f"{label}: {availability.get('status', 'unavailable')} ({availability.get('reason', 'No supported amount supplied')})")
        else:
            print(f'{label}: {currency} {value:,.2f}')


def main():
    response = requests.post(
        f"{os.environ['C9_API_ENDPOINT']}/portfolios",
        headers={'Authorization': f"Bearer {os.environ['C9_API_SECRET']}"},
        json={'calculation_type': 'margins', 'in_memory': True, 'currency_code': 'USD',
              'vendor_symbology': 'clearing', 'portfolio': [
                  {'account_code': 'MARGIN_EXAMPLE', 'exchange_code': 'CME', 'contract_code': 'ES',
                   'contract_type': 'FUT', 'contract_expiry': 'DEC-27', 'net_position': 1, 'account_type': 'S'}]},
        timeout=120,
    )
    response.raise_for_status()
    for account in response.json()['data']:
        print_margins(account)


if __name__ == '__main__':
    main()
