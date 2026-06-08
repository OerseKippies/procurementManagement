"""SQLite schema and connection helpers."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from procm import config

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    domain TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    notes TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS supplier_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    name TEXT NOT NULL,
    role TEXT,
    email TEXT,
    phone TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS supplier_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    supplier_sku TEXT,
    supplier_product_name TEXT NOT NULL,
    canonical_name TEXT,
    source_url TEXT,
    package_size REAL,
    package_unit TEXT,
    current_price REAL,
    currency TEXT NOT NULL DEFAULT 'EUR',
    image_url TEXT,
    description TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS supplier_product_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    image_url TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS import_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_url TEXT NOT NULL,
    supplier_id INTEGER REFERENCES suppliers(id),
    status TEXT NOT NULL DEFAULT 'PENDING',
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS imported_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_job_id INTEGER NOT NULL REFERENCES import_jobs(id),
    raw_title TEXT,
    raw_html_hash TEXT,
    parser_version TEXT NOT NULL DEFAULT 'mvp-1'
);

CREATE TABLE IF NOT EXISTS supplier_product_imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_job_id INTEGER NOT NULL REFERENCES import_jobs(id),
    supplier_product_id INTEGER REFERENCES supplier_products(id),
    outcome TEXT
);

CREATE TABLE IF NOT EXISTS supplier_product_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_job_id INTEGER REFERENCES import_jobs(id),
    supplier_product_id INTEGER REFERENCES supplier_products(id),
    captured_json TEXT NOT NULL,
    captured_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS supplier_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    effective_date TEXT NOT NULL DEFAULT (datetime('now')),
    price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'EUR',
    shipping_cost REAL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'manual',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    recorded_date TEXT NOT NULL DEFAULT (datetime('now')),
    unit_price REAL NOT NULL,
    effective_unit_cost REAL,
    source TEXT NOT NULL DEFAULT 'manual',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS product_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    target_supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    confidence REAL NOT NULL DEFAULT 0.5,
    decision TEXT NOT NULL DEFAULT 'unknown',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS match_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_match_id INTEGER NOT NULL REFERENCES product_matches(id),
    decided_by TEXT NOT NULL DEFAULT 'operator',
    decision TEXT NOT NULL,
    decided_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS match_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_type TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    active INTEGER NOT NULL DEFAULT 1,
    config_json TEXT
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    order_date TEXT NOT NULL DEFAULT (date('now')),
    status TEXT NOT NULL DEFAULT 'draft',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS purchase_order_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_order_id INTEGER NOT NULL REFERENCES purchase_orders(id),
    supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    line_total REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS purchase_receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    purchase_order_id INTEGER REFERENCES purchase_orders(id),
    received_date TEXT NOT NULL DEFAULT (date('now')),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS purchase_receipt_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_receipt_id INTEGER NOT NULL REFERENCES purchase_receipts(id),
    supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    quantity REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS purchase_invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    purchase_order_id INTEGER REFERENCES purchase_orders(id),
    invoice_number TEXT NOT NULL,
    invoice_date TEXT NOT NULL DEFAULT (date('now')),
    invoice_total REAL NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS purchase_invoice_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_invoice_id INTEGER NOT NULL REFERENCES purchase_invoices(id),
    supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    line_total REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS cost_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    model_type TEXT NOT NULL DEFAULT 'generic',
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cost_calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_model_id INTEGER REFERENCES cost_models(id),
    target_type TEXT,
    target_id INTEGER,
    total_cost REAL NOT NULL,
    unit_cost REAL,
    suggested_sale_price REAL,
    margin_euro REAL,
    margin_percent REAL,
    price_basis_date TEXT,
    calculated_at TEXT NOT NULL DEFAULT (datetime('now')),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS cost_components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_calculation_id INTEGER NOT NULL REFERENCES cost_calculations(id),
    component_type TEXT NOT NULL,
    amount REAL NOT NULL,
    quantity_basis TEXT,
    source_reference TEXT
);

CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS recipe_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id),
    version_number INTEGER NOT NULL DEFAULT 1,
    batch_size REAL NOT NULL DEFAULT 1,
    output_unit TEXT NOT NULL DEFAULT 'unit',
    status TEXT NOT NULL DEFAULT 'active',
    effective_from TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS recipe_components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_version_id INTEGER NOT NULL REFERENCES recipe_versions(id),
    supplier_product_id INTEGER REFERENCES supplier_products(id),
    component_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL DEFAULT 'kg',
    unit_cost REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS recipe_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_version_id INTEGER NOT NULL REFERENCES recipe_versions(id),
    cost_calculation_id INTEGER REFERENCES cost_calculations(id),
    batch_cost REAL NOT NULL,
    unit_cost REAL NOT NULL,
    calculated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS repack_recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    input_supplier_product_id INTEGER REFERENCES supplier_products(id),
    input_quantity REAL NOT NULL,
    input_unit TEXT NOT NULL DEFAULT 'kg',
    packaging_cost REAL NOT NULL DEFAULT 0,
    label_cost REAL NOT NULL DEFAULT 0,
    labor_cost REAL NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS repack_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repack_recipe_id INTEGER NOT NULL REFERENCES repack_recipes(id),
    output_quantity REAL NOT NULL,
    output_unit TEXT NOT NULL DEFAULT 'kg',
    suggested_sale_price REAL
);

CREATE TABLE IF NOT EXISTS repack_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repack_recipe_id INTEGER NOT NULL REFERENCES repack_recipes(id),
    cost_calculation_id INTEGER REFERENCES cost_calculations(id),
    output_units REAL NOT NULL,
    cost_per_output_unit REAL NOT NULL,
    waste_remainder REAL NOT NULL DEFAULT 0,
    calculated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS purchase_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    supplier_id INTEGER REFERENCES suppliers(id),
    suggested_quantity REAL NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    priority TEXT NOT NULL DEFAULT 'medium',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS suggestion_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_type TEXT NOT NULL,
    threshold REAL,
    active INTEGER NOT NULL DEFAULT 1,
    config_json TEXT
);

CREATE TABLE IF NOT EXISTS procurement_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_suggestion_id INTEGER REFERENCES purchase_suggestions(id),
    summary TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def ensure_data_dir() -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or config.DATABASE_PATH
    ensure_data_dir()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | None = None) -> None:
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


@contextmanager
def db_conn(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)
