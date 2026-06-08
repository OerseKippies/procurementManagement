# ROADMAP — procurementManagement

Date: 2026-06-08

## Phase 0 — Architecture Foundation

- **Status: COMPLETE**

## Phase 1 — Runtime MVP (current)

- Flask + SQLite local app
- All 13 operator screens
- URL intake with fallback
- Seed data, pytest 13/13
- **Status: COMPLETE (local MVP)**

## Phase 2 — Production Runtime

- MariaDB schema on Versio
- Health endpoint deployment
- commL contract registration
- Authentication

## Phase 2 — Price, Matching & Intelligence

- SupplierPrice, PriceHistory aggregates
- ProductMatch + MatchDecision workflow
- SupplierComparison computation
- PurchaseInvoice matching

## Phase 3 — Cost, Recipe & Repack Runtime

- CostEngine implementation
- Recipe / RepackRecipe APIs
- RecipeCost / RepackCost snapshots

## Phase 4 — Suggestions & Integration

- PurchaseSuggestion engine
- invM stock signal consumption via commL
- Receipt → invM event contract

## Phase 5 — URL Intake Adapters

- Site-specific parsers (Teurlings, Bol) — legal review first
- Scheduled price re-fetch

## Phase 6 — Operator UI (copM)

- Procurement workspace
- URL paste intake, comparison tables, PO flows

## Explicitly deferred

- Inventory ownership (invM)
- Accounting (finM)
- Automated mass scraping
- UI in procM repo

## Alignment

Supports OK Verwennerij / VitalBoost costing and Teurlings purchasing without blocking PM-2 commercial workspace.
