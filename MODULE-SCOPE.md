# MODULE-SCOPE — procurementManagement

Date: 2026-06-08  
Status: Production-Ready Architecture Foundation

## In scope

| Domain | Entities / capability |
|---|---|
| Suppliers | Supplier, SupplierContact |
| Supplier catalog | SupplierProduct, SupplierProductImage, SupplierProductImport, SupplierProductSnapshot |
| URL intake | ImportJob, ImportedPage (design) |
| Pricing | SupplierPrice, PriceHistory, SupplierComparison |
| Matching | ProductMatch, MatchDecision, MatchRule |
| Purchasing | PurchaseOrder, PurchaseOrderLine, PurchaseReceipt, PurchaseReceiptLine, PurchaseInvoice, PurchaseInvoiceLine |
| Costing | CostModel, CostCalculation, CostComponent |
| Recipes | Recipe, RecipeComponent, RecipeVersion, RecipeCost |
| Repack | RepackRecipe, RepackOutput, RepackCost |
| Advice | PurchaseSuggestion, SuggestionRule, ProcurementRecommendation |

## Operator journeys (designed)

1. Paste Teurlings/Plein/Bol URL → supplier product created
2. Track price history and compare suppliers
3. Calculate recipe cost (VitalBoost, Verwennerij, Kuikenstartpakket)
4. Calculate repack cost (25kg → 2kg bags)
5. Receive purchase suggestion (e.g. order 4 bags Start & Grow from Teurlings)
6. Place PO → record receipt → match invoice

## Out of scope

| Item | Owner / note |
|---|---|
| Stock, inventory movements | invM |
| Animals, breeds, feed definitions | mdM |
| Commercial catalog, ads, publications | copM / adM / pubM |
| Runtime API | Phase 1 implementation |
| UI / OK-Cockpit screens | copM consumer (future) |
| Live web scraping | Designed in URL-INTAKE-ENGINE; not implemented |
| Accounting ledger | finM (future) |

## Oerse Kippies alignment

Supports OK-Cockpit order tool vision, product intake engine, URL-first import, Teurlings purchasing data, managed-item redesign — as **procurement knowledge**, not inventory.
