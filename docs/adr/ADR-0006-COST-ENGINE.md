# ADR-0006-COST-ENGINE

Date: 2026-06-08  
Status: Accepted

## Context

Oerse Kippies needs transparent cost price: raw + packaging + label + labor + shipping for feeds, recipes, and repacks.

## Decision

Unified **CostEngine** with CostModel, CostCalculation, CostComponent.

Same engine serves SupplierProduct, RecipeVersion, and RepackRecipe targets.

## Consequences

- Consistent margin math across product types
- CostComponent.source_reference enables audit
- invM may consume unit_cost via commL without owning calculation logic

## Alternatives rejected

- Separate ad-hoc calculators per product type — inconsistent
- Cost ownership in copM commercial workspace — wrong module

See COST-ENGINE.md.
