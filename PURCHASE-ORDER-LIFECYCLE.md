# PURCHASE-ORDER-LIFECYCLE — procurementManagement

Date: 2026-06-08

## Lifecycle

```text
DRAFT → SUBMITTED → CONFIRMED → PARTIALLY_RECEIVED → RECEIVED → CLOSED
                              ↘ CANCELLED
```

## Entities

### PurchaseOrder

| Field | Description |
|---|---|
| purchase_order_id | PK |
| supplier_id | FK |
| order_date | Date placed |
| status | Lifecycle status |
| total_amount | Computed from lines |
| notes | Operator notes |

### PurchaseOrderLine

| Field | Description |
|---|---|
| line_id | PK |
| purchase_order_id | FK |
| supplier_product_id | FK |
| quantity | Ordered qty |
| unit_price | Price at order time |

## Receipt flow

```text
PurchaseOrder (CONFIRMED)
  → PurchaseReceipt + PurchaseReceiptLine(s)
  → status PARTIALLY_RECEIVED | RECEIVED
```

Receipt records **what arrived** — not inventory mutation. invM integration (future): commL event `procM.receipt.recorded.v1` consumed by invM to create inbound movement.

## Invoice flow

```text
PurchaseReceipt (RECEIVED)
  → PurchaseInvoice + PurchaseInvoiceLine(s)
  → match to PO lines for cost verification
```

## Teurlings example

1. Create PO for 50 Cream Legbar chicks — SupplierProduct linked to mdM `animal:chick-cream-legbar`.
2. Submit → Confirm with supplier.
3. Receipt on delivery date — quantity received may differ (partial).
4. Invoice matched — updates PriceHistory via SupplierPrice snapshot.

## Boundary

procM records purchase truth. invM records stock truth. No dual-write.
