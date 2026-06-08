# PURCHASE-LIFECYCLE — procurementManagement

Date: 2026-06-08

## Lifecycle

```text
DRAFT → SUBMITTED → CONFIRMED → PARTIALLY_RECEIVED → RECEIVED → INVOICED → CLOSED
                              ↘ CANCELLED
```

## States

| State | Meaning |
|---|---|
| ordered | PO confirmed (CONFIRMED+) |
| received | PurchaseReceipt recorded |
| invoiced | PurchaseInvoice matched |

## PurchaseOrder

| Field | Description |
|---|---|
| purchase_order_id | PK |
| supplier_id | FK |
| order_date | |
| status | Lifecycle status |
| total_amount | Sum of lines |
| notes | |

## PurchaseOrderLine

| Field | Description |
|---|---|
| line_id | PK |
| purchase_order_id | FK |
| supplier_product_id | FK |
| quantity | |
| unit_price | Locked at order time |

## PurchaseReceipt / PurchaseReceiptLine

Records physical receipt. Links to PO lines. **Does not** update invM directly — future commL event.

## PurchaseInvoice / PurchaseInvoiceLine

Matches receipt/PO for cost verification. Feeds PriceHistory on post.

## Teurlings example

Order 50 Cream Legbar chicks → confirm → receipt on delivery → invoice match → PriceHistory updated.

## Boundary

procM = purchase knowledge. invM = stock. See ADR-0008.
