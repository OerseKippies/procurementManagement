# SUPPLIER-MANAGEMENT — procurementManagement

Date: 2026-06-08

## Purpose

Manage supplier master data and contacts for Oerse Kippies purchasing operations.

## Oerse Kippies supplier examples

| Supplier | Typical categories |
|---|---|
| Teurlings | Chicks, breeding stock, specialty poultry |
| Havens | Feed (Start & Grow, legkorrel, gemengd graan) |
| Bol | General supplies, packaging |
| Plein | Local retail / components |
| Olba | Feed additives, supplements |
| Local suppliers | Ad-hoc packaging, labels, buckets |

## Supplier lifecycle

```text
DRAFT → ACTIVE → PREFERRED | INACTIVE
```

- **ACTIVE** — may appear on purchase orders
- **PREFERRED** — default for recommendations
- **INACTIVE** — historical only; no new POs

## SupplierContact

Multiple contacts per supplier. Used for order communication tracking (notes field on PO, not email automation in foundation phase).

## Rules

1. procM owns supplier records; invM stores `supplier_id` reference only when needed for traceability — not supplier master.
2. mdM does not own suppliers.
3. Duplicate supplier names flagged at validation (future runtime).

## Integration

Consumers (copM, future) read suppliers via commL contracts — never direct DB access.
