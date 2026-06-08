# ADR-0007-RECIPE-AND-REPACK-MODEL

Date: 2026-06-08  
Status: Accepted

## Context

VitalBoost, Kuikenstartpakket, and 25kg→2kg repacks require BOM-style costing distinct from simple supplier SKU purchase.

## Decision

Separate **Recipe** domain (multi-component mixes) and **RepackRecipe** domain (bulk conversion).

Both produce cost snapshots (RecipeCost, RepackCost) via CostEngine.

RecipeVersion is immutable once costed; RepackRecipe versioned similarly.

## Consequences

- Clear model for OK Verwennerij and feed repack lines
- Physical production/stock split remains invM responsibility
- Recipe components reference SupplierProduct where possible

## Alternatives rejected

- Model repack as Recipe only — loses input/output quantity semantics
- Recipe in mdM — mdM owns definitions, not procurement cost BOMs

See RECIPE-MODEL.md, REPACK-MODEL.md.
