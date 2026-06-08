# TEST-PURCHASING-FLOW — procM Post Go-Live

Date: 2026-06-08  
Phase: PHASE-PROCM-POSTGO-LIVE  
Environment: Local Flask + SQLite

## End-to-end workflow

```
Supplier Product → Purchase Order → Receipt → Invoice → Closed
```

## Test execution

| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | Select supplier product (Plein — Maagkiezel fijn 25 kg) | Product available in PO form | PASS |
| 2 | Create purchase order (draft) | PO created with line item | PASS |
| 3 | Set status → ordered | Status updated | PASS |
| 4 | Register receipt linked to PO | Receipt + receipt line created | PASS |
| 5 | Set PO status → received | Status updated on receipt | PASS |
| 6 | Register invoice linked to PO | Invoice + line created; price recorded | PASS |
| 7 | Set PO status → closed | Final status = `closed` | PASS |

## Automated evidence

```
tests/test_mvp.py::test_purchase_order_created PASSED
tests/test_business.py::test_purchasing_hub PASSED
```

Scripted validation (2026-06-08):

- PO created for Plein supplier
- Final purchase order status: `closed`
- Receipt and invoice rows linked to same PO

## UI walkthrough

| Screen | Route | Verified |
|---|---|---|
| Purchasing hub | `/purchasing` | PASS |
| Purchase orders | `/purchase-orders` | PASS |
| Receipts | `/receipts` | PASS |
| Invoices | `/invoices` | PASS |

### Screenshot placeholders

| Step | File | Status |
|---|---|---|
| PO draft | `docs/evidence/purchasing-01-po-draft.png` | Capture on operator review |
| Receipt | `docs/evidence/purchasing-02-receipt.png` | Capture on operator review |
| Invoice closed | `docs/evidence/purchasing-03-closed.png` | Capture on operator review |

> Screenshots to be captured during OK-Core operator review on production UI.

## Production seed alignment

After running `SEED-SUPPLIERS.sql` and `SEED-PRODUCTS.sql` on MariaDB, repeat the same flow using seeded Plein products.

## Overall

**Purchasing Flow: PASS**
