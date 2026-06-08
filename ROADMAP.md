# ROADMAP — procurementManagement

Date: 2026-06-08

## Phase 0 — Architecture Foundation (current)

- Documentation, ADRs, reviews, audits
- **Status: COMPLETE (foundation)**

## Phase 1 — Core Runtime MVP

- MariaDB schema (suppliers, supplier products, PO, receipt)
- Health endpoint
- Supplier + PO CRUD API
- commL contract registration
- Versio deployment

## Phase 2 — Price & Receipt

- SupplierPrice, PriceHistory
- PurchaseInvoice matching
- Receipt → invM integration contract

## Phase 3 — Recommendations

- ProcurementRule engine
- invM stock signal consumption
- Seasonal rules

## Phase 4 — Operator UI (copM)

- Procurement workspace in Co-Pilot
- Teurlings / Havens order flows
- Supplier comparison views

## Explicitly deferred

- Browser automation (Marktplaats-style — N/A for procM)
- Supplier website scraping
- Accounting integration (finM)
- Inventory ownership overlap

## Alignment

Post PM-2 commercial workspace; supports repack and cost traceability without blocking sales flow.
