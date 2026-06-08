# ADR-0002-URL-FIRST-INTAKE

Date: 2026-06-08  
Status: Accepted

## Context

Operators currently copy supplier product data manually. Teurlings, Plein, and Bol product pages contain structured data suitable for URL-first intake.

## Decision

Primary product creation path is **URL paste** → ImportJob → SupplierProductSnapshot → SupplierProduct.

Manual entry remains available when `ImportJob.status = MANUAL_REQUIRED`.

## Consequences

- SupplierProduct always carries `supplier_url` and snapshot evidence
- Scraping adapters are pluggable per supplier (runtime phase)
- Legal review required before automated fetch per domain

## Alternatives rejected

- Manual-only supplier catalog — too slow for price tracking
- copM-owned intake — violates procM ownership of supplier products

See URL-INTAKE-ENGINE.md.
