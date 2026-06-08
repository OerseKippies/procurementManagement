# procurementManagement (procM)

Date: 2026-06-08  
Repository: OerseKippies/procurementManagement  
Module code: procM  
Status: **PROCUREMENT MVP COMPLETE** (post-go-live freeze)  
Governance: OK-Core

## Purpose

procM is the **central procurement knowledge base** for Oerse Kippies — suppliers, URL intake, prices, purchasing, costing, recipes, repack, and purchase suggestions.

## Quick start

```bash
pip install -r requirements.txt
python run.py
```

→ http://127.0.0.1:5010/

## Tests

```bash
python -m pytest tests/ -v --cov=procm
```

44 tests — MVP + business edition + Co-Pilot consumption API.

## Seed data

**Production (MariaDB):**

```bash
mysql nol_module_procM < SEED-SUPPLIERS.sql
mysql nol_module_procM < SEED-PRODUCTS.sql
```

**Local (SQLite):** On first run the app creates `data/procm.sqlite3` and seeds suppliers, feed, supplements, packaging, recipes, and repack examples.

## Co-Pilot integration

Consumption API: `COPILOT-INTEGRATION.md`  
Dashboard feed: `GET /api/copilot/dashboard`

## Documentation

| Topic | File |
|---|---|
| Architecture | ARCHITECTURE.md |
| Domain | DOMAIN-MODEL.md |
| URL intake | URL-INTAKE-ENGINE.md |
| API (draft) | API-DRAFT.md |
| Handover | handover/HANDOVER-PROCM-COMPLETE-MVP.md |
| ADRs | docs/adr/ |

## Owns

Supplier catalog, URL intake, price history, purchasing, cost/recipe/repack knowledge, purchase suggestions.

## Does NOT own

Inventory, animals, breeds, ads, publications, sales accounting.

## Production (Versio)

URL: https://procm.oerse-kippies.nl/health

```bash
cp config/config.example.php config/config.php
# Set database password (nol_module_procM) and api_key
php scripts/migrate.php
bash scripts/deploy_procm_versio.sh
```

## Environment (local Flask)

| Variable | Default |
|---|---|
| `PROCM_DATABASE` | `data/procm.sqlite3` |
| `PROCM_DATA_DIR` | `data/` |
| `PROCM_SECRET_KEY` | dev key (change in production) |

## Phase

Post-go-live stabilization complete. See `REVIEW-PROCM-POSTGO-LIVE.md`.
