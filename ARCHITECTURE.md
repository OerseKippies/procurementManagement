# procurementManagement Architecture

Date: 2026-06-08  
Status: Complete Business Edition (Flask + SQLite runtime)  
Module code: procM

## Vision

```text
URL paste → SupplierProduct → PriceHistory → SupplierComparison
                ↓
         PurchaseOrder → Receipt → Invoice
                ↓
         CostEngine → RecipeCost / RepackCost → PurchaseSuggestion
```

procM owns **procurement knowledge**. invM owns **stock truth**. mdM owns **canonical definitions**.

## Engine architecture

| Layer | Responsibility |
|---|---|
| Intake | URL → ImportJob → SupplierProductSnapshot → SupplierProduct |
| Matching | ProductMatch across suppliers (Teurlings vs Plein vs Bol) |
| Intelligence | Effective unit cost, trends, comparison |
| Purchasing | PO → receipt → invoice lifecycle |
| Costing | Raw + packaging + label + labor + shipping = cost price |
| Recipe | Multi-component products (VitalBoost, Verwennerij, Kuikenstartpakket) |
| Repack | Bulk input → packaged output (25kg → 2kg bags) |
| Suggestions | Low stock, seasonal, manual — PurchaseSuggestion |

## Principles

```text
URL-first product discovery (manual fallback always available)
Append-only price history
No inventory dual-write
commL-only cross-module access
Versio target (PHP 8.3, MariaDB 10.6)
Design for runtime without redesign
```

## Runtime (delivered)

```text
Flask web app (run.py) — port 5010
SQLite (data/procm.sqlite3) + migrations v2-business
URL intake (procm/intake.py)
Monitoring, forecasts, reports (procm/business_routes.py)
Services: pricing, cost, recipe, repack, suggestions, invoice_import
pytest suite (27 tests)
```

## Deferred

```text
MariaDB / Versio deploy
commL contract registry
copM procurement workspace consumer
```

## Boundaries

See ADR-0008-PROCUREMENT-INVENTORY-BOUNDARY.md and CROSS-MODULE-INTEGRATION.md.
