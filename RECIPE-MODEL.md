# RECIPE-MODEL — procurementManagement

Date: 2026-06-08

## Purpose

Model composite products (mixes, kits) and calculate recipe cost.

## Examples (Oerse Kippies)

| Recipe | Components |
|---|---|
| VitalBoost | Additives + base feed components |
| OK Verwennerij | Treat mix |
| Kuikenstartpakket | Feed + grit + supplement bundle |

## Entities

### Recipe

| Field | Description |
|---|---|
| recipe_id | PK |
| name | |
| catalog_item_reference | mdM ref for sellable output (optional) |
| active | |

### RecipeVersion

Versioned BOM — immutable once cost snapshot taken.

| Field | Description |
|---|---|
| version_id | PK |
| recipe_id | FK |
| version_number | |
| effective_from | |
| status | DRAFT, ACTIVE, RETIRED |

### RecipeComponent

| Field | Description |
|---|---|
| component_id | PK |
| version_id | FK |
| supplier_product_id | FK (preferred) |
| catalog_item_reference | mdM ref fallback |
| quantity | |
| unit | kg, g, each |
| waste_factor | Optional % |

### RecipeCost

Snapshot linking RecipeVersion → CostCalculation.

| Field | Description |
|---|---|
| recipe_cost_id | PK |
| version_id | FK |
| calculation_id | FK |
| batch_size | |
| batch_cost | |
| unit_cost | batch_cost / output units |

## Calculation flow

```text
RecipeVersion (ACTIVE)
  → resolve each RecipeComponent → SupplierPrice / CostCalculation
  → CostEngine (RAW + PACKAGING + LABEL + LABOR + SHIPPING)
  → RecipeCost snapshot
```

## Outputs

- Recipe unit cost for pricing advice
- Batch cost for production planning
- Historical RecipeCost for margin audit

See ADR-0007-RECIPE-AND-REPACK-MODEL.md.
