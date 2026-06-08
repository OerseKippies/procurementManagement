# AUDIT-003-OWNERSHIP

Audit ID: AUDIT-003-OWNERSHIP  
Date: 2026-06-08  
Outcome: **PASS**

## Method

Map CCM ownership list to DOMAIN-MODEL.md and ADR-0001.

## procM owns (verified)

Supplier, SupplierContact, SupplierProduct, SupplierProductImage, SupplierProductImport, SupplierProductSnapshot, SupplierPrice, SupplierComparison, ImportJob, ImportedPage, ProductMatch, MatchDecision, MatchRule, PurchaseOrder, PurchaseOrderLine, PurchaseReceipt, PurchaseReceiptLine, PurchaseInvoice, PurchaseInvoiceLine, CostModel, CostCalculation, CostComponent, PriceHistory, Recipe, RecipeComponent, RecipeVersion, RecipeCost, RepackRecipe, RepackOutput, RepackCost, PurchaseSuggestion, SuggestionRule, ProcurementRecommendation.

## procM does NOT own (verified)

CatalogItem, Product, Feed, Breed, Animal, InventoryBalance, StockBatch, StockMovement, Advertisement, Publication.

## Violations

None.
