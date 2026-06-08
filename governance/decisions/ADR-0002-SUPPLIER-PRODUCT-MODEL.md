# ADR-0002-SUPPLIER-PRODUCT-MODEL

Date: 2026-06-08  
Status: Accepted

## Context

Suppliers sell SKUs that map to Oerse Kippies catalog items defined in mdM. procM must not duplicate product definitions.

## Decision

Introduce **SupplierProduct** as the join between:

```text
Supplier (procM) + catalog_item_reference (mdM) + supplier_sku (procM)
```

Purchase order lines reference **SupplierProduct**, not raw mdM records directly.

## Consequences

- Repack traceability: receipt → supplier product → mdM catalog ref
- Supplier comparison per catalog item across suppliers
- mdM validation required before PO line creation (runtime phase)

## Alternatives rejected

- Store supplier SKU in invM — violates boundary (invM owns stock, not procurement catalog)
