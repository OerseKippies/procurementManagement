# SUPPLIER-INTELLIGENCE — procurementManagement

Date: 2026-06-08

## Purpose

Compare suppliers on equal footing for Oerse Kippies purchasing decisions.

## Primary suppliers

| Supplier | Focus |
|---|---|
| Teurlings | Chicks, specialty poultry, some feed |
| Plein | Local retail, components |
| Bol | Packaging, general supplies |
| Havens | Feed (Start & Grow, legkorrel, gemengd graan) |
| Olba | Additives |
| Local suppliers | Ad-hoc packaging, labels |

## Comparison metrics

| Metric | Calculation |
|---|---|
| Product price | Latest SupplierPrice.price |
| Shipping | SupplierPrice.shipping_cost or order-level |
| Package size | SupplierProduct.package_size |
| Effective unit cost | (price + allocated shipping) / normalized units |
| Historical trend | PriceHistory slope over 90/180 days |
| Lowest / highest / average | PriceHistory aggregates |

## SupplierComparison entity

| Field | Description |
|---|---|
| comparison_id | PK |
| catalog_item_reference | mdM ref (optional) |
| product_match_group_id | Linked matches |
| supplier_id | FK |
| supplier_product_id | FK |
| effective_unit_cost | Computed |
| rank | 1 = cheapest effective |
| computed_at | |

## Intelligence outputs

- Side-by-side table: Teurlings vs Plein vs Bol for same matched product
- Trend alert: price increased >10% since last order
- Seasonal note: pre-March feed buffer (feeds PurchaseSuggestion)

## Boundary

Intelligence uses procM data only. Stock levels from invM inform suggestions but not comparison math.
