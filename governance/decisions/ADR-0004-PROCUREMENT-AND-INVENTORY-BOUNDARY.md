# ADR-0004-PROCUREMENT-AND-INVENTORY-BOUNDARY

Date: 2026-06-08  
Status: Accepted

## Context

invM owns inventory state. procM owns purchasing. Overlap causes dual-write and reconciliation failures.

## Decision

```text
procM records: ordered, received (procurement view), invoiced
invM records: stock levels, movements, batches
```

Receipt in procM emits integration event (future). invM creates inbound **StockMovement** — procM does not.

procM may **read** invM stock levels for recommendations only.

## Consequences

- Clear accountability: "purchased" vs "in stock"
- Teurlings chick delivery: procM receipt + invM inbound are linked by correlationId, not shared tables
- OK-Core boundary audit PASS

## Anti-patterns (forbidden)

- invM storing supplier master data
- procM storing InventoryBalance or StockMovement
- Direct SQL cross-module queries
