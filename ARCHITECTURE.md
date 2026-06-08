# procurementManagement Architecture

Date: 2026-06-08  
Status: Architecture Foundation  
Module: procurementManagement  
Module code: procM  
Governance authority: OK-Core

## Summary

procM owns procurement truth: suppliers, supplier products, purchase orders, receipts, invoices, price history, and procurement recommendations.

procM does **not** own inventory balances, product definitions, breeds, or commercial catalog data.

## Principles

```text
One module. One ownership boundary. One database/schema.
Only own procurement data.
Cross-module access via communicationLayer (commL) only.
Versio-hosted target (PHP 8.3, MariaDB 10.6).
No runtime in architecture foundation phase.
```

## Component Overview (planned)

```text
procM API (draft)
procM domain services
procM-owned MariaDB schema
procM audit model
Supplier management
Purchase order lifecycle
Receipt and invoice matching
Price history engine
Procurement recommendation engine
```

## Domain Map

See `DOMAIN-MODEL.md`. Detailed lifecycles in `PURCHASE-ORDER-LIFECYCLE.md`, `PRICE-HISTORY-MODEL.md`, `PROCUREMENT-RECOMMENDATION-MODEL.md`.

## Boundaries

| Module | Relationship |
|---|---|
| mdM | Product/feed/catalog **definitions** (reference only) |
| invM | Stock levels, consumption signals (consume only) |
| finM | Future: invoice handoff (out of MVP foundation) |
| commL | Mandatory mediation for all consumers |

## Deployment Target

Versio shared hosting — aligned with OK-Core Deployment Target First (GD-2026-06-06).

## References

- `OerseKippies/OK-Core/architecture/MODULE-BOUNDARIES.md` — procM section
- `OerseKippies/inventoryManagement` — boundary reference (invM owns stock, not procurement)
