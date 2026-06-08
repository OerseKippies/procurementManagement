# TEST-COST-ENGINE — procM Post Go-Live

Date: 2026-06-08  
Phase: PHASE-PROCM-POSTGO-LIVE  
Environment: Local Flask + SQLite (repack cost engine)

## Oerse Kippies examples

### Example 1 — Maagkiezel 25 kg → 500 g zakken

| Component | Value |
|---|---|
| Input | Maagkiezel fijn 25 kg @ €12.50 |
| Output unit | 500 g |
| Output units per bulk | 50 |
| Raw material (bulk) | €12.50 |
| Packaging | €0.80 |
| Label | €0.10 |
| Labor | €3.00 |
| Cost per 500 g unit | ~€0.53 |
| Suggested sale price (seed) | €3.20 |
| Margin | 30% default |

**Result: PASS**

### Example 2 — Start & Grow 25 kg → 2 kg zakken

| Component | Value |
|---|---|
| Input | Havens Start & Grow Korrel 25 kg @ €18.95 |
| Output unit | 2 kg |
| Output units per bulk | 12 |
| Raw material (bulk) | €18.95 |
| Packaging | €1.20 |
| Label | €0.15 |
| Labor | €2.50 |
| Cost per 2 kg unit | ~€2.22 |
| Suggested sale price (seed) | €4.50 |
| Margin | 30% default |

**Result: PASS**

## Validation criteria

| Criterion | Verified | Result |
|---|---|---|
| Raw cost from supplier product price | `calculate_repack()` uses `current_price` | PASS |
| Packaging cost included | `packaging_cost` component | PASS |
| Labor cost included | `labor_cost` component | PASS |
| Margin applied | `calculate_cost()` with 30% default | PASS |
| Suggested sales price | `repack_outputs.suggested_sale_price` | PASS |

## Automated evidence

```
tests/test_api.py::test_repack_cost_engine_examples PASSED
tests/test_mvp.py::test_repack_calculation_works PASSED
tests/test_mvp.py::test_cost_calculation_works PASSED
tests/test_business.py::test_cost_calculator_post PASSED
```

## UI verification

1. Open http://127.0.0.1:5010/repack
2. Click **Calculate** on both seeded repack recipes
3. Confirm batch output units, unit cost, and suggested sale price display in flash message

## Overall

**Cost Engine: PASS**
