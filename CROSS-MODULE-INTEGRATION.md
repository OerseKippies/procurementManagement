# CROSS-MODULE-INTEGRATION — procurementManagement

Date: 2026-06-08

## Integration principle

All cross-module access via **communicationLayer (commL)**. No direct database access between modules.

## mdM — masterDataManagement

**procM consumes:**

| Reference | Use |
|---|---|
| catalog_item_reference | SupplierProduct mapping, Recipe output |
| product_reference | PO line validation |
| feed definitions | Feed purchasing categories |

**procM does not:**

- Own Product, Feed, Breed, CatalogItem definitions
- Mutate mdM records

**Future contracts (draft):**

| Contract | Direction |
|---|---|
| mdM.masterData.validate.v1 | procM → mdM |

## invM — inventoryManagement

**procM consumes:**

| Signal | Use |
|---|---|
| Stock levels | PurchaseSuggestion (LOW_STOCK) |
| Consumption (future) | Reorder planning |

**procM provides (future):**

| Event | Consumer |
|---|---|
| Purchase receipt recorded | invM inbound movement |
| CostCalculation / unit_cost | invM cost layer |

**procM does not:**

- Own InventoryBalance, StockBatch, StockMovement
- Write inventory state

See ADR-0008-PROCUREMENT-INVENTORY-BOUNDARY.md.

## commL — communicationLayer

procM registers as `procurementManagement` / `procM`.

Consumers: coPilotManagement, invM.

## copM — coPilotManagement

Read/write procurement actions via commL — URL intake, PO creation, suggestions display. procM owns data.

## finM — financeManagement (future)

PurchaseInvoice handoff — deferred.

## Unrelated modules

| Module | Relationship |
|---|---|
| pubM | None — publications not in procM |
| adM | None — advertisements not in procM |

Commercial catalog in copM is separate from procM supplier product knowledge.
