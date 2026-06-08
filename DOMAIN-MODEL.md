# DOMAIN-MODEL — procurementManagement

Date: 2026-06-08  
Status: Production-Ready Architecture Foundation

## Entity catalog

### Supplier domain

| Entity | PK | Purpose |
|---|---|---|
| Supplier | supplier_id | Vendor master |
| SupplierContact | contact_id | Contacts |
| SupplierProduct | supplier_product_id | Supplier SKU + mdM ref |
| SupplierProductImage | image_id | Image URLs from intake |
| SupplierProductImport | import_id | Import attempt record |
| SupplierProductSnapshot | snapshot_id | Point-in-time captured data |
| SupplierPrice | supplier_price_id | Effective-dated price |
| SupplierComparison | comparison_id | Computed comparison row |

### Intake domain

| Entity | PK | Purpose |
|---|---|---|
| ImportJob | import_job_id | URL intake job |
| ImportedPage | page_id | Raw page metadata |

### Matching domain

| Entity | PK | Purpose |
|---|---|---|
| ProductMatch | match_id | Cross-supplier match candidate |
| MatchDecision | decision_id | Confirmed/rejected match |
| MatchRule | rule_id | Matching heuristics |

### Purchasing domain

| Entity | PK | Purpose |
|---|---|---|
| PurchaseOrder | purchase_order_id | Order header |
| PurchaseOrderLine | line_id | Order line |
| PurchaseReceipt | receipt_id | Goods received |
| PurchaseReceiptLine | receipt_line_id | Received qty |
| PurchaseInvoice | invoice_id | Supplier invoice |
| PurchaseInvoiceLine | invoice_line_id | Invoice line |

### Cost domain

| Entity | PK | Purpose |
|---|---|---|
| CostModel | cost_model_id | Template (raw+pack+label+labor+ship) |
| CostCalculation | calculation_id | Computed result |
| CostComponent | component_id | Line in calculation |
| PriceHistory | price_history_id | Analytical price series |

### Recipe domain

| Entity | PK | Purpose |
|---|---|---|
| Recipe | recipe_id | e.g. VitalBoost, Verwennerij |
| RecipeComponent | component_id | Ingredient line |
| RecipeVersion | version_id | Versioned BOM |
| RecipeCost | recipe_cost_id | Cost snapshot per version |

### Repack domain

| Entity | PK | Purpose |
|---|---|---|
| RepackRecipe | repack_recipe_id | e.g. 25kg → 2kg bags |
| RepackOutput | output_id | Output SKU/qty |
| RepackCost | repack_cost_id | Cost snapshot |

### Suggestion domain

| Entity | PK | Purpose |
|---|---|---|
| PurchaseSuggestion | suggestion_id | Actionable advice |
| SuggestionRule | rule_id | Rule definition |
| ProcurementRecommendation | recommendation_id | Legacy alias / aggregate view |

## Reference fields (not owned)

| Field | Source |
|---|---|
| catalog_item_reference | mdM |
| inventory_signal | invM (read-only) |

## Detail documents

URL-INTAKE-ENGINE.md, PRODUCT-MATCHING-MODEL.md, SUPPLIER-INTELLIGENCE.md, PRICE-HISTORY-MODEL.md, PURCHASE-LIFECYCLE.md, PURCHASE-SUGGESTION-MODEL.md, COST-ENGINE.md, RECIPE-MODEL.md, REPACK-MODEL.md, OERSE-KIPPIES-USE-CASES.md
