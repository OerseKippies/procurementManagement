# ADR-0004-PRICE-HISTORY-STRATEGY

Date: 2026-06-08  
Status: Accepted

## Context

Supplier prices change frequently. Historical analysis requires immutable records.

## Decision

**Append-only** pricing:

- SupplierPrice — point-in-time quote
- PriceHistory — analytical series derived on write
- Never mutate prior price rows

Aggregates (current, previous, lowest, highest, average) computed from series.

## Consequences

- Audit trail for disputes and seasonal analysis
- Storage growth manageable for Oerse Kippies scale
- Invoice-posted prices feed history as ground truth

## Alternatives rejected

- Single current_price column with overwrite — loses history

See PRICE-HISTORY-MODEL.md.
