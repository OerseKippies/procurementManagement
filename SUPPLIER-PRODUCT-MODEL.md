# SUPPLIER-PRODUCT-MODEL — procurementManagement

Date: 2026-06-08

## Purpose

Map a supplier's sellable SKU to an mdM catalog reference without owning the catalog definition.

## SupplierProduct fields

| Field | Description |
|---|---|
| supplier_product_id | PK |
| supplier_id | FK → Supplier |
| catalog_item_reference | mdM CanonicalIdentifier (required for traceability) |
| supplier_sku | Supplier article number |
| supplier_name | Supplier product label |
| supplier_url | Product page URL |
| package_size | e.g. 20kg, 500pc |
| unit | KG, LITER, PIECE, BAG |
| active | boolean |

## Examples

| Supplier | supplier_name | catalog_item_reference (mdM) |
|---|---|---|
| Havens | Start & Grow 20kg | feed:start-grow |
| Havens | Legkorrel 25kg | feed:legkorrel |
| Bol | Kraft bag 5kg | packaging:kraft-bag-5kg |
| Local | Maagkiezel 2kg | component:maagkiezel |

## Repack source traceability

Repack operations in invM reference **inventory** created from received goods. procM traces **source purchase** via:

```text
PurchaseReceiptLine → SupplierProduct → catalog_item_reference
```

invM does not store supplier SKU; procM does.

## Rules

- One SupplierProduct per supplier SKU per supplier.
- `catalog_item_reference` must validate against mdM before PO line creation (future commL flow).
- procM never duplicates mdM product definitions.
