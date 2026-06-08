# MODULE-SCOPE — procurementManagement

Date: 2026-06-08  
Status: Architecture Foundation

## In Scope

| Area | Included |
|---|---|
| Supplier master data | Supplier, SupplierContact |
| Supplier catalog mapping | SupplierProduct, SupplierPrice |
| Purchasing | PurchaseOrder, PurchaseOrderLine |
| Receiving | PurchaseReceipt, PurchaseReceiptLine |
| Invoicing (procurement view) | PurchaseInvoice, PurchaseInvoiceLine |
| Cost intelligence | PriceHistory, SupplierPrice |
| Planning support | ProcurementRecommendation, ProcurementRule |
| Feed purchasing | Examples: Havens Start & Grow, legkorrel |
| Packaging purchasing | Kraft bags, stickers, buckets, labels |
| Product component purchasing | Meelwormen, BSF, maagkiezel, vitamines |
| Repack source traceability | SupplierProduct → catalog_item_reference |
| Supplier comparison | Via PriceHistory / SupplierPrice |
| Seasonal purchasing analysis | Recommendation rules (documented, not runtime) |

## Out of Scope

| Area | Owner |
|---|---|
| Inventory balances, movements, batches | invM |
| Product, feed, breed definitions | mdM |
| Catalog offers, advertisements | copM / commercial workspace |
| Publications | pubM |
| Sales, reservations | salesM (future) |
| Accounting ledger | finM (future) |
| Runtime API implementation | Future phase |
| UI / Co-Pilot screens | copM (consumer, future) |
| Browser automation / supplier scraping | Explicitly excluded from foundation |

## MVP Foundation Deliverable

Documentation, ADRs, reviews, audits — **PASS** when ownership and boundaries are unambiguous and cross-module integration is specified.
