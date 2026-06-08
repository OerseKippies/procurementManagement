# API-DRAFT — procurementManagement

Date: 2026-06-08  
Status: **Draft** — no runtime implementation

Base path (planned): `/api/v1/procurement`

## URL intake

| Method | Path | Contract (planned) |
|---|---|---|
| POST | /imports/url | procM.imports.url.v1 |

Request body: `{ "source_url": "https://..." }`  
Response: ImportJob + SupplierProductSnapshot (or MANUAL_REQUIRED).

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
| GET | /supplier-products | procM.supplierProducts.list.v1 |
| GET | /suppliers/{supplierId}/products | procM.supplierProducts.listBySupplier.v1 |
| POST | /supplier-products | procM.supplierProducts.create.v1 |

## Price history

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /price-history | procM.priceHistory.list.v1 |
| POST | /supplier-prices | procM.supplierPrices.create.v1 |

Query: `supplier_product_id`, `catalog_item_reference`, date range.

## Product matching

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /product-matches | procM.productMatches.list.v1 |
| POST | /product-matches/{matchId}/decide | procM.productMatches.decide.v1 |

## Supplier comparison

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /supplier-comparisons | procM.supplierComparisons.list.v1 |

## Purchase orders

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /purchase-orders | procM.purchaseOrders.list.v1 |
| POST | /purchase-orders | procM.purchaseOrders.create.v1 |
| GET | /purchase-orders/{purchaseOrderId} | procM.purchaseOrders.get.v1 |
| PATCH | /purchase-orders/{purchaseOrderId} | procM.purchaseOrders.update.v1 |
| POST | /purchase-orders/{purchaseOrderId}/submit | procM.purchaseOrders.submit.v1 |

## Receipts & invoices

| Method | Path | Contract (planned) |
|---|---|---|
| POST | /purchase-receipts | procM.purchaseReceipts.create.v1 |
| POST | /purchase-invoices | procM.purchaseInvoices.create.v1 |

## Cost engine

| Method | Path | Contract (planned) |
|---|---|---|
| POST | /cost-calculations | procM.costCalculations.create.v1 |
| GET | /cost-calculations/{id} | procM.costCalculations.get.v1 |

## Recipes

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /recipes | procM.recipes.list.v1 |
| POST | /recipes | procM.recipes.create.v1 |
| POST | /recipes/{recipeId}/versions/{versionId}/cost | procM.recipes.calculateCost.v1 |

## Repack

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /repack-recipes | procM.repackRecipes.list.v1 |
| POST | /repack | procM.repack.calculate.v1 |

## Purchase suggestions

| Method | Path | Contract (planned) |
|---|---|---|
| GET | /purchase-suggestions | procM.purchaseSuggestions.list.v1 |
| POST | /purchase-suggestions/{id}/accept | procM.purchaseSuggestions.accept.v1 |
| GET | /recommendations | procM.recommendations.list.v1 (alias) |

## Headers

```text
X-Correlation-Id: required
X-Actor-Type / X-Actor-Id: required for mutations
X-Idempotency-Key: required for mutations (commL)
```

## Consumers (planned)

- coPilotManagement — operator procurement workspace
- invM — receipt events (inbound), stock signals (outbound to procM)
