# COST-ENGINE — procurementManagement

Date: 2026-06-08

## Purpose

Calculate **cost price** for supplier products, recipes, and repack outputs.

## Formula

```text
Cost Price =
  Raw cost
  + Packaging
  + Label
  + Labor
  + Shipping
```

## Entities

### CostModel

Template defining component types and default allocation rules.

| Field | Description |
|---|---|
| cost_model_id | PK |
| name | e.g. Standard feed repack |
| model_type | SUPPLIER_PRODUCT, RECIPE, REPACK |
| active | boolean |

### CostComponent

Single line in a calculation.

| Field | Description |
|---|---|
| component_id | PK |
| cost_calculation_id | FK |
| component_type | RAW, PACKAGING, LABEL, LABOR, SHIPPING |
| amount | Decimal EUR |
| quantity_basis | Per unit, per batch, per kg |
| source_reference | SupplierPrice, manual, rule |

### CostCalculation

Computed result for a target entity at a point in time.

| Field | Description |
|---|---|
| calculation_id | PK |
| cost_model_id | FK |
| target_type | SUPPLIER_PRODUCT, RECIPE_VERSION, REPACK_RECIPE |
| target_id | FK |
| total_cost | Sum of components |
| unit_cost | Per sellable unit |
| calculated_at | |
| price_basis_date | SupplierPrice effective date used |

## Inputs

| Component | Typical source |
|---|---|
| Raw cost | Latest SupplierPrice or PO line price |
| Packaging | SupplierProduct (Bol bag) via CostModel |
| Label | Fixed or supplier price |
| Labor | Minutes × rate from CostModel |
| Shipping | Allocated from SupplierPrice.shipping_cost |

## Outputs

- Unit cost for margin analysis (copM commercial — read-only)
- RecipeCost / RepackCost snapshots
- Audit trail via CostComponent.source_reference

## Boundary

Cost **knowledge** lives in procM. Stock valuation in invM may consume cost via commL (future).

See ADR-0006-COST-ENGINE.md.
