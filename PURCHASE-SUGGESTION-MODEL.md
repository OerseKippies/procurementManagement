# PURCHASE-SUGGESTION-MODEL — procurementManagement

Date: 2026-06-08

## Purpose

Generate actionable purchasing advice.

## Entities

### PurchaseSuggestion

| Field | Description |
|---|---|
| suggestion_id | PK |
| catalog_item_reference | mdM ref |
| supplier_id | Recommended supplier |
| supplier_product_id | FK |
| suggested_quantity | e.g. 4 bags |
| reason | Human-readable |
| status | OPEN, ACCEPTED, DISMISSED, ORDERED |
| priority | LOW, MEDIUM, HIGH |
| created_at | |

### SuggestionRule

| Field | Description |
|---|---|
| rule_id | PK |
| rule_type | LOW_STOCK, SEASONAL, REORDER_INTERVAL, MANUAL |
| threshold | |
| active | |

### ProcurementRecommendation

Aggregate view / legacy alias linking to PurchaseSuggestion for commL compatibility.

## Signal sources

| Signal | Source |
|---|---|
| Low stock | invM via commL |
| Seasonal (pre-March feed) | SuggestionRule + calendar |
| Price drop | SupplierComparison |
| Manual | Operator |

## Example

**Product:** Havens Start & Grow  
**Suggestion:** Order **4 bags** from **Teurlings**  
**Reason:** Stock below 2 bags; preferred supplier; effective unit cost lowest

## Workflow

```text
SuggestionRule + signals → PurchaseSuggestion (OPEN)
  → operator ACCEPT → create PurchaseOrder draft
  → ORDERED when PO submitted
```

No auto-PO in foundation phase.
