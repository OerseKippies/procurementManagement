# COPILOT-INTEGRATION — procM Consumption API

Date: 2026-06-08  
Status: **Active** — read-only consumption contract for coPilotManagement  
Module: procM  
Ownership: unchanged (procM owns procurement data; copM consumes)

## Base URLs

| Runtime | Base URL |
|---|---|
| Production (Versio PHP) | `https://procm.oerse-kippies.nl/api` |
| Local dev (Flask) | `http://127.0.0.1:5010/api` |

## Authentication

When `config.php` sets `api.require_api_key = true`, pass:

```http
X-API-Key: <api_key>
```

## Endpoints exposed to Co-Pilot

### GET /suppliers

Contract: `procM.suppliers.list.v1`

| Query | Type | Description |
|---|---|---|
| `active` | int (0/1) | Filter by active flag |

Response:

```json
{
  "data": [
    {
      "id": 1,
      "name": "Teurlings de Mulder",
      "domain": "teurlings.nl",
      "notes": "...",
      "active": 1
    }
  ],
  "count": 4
}
```

### GET /supplier-products

Contract: `procM.supplierProducts.list.v1`

| Query | Type | Description |
|---|---|---|
| `supplier_id` | int | Filter by supplier |
| `active` | int (0/1) | Filter by active flag |

Response includes `supplier_name`, `package_size`, `package_unit`, `current_price`.

### GET /purchase-suggestions

Contract: `procM.purchaseSuggestions.list.v1`

| Query | Type | Default |
|---|---|---|
| `status` | string | `open` |

Returns open purchase suggestions with product and supplier names.

### GET /recipes

Contract: `procM.recipes.list.v1`

Returns active recipe versions with batch size and output unit.

### GET /cost-calculations

Contract: `procM.costCalculations.list.v1`

| Query | Type | Default |
|---|---|---|
| `limit` | int | 50 (max 100) |

Returns recent cost calculation records (repack, recipe, manual).

### GET /dashboard-summary

Contract: `procM.dashboard.summary.v1`

Aggregated procurement KPIs for operator dashboards.

```json
{
  "suppliers_count": 4,
  "supplier_products_count": 12,
  "open_purchase_suggestions": 0,
  "purchase_orders_count": 0,
  "recent_purchase_orders": [],
  "module": "procM",
  "status": "PROCUREMENT MVP COMPLETE"
}
```

## Co-Pilot dashboard feed

### GET /copilot/dashboard

Contract: `procM.copilot.dashboard.v1`

Lightweight feed for coPilotManagement Sales MVP dashboard (priority 8 integration).

Response:

```json
{
  "suppliers_count": 4,
  "supplier_products_count": 12,
  "products_needing_reorder": 0,
  "active_purchase_suggestions": 0,
  "recent_purchases": [
    {
      "id": 1,
      "order_date": "2026-06-08",
      "status": "closed",
      "supplier_name": "Plein",
      "total": 25.0
    }
  ],
  "generated_at": "2026-06-08T12:00:00+00:00",
  "contract": "procM.copilot.dashboard.v1"
}
```

| Field | Source |
|---|---|
| `suppliers_count` | `suppliers` WHERE active = 1 |
| `supplier_products_count` | `supplier_products` WHERE active = 1 |
| `products_needing_reorder` | DISTINCT `supplier_product_id` in open `purchase_suggestions` |
| `active_purchase_suggestions` | `purchase_suggestions` WHERE status = 'open' |
| `recent_purchases` | Last 10 `purchase_orders` with line totals |

## Health

### GET /health

No API key required. Returns runtime, database, and commit metadata.

## Boundaries (no ownership changes)

| procM owns | copM does NOT own |
|---|---|
| Supplier catalog | Inventory stock |
| Supplier products & prices | Sales tickets |
| Purchase orders / receipts / invoices | Advertisements |
| Cost / recipe / repack knowledge | Publications |
| Purchase suggestions | Customer leads |

copM **consumes** procM read APIs; mutations remain in procM UI or future write contracts.

## Implementation files

| File | Role |
|---|---|
| `public/api/index.php` | Production PHP router |
| `src-php/api_handlers.php` | MariaDB query handlers |
| `procm/api_routes.py` | Flask dev mirror |

## Tests

```
tests/test_api.py — 6 API integration tests (all PASS)
```
