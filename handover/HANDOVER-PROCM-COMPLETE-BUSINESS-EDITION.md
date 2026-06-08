# HANDOVER — procM Complete Business Edition

Date: 2026-06-08  
Repository: OerseKippies/procurementManagement

## Delivered

Spreadsheet replacement for Oerse Kippies procurement:

| Area | Capability |
|---|---|
| Suppliers & products | Full CRUD |
| URL intake | Teurlings/Plein/Bol/generic + manual fallback |
| Price history | Current/previous/min/max/avg + visual chart |
| Monitoring | SupplierWatch, refresh, dashboard moves |
| Alerts | PriceAlert target/maximum |
| Canonical products | Unified view across suppliers |
| Purchasing | PO, receipts, invoices, hub |
| Invoice import | CSV paste, CSV/Excel upload |
| Cost / recipe / repack | Calculators + builders |
| Consumption | Planning events (not inventory) |
| Forecasting | Days remaining, reorder date |
| Suggestions | Price + forecast driven |
| Reports | CSV + Excel export |

## Run

```bash
pip install -r requirements.txt
python run.py
```

http://127.0.0.1:5010/

## Tests

```bash
python -m pytest tests/ -v --cov=procm
```

27 tests (MVP + business). Target ≥80% coverage — run with `--cov-fail-under=80` after expansion.

## Database

- SQLite: `data/procm.sqlite3`
- Migrations: `procm/migrations.py` (schema v2-business)
- Auto-init on startup

## Boundaries

- No inventory stock ownership (planning qty only)
- No ads/publications/accounting
- User-triggered URL fetch only

## Next steps

- Versio deploy (MariaDB)
- commL + copM workspace
- invM signal consumption (optional)
- Site-specific URL adapters
