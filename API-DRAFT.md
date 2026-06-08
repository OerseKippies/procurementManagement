# API-DRAFT — procurementManagement

Date: 2026-06-08  
Status: **Draft** — no runtime implementation

Base path (planned): `/api/v1/procurement`

## Suppliers

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /suppliers | procM.suppliers.list.v1 |
| POST | /suppliers | procM.suppliers.create.v1 |
| GET | /suppliers/{supplierId} | procM.suppliers.get.v1 |
| PATCH | /suppliers/{supplierId} | procM.suppliers.update.v1 |

## Supplier products

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /suppliers/{supplierId}/products | procM.supplierProducts.list.v1 |
| POST | /supplier-products | procM.supplierProducts.create.v1 |

## Purchase orders

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /purchase-orders | procM.purchaseOrders.list.v1 |
| POST | /purchase-orders | procM.purchaseOrders.create.v1 |
| GET | /purchase-orders/{purchaseOrderId} | procM.purchaseOrders.get.v1 |
| PATCH | /purchase-orders/{purchaseOrderId} | procM.purchaseOrders.update.v1 |
| POST | /purchase-orders/{purchaseOrderId}/submit | procM.purchaseOrders.submit.v1 |

## Receipts

| Method | Path | Contract (planned) |
|---|---|---|
| POST | /purchase-receipts | procM.purchaseReceipts.create.v1 |

## Prices

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /price-history | procM.priceHistory.list.v1 |
| POST | /supplier-prices | procM.supplierPrices.create.v1 |

## Recommendations

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /recommendations | procM.recommendations.list.v1 |
| POST | /recommendations/{id}/accept | procM.recommendations.accept.v1 |

## Headers

```text
X-Correlation-Id: required
X-Actor-Type / X-Actor-Id: required for mutations
X-Idempotency-Key: required for mutations (commL)
```

## Consumers (planned)

- coPilotManagement — operator procurement workspace
- invM — receipt events (inbound)
