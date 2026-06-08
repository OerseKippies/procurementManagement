# ADR-0001-PROCUREMENT-OWNERSHIP

Date: 2026-06-08  
Status: Accepted  
Module: procurementManagement (procM)

## Context

OK-Core requires explicit module ownership before implementation. procM is the central procurement **knowledge** base — not merely purchasing.

## Decision

procM owns:

```text
Supplier, SupplierContact,
SupplierProduct, SupplierProductImage, SupplierProductImport, SupplierProductSnapshot,
SupplierPrice, SupplierComparison,
ImportJob, ImportedPage,
ProductMatch, MatchDecision, MatchRule,
PurchaseOrder, PurchaseOrderLine,
PurchaseReceipt, PurchaseReceiptLine,
PurchaseInvoice, PurchaseInvoiceLine,
PriceHistory,
CostModel, CostCalculation, CostComponent,
Recipe, RecipeComponent, RecipeVersion, RecipeCost,
RepackRecipe, RepackOutput, RepackCost,
PurchaseSuggestion, SuggestionRule, ProcurementRecommendation
```

## Consequences

- Single schema for procurement truth
- invM, mdM, copM consume via commL only
- Cost and recipe knowledge centralized for Oerse Kippies margin analysis

## Compliance

Aligned with OK-Core `architecture/MODULE-BOUNDARIES.md` procM section.
