"""Schema migrations for procM SQLite database."""

from __future__ import annotations

import sqlite3

BUSINESS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS canonical_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    category TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS supplier_watches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    source_url TEXT,
    last_checked_at TEXT,
    last_price REAL,
    previous_price REAL,
    change_percent REAL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS price_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    alert_type TEXT NOT NULL,
    threshold_price REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    triggered_at TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS consumption_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_product_id INTEGER NOT NULL REFERENCES supplier_products(id),
    event_type TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL DEFAULT 'kg',
    event_date TEXT NOT NULL DEFAULT (date('now')),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS consumption_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_product_id INTEGER NOT NULL UNIQUE REFERENCES supplier_products(id),
    avg_daily_consumption REAL NOT NULL DEFAULT 0,
    unit TEXT NOT NULL DEFAULT 'kg',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS forecast_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_product_id INTEGER NOT NULL UNIQUE REFERENCES supplier_products(id),
    current_planning_qty REAL NOT NULL DEFAULT 0,
    safety_days INTEGER NOT NULL DEFAULT 7,
    lead_time_days INTEGER NOT NULL DEFAULT 7,
    preferred_supplier_id INTEGER REFERENCES suppliers(id),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS invoice_imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER REFERENCES suppliers(id),
    source_type TEXT NOT NULL DEFAULT 'manual',
    source_filename TEXT,
    imported_at TEXT NOT NULL DEFAULT (datetime('now')),
    line_count INTEGER NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS invoice_import_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_import_id INTEGER NOT NULL REFERENCES invoice_imports(id),
    supplier_product_id INTEGER REFERENCES supplier_products(id),
    line_description TEXT,
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    line_total REAL NOT NULL
);
"""


def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == column for r in rows)


def run_migrations(conn: sqlite3.Connection) -> None:
    conn.executescript(BUSINESS_SCHEMA_SQL)
    if not _has_column(conn, "supplier_products", "canonical_product_id"):
        conn.execute(
            "ALTER TABLE supplier_products ADD COLUMN canonical_product_id INTEGER REFERENCES canonical_products(id)"
        )
    if not _has_column(conn, "purchase_invoices", "import_id"):
        conn.execute(
            "ALTER TABLE purchase_invoices ADD COLUMN import_id INTEGER REFERENCES invoice_imports(id)"
        )
    conn.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES ('schema_version', '2-business')"
    )
