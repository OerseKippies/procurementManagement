# CROSS-MODULE-INTEGRATION — procurementManagement

Date: 2026-06-08

## Integration principle

All cross-module access via **communicationLayer (commL)**. No direct database access between modules.

## mdM — masterDataManagement

**procM consumes:**

| Reference | Use |
|---|---|
| catalog_item_reference | SupplierProduct mapping |
| product_reference | PO line validation |
| feed definitions | Feed purchasing categories |

**procM does not:**

- Own Product, Feed, Breed, CatalogItem definitions
- Mutate mdM records

**Future contracts (draft):**

| Contract | Direction |
|---|---|
| mdM.masterData.validate.v1 | procM → mdM (validate catalog ref) |

## invM — inventoryManagement

**procM consumes:**

| Signal | Use |
|---|---|
| Stock levels | LOW_STOCK recommendations |
| Consumption (future) | Reorder planning |

**procM provides (future):**

| Event | Consumer |
|---|---|
| Purchase receipt recorded | invM creates inbound movement |
| Cost reference | invM cost layer (future) |

**procM does not:**

- Own InventoryBalance, StockBatch, StockMovement
- Write inventory state

See ADR-0004-PROCUREMENT-AND-INVENTORY-BOUNDARY.md.

## commL — communicationLayer

procM registers as owner module `procurementManagement` / `procM`.

Future consumers: coPilotManagement (operator UI), invM (receipt events).

## copM — coPilotManagement

Future read-only/procurement workspace — **not in foundation phase**.

copM displays procurement data; procM owns it.

## finM — financeManagement (future)

PurchaseInvoice handoff for accounting — deferred.

## Reference modules

| Module | Relationship |
|---|---|
| pubM | None |
| adM | None |

Commercial catalog in copM is unrelated to procM supplier catalog mapping.
