# ADR-0003-PRICE-HISTORY-STRATEGY

Date: 2026-06-08  
Status: Accepted

## Context

Operators need supplier comparison, seasonal analysis, and cost-price support for repack products.

## Decision

Dual-layer pricing:

1. **SupplierPrice** — planned/quoted effective-dated prices
2. **PriceHistory** — append-only analytical history from quotes, orders, and invoice actuals

No in-place price mutation. New effective date = new SupplierPrice row.

## Consequences

- Historical accuracy for Havens feed price trends
- Invoice actuals can diverge from quoted price (recorded separately)
- finM may consume invoice totals later without rewriting procM history

## Alternatives rejected

- Overwrite single price field — loses audit trail
