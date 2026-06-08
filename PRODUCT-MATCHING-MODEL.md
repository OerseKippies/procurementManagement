# PRODUCT-MATCHING-MODEL — procurementManagement

Date: 2026-06-08

## Purpose

Determine whether **Supplier A product** matches **Supplier B product** for comparison and unified costing.

Example: Teurlings Start & Grow 20kg vs Plein equivalent chick feed.

## Entities

### ProductMatch

| Field | Description |
|---|---|
| match_id | PK |
| supplier_product_id_a | FK |
| supplier_product_id_b | FK |
| confidence_score | 0.0–1.0 |
| match_status | PROPOSED, CONFIRMED, REJECTED |
| match_reason | e.g. same catalog ref, alias, manual |

### MatchDecision

| Field | Description |
|---|---|
| decision_id | PK |
| match_id | FK |
| decided_by | Actor reference |
| decision | CONFIRM, REJECT, MERGE |
| decided_at | |

### MatchRule

| Field | Description |
|---|---|
| rule_id | PK |
| rule_type | CATALOG_REF, NAME_SIMILARITY, PACKAGE_SIZE, MANUAL_ALIAS |
| priority | int |
| active | boolean |

## Matching signals

| Signal | Weight |
|---|---|
| Same mdM catalog_item_reference | High |
| Normalized name similarity | Medium |
| Package size + unit match | Medium |
| Manual alias table | Definitive |
| Category (feed vs packaging) | Gate |

## Workflow

```text
Intake new SupplierProduct
  → run MatchRules
  → ProductMatch (PROPOSED) if confidence ≥ threshold
  → operator MatchDecision (CONFIRM / REJECT)
  → confirmed matches feed SupplierComparison
```

## Alias handling

Operator may define: "Plein Kuikenvoer 5kg" = "Havens Start & Grow 5kg" via confirmed ProductMatch without changing mdM ownership.
