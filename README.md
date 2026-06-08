# procurementManagement (procM)

Date: 2026-06-08  
Repository: OerseKippies/procurementManagement  
Module code: procM  
Status: **Complete Architecture + Runtime MVP**  
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
python -m pytest tests/ -v
```

## Seed data

On first run the app creates `data/procm.sqlite3` and seeds:

- Suppliers: Teurlings, Plein, Bol, Scharrelpluimvee, Olba
- Feed & supplies (Start & Grow, Legkorrel, Maagkiezel, …)
- Recipes: VitalBoost Start, Tamme Kuikenmix, Wormenmix, Kuikenstartpakket
- Repack examples: 25 kg → 2 kg, Maagkiezel → 500 g

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

## Environment

| Variable | Default |
|---|---|
| `PROCM_DATABASE` | `data/procm.sqlite3` |
| `PROCM_DATA_DIR` | `data/` |
| `PROCM_SECRET_KEY` | dev key (change in production) |

## Phase

Runtime MVP — local Flask + SQLite. Not OK-Core approved until governance review.
