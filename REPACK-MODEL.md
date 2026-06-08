# REPACK-MODEL — procurementManagement

Date: 2026-06-08

## Purpose

Model bulk-to-retail conversion and calculate repack cost.

## Example

```text
25 kg Havens Start & Grow (bulk sack)
  → 2 kg consumer bags (×12) + labels + labor
```

## Entities

### RepackRecipe

| Field | Description |
|---|---|
| repack_recipe_id | PK |
| name | e.g. Start & Grow 25kg → 2kg |
| input_supplier_product_id | Bulk SKU |
| input_quantity | e.g. 25 kg |

### RepackOutput

| Field | Description |
|---|---|
| output_id | PK |
| repack_recipe_id | FK |
| output_supplier_product_id | Retail SKU (or virtual) |
| output_quantity | e.g. 12 × 2 kg |
| catalog_item_reference | mdM sellable ref |

### RepackCost

| Field | Description |
|---|---|
| repack_cost_id | PK |
| repack_recipe_id | FK |
| calculation_id | FK to CostCalculation |
| input_cost | Bulk purchase cost |
| packaging_cost | Bags, labels |
| labor_cost | |
| final_unit_cost | Per output unit |

## Calculation flow

```text
RepackRecipe
  → input_cost from SupplierPrice (bulk)
  → packaging from SupplierProduct (Bol bags, labels)
  → labor from CostModel
  → RepackCost via CostEngine
```

## Boundary

Repack **cost knowledge** in procM. Physical repack execution and stock split in invM (future commL).

See ADR-0007-RECIPE-AND-REPACK-MODEL.md.
