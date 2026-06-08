# DOMAIN-MODEL — procurementManagement

Date: 2026-06-08  
Status: Architecture Foundation

## Entity Catalog

| Entity | Primary key | Purpose |
|---|---|---|
| Supplier | supplier_id | Vendor master |
| SupplierContact | contact_id | Supplier contacts |
| SupplierProduct | supplier_product_id | Supplier SKU mapped to mdM catalog reference |
| SupplierPrice | supplier_price_id | Point-in-time supplier price |
| PriceHistory | price_history_id | Normalized cost history for analysis |
| PurchaseOrder | purchase_order_id | Order header |
| PurchaseOrderLine | line_id | Order line |
| PurchaseReceipt | receipt_id | Goods received |
| PurchaseReceiptLine | receipt_line_id | Received quantities |
| PurchaseInvoice | invoice_id | Supplier invoice |
| PurchaseInvoiceLine | invoice_line_id | Invoice lines |
| ProcurementRecommendation | recommendation_id | Suggested purchase |
| ProcurementRule | rule_id | Rule driving recommendations |

## Supplier

| Field | Type | Notes |
|---|---|---|
| supplier_id | UUID | PK |
| name | string | e.g. Teurlings, Havens, Bol |
| status | enum | ACTIVE, INACTIVE, PREFERRED |
| website | string | Optional |
| notes | text | Operator notes |

## SupplierContact

| Field | Type | Notes |
|---|---|---|
| contact_id | UUID | PK |
| supplier_id | UUID | FK → Supplier |
| name | string | |
| email | string | |
| phone | string | |
| role | string | e.g. sales, support |

## SupplierProduct

See `SUPPLIER-PRODUCT-MODEL.md`.

## SupplierPrice / PriceHistory

See `PRICE-HISTORY-MODEL.md`.

## PurchaseOrder / PurchaseOrderLine

See `PURCHASE-ORDER-LIFECYCLE.md`.

## PurchaseReceipt / PurchaseReceiptLine

Linked to PurchaseOrder; records physical receipt. Does **not** create inventory — invM receives events separately via integration contract (future).

## PurchaseInvoice / PurchaseInvoiceLine

Procurement cost record; finM integration deferred.

## ProcurementRecommendation / ProcurementRule

See `PROCUREMENT-RECOMMENDATION-MODEL.md`.

## Reference Fields (not owned)

| Field | Source module |
|---|---|
| catalog_item_reference | mdM CanonicalIdentifier |
| product_reference | mdM |
| inventory_item_reference | invM (read-only signal) |
