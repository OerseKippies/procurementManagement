# ADR-0005-PRODUCT-MATCHING

Date: 2026-06-08  
Status: Accepted

## Context

Same effective product may appear under different names/SKUs at Teurlings, Plein, and Havens. Comparison requires cross-supplier equivalence.

## Decision

Introduce **ProductMatch** with confidence score and **MatchDecision** for operator confirmation.

MatchRule provides automated proposals; manual alias via confirmed match is definitive.

## Consequences

- SupplierComparison operates on match groups
- No merge of SupplierProduct records — links only
- mdM catalog_item_reference accelerates high-confidence matches

## Alternatives rejected

- Single global SKU in procM — duplicates mdM
- Automatic merge without confirmation — risk of false equivalence

See PRODUCT-MATCHING-MODEL.md.
