# HANDOVER — procM Complete MVP

Date: 2026-06-08  
Repository: OerseKippies/procurementManagement  
Module: procM

## What was built

### Architecture (Part 1)

- Full documentation set (README, ARCHITECTURE, domain models, API draft)
- ADRs 0001–0008 in `docs/adr/` and `governance/decisions/`
- Reviews 001–006, Audits 001–006

### Runtime (Part 2)

- **Flask** web app (`procm/`, `run.py`)
- **SQLite** database (`data/procm.sqlite3`)
- **13 screens**: Dashboard, Suppliers, Products, URL Intake, Price History, PO, Receipts, Invoices, Recipes, Repack, Cost Calculator, Suggestions, Settings (+ Matching, Intelligence)
- URL intake with fetch + heuristic parse + manual fallback
- Seed data: Teurlings, Plein, Bol, Scharrelpluimvee, Olba products and recipes

## How to run

```bash
cd procurementManagement
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5010/

## Database

- Default path: `data/procm.sqlite3`
- Override: `PROCM_DATABASE` or `PROCM_DATA_DIR` env vars
- Schema: `procm/db.py` (`init_db` on startup)
- Seed: automatic on empty database (`procm/seed.py`)

## Tests

```bash
python -m pytest tests/ -v
```

## Known limitations

1. Single-user local SQLite — not multi-tenant production
2. No authentication / authorization
3. No commL integration yet
4. No invM stock signals — manual quantity for suggestions
5. URL fetch depends on network; blocked sites → manual mode
6. Generic HTML heuristics — no site-specific Bol/Teurlings adapters yet
7. No automated purchasing or email
8. Recipe/repack editing via seed only (view + calculate in UI)
9. Not deployed to Versio yet
10. OK-Core approval still PENDING

## Next steps

1. OK-Core review and approval
2. commL contract registration
3. copM procurement workspace consumer
4. MariaDB migration for Versio deployment
5. Site-specific URL adapters (legal review)
6. invM low-stock signal integration
