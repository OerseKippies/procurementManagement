# PROCUREMENT-RECOMMENDATION-MODEL — procurementManagement

Date: 2026-06-08

## Purpose

Answer **what should be purchased?** based on rules, stock signals, and seasonal patterns.

## ProcurementRule

| Field | Description |
|---|---|
| rule_id | PK |
| name | e.g. Low feed buffer |
| catalog_item_reference | mdM ref (optional) |
| rule_type | LOW_STOCK, SEASONAL, FIXED_INTERVAL, MANUAL |
| threshold_quantity | For LOW_STOCK |
| active | boolean |

## ProcurementRecommendation

| Field | Description |
|---|---|
| recommendation_id | PK |
| catalog_item_reference | mdM ref |
| supplier_reference | Preferred supplier_id |
| reason | Human-readable |
| suggested_quantity | |
| status | OPEN, ACCEPTED, DISMISSED, ORDERED |
| created_at | |

## Signal sources (consume only)

| Signal | Source |
|---|---|
| Current stock level | invM via commL |
| Consumption rate | invM (future) |
| Seasonal calendar | calM (future) |
| Active supplier prices | procM SupplierPrice |

## Examples

| Scenario | Recommendation |
|---|---|
| Legkorrel below 50kg | Order 100kg from Havens |
| Pre-season chick feed | Order Start & Grow before March |
| Packaging low | Order kraft bags from Bol |
| Repack component | Maagkiezel — compare Plein vs Bol prices |

## Boundary

Recommendations do **not** create inventory or POs automatically in foundation phase. Operator accepts → creates PO (future UI in copM).
