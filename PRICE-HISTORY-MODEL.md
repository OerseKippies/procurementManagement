# PRICE-HISTORY-MODEL — procurementManagement

Date: 2026-06-08

## Purpose

Track supplier pricing over time for comparison, seasonal analysis, and cost-price calculation.

## SupplierPrice

Point-in-time quoted or observed price.

| Field | Description |
|---|---|
| supplier_price_id | PK |
| supplier_product_id | FK |
| effective_date | |
| price | Unit price |
| currency | EUR |
| shipping_cost | |
| source | URL_INTAKE, MANUAL, INVOICE, ORDER |
| notes | |

## PriceHistory

Analytical series (append-only).

| Field | Description |
|---|---|
| price_history_id | PK |
| supplier_product_id | FK |
| catalog_item_reference | mdM ref |
| recorded_date | |
| unit_price | |
| effective_unit_cost | After package normalization |
| source | |

## Tracked aggregates (per supplier_product or match group)

| Metric | Description |
|---|---|
| current_price | Latest SupplierPrice |
| previous_price | Prior effective price |
| lowest_price | Min in window |
| highest_price | Max in window |
| average_price | Mean in window (default 12 months) |

## Update triggers

| Event | Action |
|---|---|
| URL intake | New SupplierPrice + PriceHistory row |
| PO confirmed | Snapshot order price |
| Invoice posted | Actual price → PriceHistory |
| Manual edit | New SupplierPrice row (no overwrite) |

## Strategy

See ADR-0004-PRICE-HISTORY-STRATEGY.md — append-only, no in-place mutation.
