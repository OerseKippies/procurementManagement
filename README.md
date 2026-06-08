# procurementManagement (procM)

Date: 2026-06-08  
Repository: OerseKippies/procurementManagement  
Module code: procM  
Status: **Architecture Foundation**  
Governance: OK-Core

## Purpose

procurementManagement is the procurement and purchasing module for the Oerse Kippies ecosystem.

procM answers:

- What should be purchased?
- What was purchased?
- From whom?
- At what price?
- When was it received?
- What was the cost history?

## Authority

```text
1. OK-Core ADRs and governance
2. OK-Core architecture/MODULE-BOUNDARIES.md
3. OK-Core architecture/MODULE-CATALOG.md
4. Local procM ADRs
5. Local procM documentation
```

## Owns

```text
Supplier
SupplierContact
SupplierProduct
PurchaseOrder
PurchaseOrderLine
PurchaseReceipt
PurchaseReceiptLine
PurchaseInvoice
PurchaseInvoiceLine
PriceHistory
SupplierPrice
ProcurementRecommendation
ProcurementRule
```

## Does Not Own

```text
CatalogItem, Product, Feed, Breed, Animal
Advertisement, Publication
InventoryBalance, StockBatch, StockMovement
```

## Scope

Architecture foundation only. No runtime, UI, or inventory implementation in this phase.

## Documentation

| Document | Purpose |
|---|---|
| ARCHITECTURE.md | Module architecture overview |
| MODULE-SCOPE.md | In/out of scope |
| DOMAIN-MODEL.md | Entity catalog |
| SUPPLIER-MANAGEMENT.md | Supplier domain |
| SUPPLIER-PRODUCT-MODEL.md | Supplier catalog mapping |
| PURCHASE-ORDER-LIFECYCLE.md | PO → receipt → invoice |
| PRICE-HISTORY-MODEL.md | Price tracking |
| PROCUREMENT-RECOMMENDATION-MODEL.md | Reorder advice |
| CROSS-MODULE-INTEGRATION.md | mdM, invM, commL |
| API-DRAFT.md | Future API surface |
| ROADMAP.md | Implementation phases |

## Oerse Kippies examples

Teurlings, Havens, Bol, Plein, Olba, local suppliers — feed, packaging, repack components.
