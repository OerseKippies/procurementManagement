# ADR-0008-PROCUREMENT-INVENTORY-BOUNDARY

Date: 2026-06-08  
Status: Accepted

## Context

Purchase receipts affect stock but inventory is owned by invM per OK-Core boundaries.

## Decision

procM records **PurchaseReceipt** as procurement knowledge.

Future: commL event `procM.purchaseReceipt.recorded.v1` → invM creates inbound StockMovement.

procM never writes InventoryBalance, StockBatch, or StockMovement.

Low-stock signals flow **invM → procM** for PurchaseSuggestion only.

## Consequences

- Clear separation: ordered/received/invoiced (procM) vs on-hand (invM)
- No dual-write risk at foundation phase
- Integration contract defined before runtime

## Alternatives rejected

- procM updates stock on receipt — violates MODULE-BOUNDARIES
- invM owns purchase orders — wrong domain

See PURCHASE-LIFECYCLE.md, CROSS-MODULE-INTEGRATION.md.
