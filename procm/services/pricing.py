"""Price history helpers."""

from __future__ import annotations

import sqlite3
from typing import Any


def record_price(
    conn: sqlite3.Connection,
    supplier_product_id: int,
    price: float,
    *,
    source: str = "manual",
    shipping_cost: float = 0,
    notes: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO supplier_prices (supplier_product_id, price, shipping_cost, source, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (supplier_product_id, price, shipping_cost, source, notes),
    )
    product = conn.execute(
        "SELECT package_size FROM supplier_products WHERE id = ?",
        (supplier_product_id,),
    ).fetchone()
    package_size = product["package_size"] if product else None
    effective = price
    if package_size and package_size > 0:
        effective = (price + shipping_cost) / package_size
    conn.execute(
        """
        INSERT INTO price_history (supplier_product_id, unit_price, effective_unit_cost, source, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (supplier_product_id, price, effective, source, notes),
    )
    conn.execute(
        "UPDATE supplier_products SET current_price = ?, updated_at = datetime('now') WHERE id = ?",
        (price, supplier_product_id),
    )


def price_summary(conn: sqlite3.Connection, supplier_product_id: int) -> dict[str, Any]:
    rows = conn.execute(
        """
        SELECT unit_price, recorded_date FROM price_history
        WHERE supplier_product_id = ?
        ORDER BY recorded_date DESC, id DESC
        """,
        (supplier_product_id,),
    ).fetchall()
    if not rows:
        return {
            "current": None,
            "previous": None,
            "difference": None,
            "lowest": None,
            "highest": None,
            "last_checked": None,
        }
    prices = [r["unit_price"] for r in rows]
    current = prices[0]
    previous = prices[1] if len(prices) > 1 else None
    diff = (current - previous) if previous is not None else None
    return {
        "current": current,
        "previous": previous,
        "difference": diff,
        "lowest": min(prices),
        "highest": max(prices),
        "average": sum(prices) / len(prices),
        "last_checked": rows[0]["recorded_date"],
        "history": [dict(r) for r in rows],
    }
