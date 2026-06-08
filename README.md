# procurementManagement (procM)

Date: 2026-06-08  
Repository: OerseKippies/procurementManagement  
Module code: procM  
Status: **Production-Ready Architecture Foundation**  
Governance: OK-Core

## Purpose

procM is the **central procurement knowledge base** for Oerse Kippies — not merely purchasing.

procM answers:

- What should be purchased? From whom? At what price?
- What was ordered, received, and invoiced?
- What does a supplier product cost (unit, effective, historical)?
- What does a recipe or repack product cost?
- Which supplier is cheapest for the same effective product?

## Core capabilities (designed, not runtime)

| Engine | Document |
|---|---|
| URL intake | URL-INTAKE-ENGINE.md |
| Product matching | PRODUCT-MATCHING-MODEL.md |
| Supplier intelligence | SUPPLIER-INTELLIGENCE.md |
| Price history | PRICE-HISTORY-MODEL.md |
| Purchasing | PURCHASE-LIFECYCLE.md |
| Purchase suggestions | PURCHASE-SUGGESTION-MODEL.md |
| Cost calculation | COST-ENGINE.md |
| Recipe costing | RECIPE-MODEL.md |
| Repack costing | REPACK-MODEL.md |

## Owns

Supplier, SupplierContact, SupplierProduct, SupplierProductImage, SupplierProductImport, SupplierProductSnapshot, SupplierPrice, SupplierComparison, PurchaseOrder/Line, PurchaseReceipt/Line, PurchaseInvoice/Line, ProductMatch, MatchDecision, MatchRule, CostModel, CostCalculation, CostComponent, Recipe, RecipeComponent, RecipeVersion, RecipeCost, RepackRecipe, RepackOutput, RepackCost, PurchaseSuggestion, SuggestionRule, ProcurementRecommendation.

## Does NOT own

CatalogItem, Product, Feed, Breed, Animal, InventoryBalance, StockBatch, StockMovement, Advertisement, Publication.

## Phase

Architecture foundation only — no UI, runtime, scraping implementation, or inventory.

## Authority

OK-Core MODULE-BOUNDARIES.md → local ADRs → local documentation.
