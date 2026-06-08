# ADR-0001-PROCUREMENT-OWNERSHIP

Date: 2026-06-08  
Status: Accepted  
Module: procurementManagement (procM)

## Context

OK-Core requires explicit module ownership before implementation. procM is catalogued but had no repository foundation.

## Decision

procM owns all procurement and supplier purchasing data:

```text
Supplier, SupplierContact, SupplierProduct,
PurchaseOrder, PurchaseOrderLine,
PurchaseReceipt, PurchaseReceiptLine,
PurchaseInvoice, PurchaseInvoiceLine,
PriceHistory, SupplierPrice,
ProcurementRecommendation, ProcurementRule
```

## Consequences

- Single schema for procurement truth
- invM, mdM, copM consume via commL only
- No procurement tables in invM database

## Compliance

Aligned with OK-Core `architecture/MODULE-BOUNDARIES.md` procM section (extended entity list).
