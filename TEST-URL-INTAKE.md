# TEST-URL-INTAKE — procM Post Go-Live

Date: 2026-06-08  
Phase: PHASE-PROCM-POSTGO-LIVE  
Environment: Local Flask + SQLite (mirrors production URL intake engine)

## Scope

Validate complete URL workflow against Teurlings, Plein, and Bol supplier domains.

## Test matrix

| # | Supplier | Test URL | URL accepted | Import job | Product draft | Snapshot | Manual correction | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | Teurlings de Mulder | `https://www.teurlings.nl/product/meelwormen` | PASS | PASS | PASS | PASS | PASS (UI edit) | **PASS** |
| 2 | Plein | `https://www.plein.nl/maagkiezel` | PASS | PASS | PASS | PASS | PASS (UI edit) | **PASS** |
| 3 | Bol | `https://www.bol.com/nl/nl/p/kraft-zakjes/123/` | PASS | PASS | PASS | PASS | PASS (UI edit) | **PASS** |

## Validation criteria

| Criterion | Evidence | Result |
|---|---|---|
| URL accepted | `run_url_intake()` accepts http/https URLs; normalizes missing scheme | PASS |
| Import job created | Row in `import_jobs` with status `COMPLETED` or `MANUAL_REQUIRED` | PASS |
| Product draft created | Row in `supplier_products` linked via `supplier_product_imports` | PASS |
| Snapshot stored | JSON in `supplier_product_snapshots.captured_json` | PASS |
| Manual correction works | Product edit at `/products/<id>/edit` updates name, price, package | PASS |

## Automated evidence

```
tests/test_api.py::test_url_intake_api_flow PASSED
tests/test_mvp.py::test_url_intake_fallback PASSED
tests/test_business.py::test_intake_parse_html PASSED
```

Supplier detection verified:

- `teurlings.nl` → Teurlings de Mulder
- `plein.nl` → Plein
- `bol.com` → Bol

## UI verification

1. Start app: `python run.py` → http://127.0.0.1:5010/url-intake
2. Submit each test URL
3. Confirm job appears in recent imports table
4. Open draft product via Products list and correct fields

## Overall

**URL Intake: PASS**
