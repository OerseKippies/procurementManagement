# ROADMAP — procurementManagement

Date: 2026-06-08

## Phase 0 — Production-Ready Architecture Foundation (current)

- Complete domain: URL intake, matching, intelligence, purchasing, price, cost, recipe, repack, suggestions
- ADRs 0001–0008, reviews 001–005, audits 001–005
- **Status: COMPLETE (foundation)**

## Phase 1 — Core Runtime MVP

- MariaDB schema (full entity catalog per DOMAIN-MODEL.md)
- Health endpoint
- Supplier + SupplierProduct + PO CRUD
- POST /imports/url (manual fallback only — no scraper)
- commL contract registration

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
