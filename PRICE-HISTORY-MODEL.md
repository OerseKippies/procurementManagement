# PRICE-HISTORY-MODEL — procurementManagement

Date: 2026-06-08

## Purpose

Track supplier pricing over time for comparison, seasonal analysis, and cost-price calculation support.

## SupplierPrice

Point-in-time price for a SupplierProduct.

| Field | Description |
|---|---|
| supplier_price_id | PK |
| supplier_product_id | FK |
| effective_date | Date price applies from |
| price | Unit price |
| currency | EUR (default) |
| shipping_cost | Optional per unit or order |
| notes | e.g. seasonal promo |

## PriceHistory

Denormalized history row for analytics (may aggregate SupplierPrice + invoice actuals).

| Field | Description |
|---|---|
| price_history_id | PK |
| catalog_item_reference | mdM ref |
| supplier_id | FK |
| recorded_date | |
| unit_price | |
| source | ORDER, INVOICE, MANUAL_QUOTE |

## Use cases

| Use case | Mechanism |
|---|---|
| Supplier comparison | Compare SupplierPrice across suppliers for same catalog_item_reference |
| Seasonal purchasing | PriceHistory trends by month/quarter |
| Cost price support | Latest effective price + receipt actuals for repack costing |
| Havens feed tracking | SupplierProduct per feed SKU → PriceHistory over time |

## Strategy

See ADR-0003-PRICE-HISTORY-STRATEGY.md.

- **SupplierPrice** = planned/quoted price
- **Invoice line actual** = realized price (feeds PriceHistory on invoice post)
- No retroactive mutation — append-only history
