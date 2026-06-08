# OERSE-KIPPIES-USE-CASES — procurementManagement

Date: 2026-06-08

Worked examples for architecture validation. Design only — no runtime.

## 1. Start & Grow (Havens / Teurlings)

| Step | procM action |
|---|---|
| URL intake | Paste Teurlings product URL → SupplierProduct + Snapshot |
| Price | SupplierPrice €X / 20 kg bag |
| Match | ProductMatch to Plein equivalent chick feed |
| Compare | SupplierComparison — effective €/kg |
| Suggest | PurchaseSuggestion: order 4 bags from Teurlings (low stock signal) |
| PO | PurchaseOrder 4 × 20 kg → receipt → invoice |
| Repack | RepackRecipe 25 kg bulk → 2 kg bags → RepackCost |

## 2. Legkorrel

| Step | procM action |
|---|---|
| Intake | Havens legkorrel URL or manual |
| History | PriceHistory — seasonal trend pre-laying season |
| Cost | CostCalculation — raw + shipping |

## 3. Gemengd Graan

| Step | procM action |
|---|---|
| Suppliers | Havens vs local mill |
| Compare | SupplierComparison on €/kg normalized |
| Suggest | Seasonal buffer rule (SuggestionRule) |

## 4. VitalBoost

| Step | procM action |
|---|---|
| Recipe | Recipe + RecipeVersion with Olba additives + base feed |
| Cost | RecipeCost — batch of 50 units |

## 5. Maagkiezel

| Step | procM action |
|---|---|
| Intake | Supplier URL (Plein / specialty) |
| Match | Match to mdM catalog_item_reference |
| PO | Small-quantity PO line |

## 6. Wormenmix

| Step | procM action |
|---|---|
| Recipe | RecipeComponent — dried worms + carrier |
| Cost | RecipeCost for Verwennerij line |

## 7. Kuikenstartpakket

| Step | procM action |
|---|---|
| Recipe | Bundle: Start & Grow sample + maagkiezel + supplement |
| Cost | RecipeCost unit cost for kit pricing |
| Suggest | Pre-season PurchaseSuggestion (March chick season) |

## Cross-cutting

All use cases respect boundaries: mdM owns catalog definitions; invM owns stock; procM owns procurement knowledge and cost snapshots.
