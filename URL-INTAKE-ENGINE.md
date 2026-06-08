# URL-INTAKE-ENGINE — procurementManagement

Date: 2026-06-08  
Status: Architecture design (no scraping runtime)

## Purpose

Core capability: operator pastes a supplier URL → system builds or updates a **SupplierProduct** with snapshot evidence.

## Supported sources (Oerse Kippies)

| Supplier | Example URL pattern |
|---|---|
| Teurlings | teurlings.nl product pages |
| Plein | plein.nl / local retail |
| Bol | bol.com product pages |
| Havens, Olba | Supplier-specific URLs |
| Generic | Any supplier product URL |

## Flow

```text
POST /imports/url
  → ImportJob (PENDING)
  → ImportedPage (fetch metadata — future)
  → SupplierProductSnapshot (captured fields)
  → SupplierProduct (upsert)
  → SupplierPrice (if price detected)
  → SupplierProductImage[] (image URLs)
```

## Captured fields

| Field | Storage |
|---|---|
| supplier | Supplier (resolve or create draft) |
| product name | SupplierProduct.supplier_name |
| supplier SKU | SupplierProduct.supplier_sku |
| image URLs | SupplierProductImage |
| source URL | SupplierProduct.supplier_url |
| package size | SupplierProduct.package_size |
| weight | Snapshot metadata |
| quantity | Snapshot metadata |
| price | SupplierPrice + snapshot |
| timestamp | SupplierProductSnapshot.captured_at |

## Domain entities

### ImportJob

| Field | Description |
|---|---|
| import_job_id | PK |
| source_url | Pasted URL |
| supplier_id | Resolved supplier |
| status | PENDING, PROCESSING, COMPLETED, FAILED, MANUAL_REQUIRED |
| correlation_id | Trace |
| created_at | |

### ImportedPage

| Field | Description |
|---|---|
| page_id | PK |
| import_job_id | FK |
| raw_title | Parsed title |
| raw_html_hash | Dedup / audit (no long-term HTML store in MVP runtime) |
| parser_version | |

### SupplierProductImport

Links ImportJob → SupplierProduct creation outcome.

### SupplierProductSnapshot

Immutable capture at intake time — supports price dispute and audit.

## Scraping strategy (research — not implemented)

| Approach | Use |
|---|---|
| Structured metadata / JSON-LD | Preferred when present |
| Site-specific adapters | Teurlings, Bol — phased |
| Manual fallback | **Always available** — operator completes fields |
| Scheduled re-fetch | Price watch (future) |

## Legal & operational considerations

- Respect robots.txt and supplier terms of use
- No automated ordering or checkout
- Rate limiting on fetch jobs
- Operator-triggered intake only (no background mass scrape in foundation)
- Store source URL for attribution
- GDPR: no personal data from product pages

## Fallback manual mode

If parser fails → `ImportJob.status = MANUAL_REQUIRED` → operator form pre-filled with URL only.

## API

See API-DRAFT.md — `POST /imports/url`
