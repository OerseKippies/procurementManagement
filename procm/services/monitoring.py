"""Supplier watch and price alert services."""

from __future__ import annotations

import sqlite3
from typing import Any

from procm import intake
from procm.services.pricing import record_price


def refresh_watch(conn: sqlite3.Connection, watch_id: int) -> dict[str, Any]:
    watch = conn.execute(
        "SELECT * FROM supplier_watches WHERE id = ?", (watch_id,)
    ).fetchone()
    if not watch:
        raise ValueError("Watch not found")
    product = conn.execute(
        "SELECT * FROM supplier_products WHERE id = ?",
        (watch["supplier_product_id"],),
    ).fetchone()
    url = watch["source_url"] or (product["source_url"] if product else None)
    previous = watch["last_price"]
    new_price = product["current_price"] if product else None
    if url:
        html_content, _err = intake.fetch_page(url)
        parsed = intake.parse_product_page(url, html_content)
        if parsed.get("price") is not None:
            new_price = float(parsed["price"])
            record_price(conn, watch["supplier_product_id"], new_price, source="watch_refresh")
    change_percent = None
    if previous and new_price and previous > 0:
        change_percent = ((new_price - previous) / previous) * 100
    conn.execute(
        """
        UPDATE supplier_watches SET
            last_checked_at = datetime('now'),
            previous_price = last_price,
            last_price = ?,
            change_percent = ?
        WHERE id = ?
        """,
        (new_price, change_percent, watch_id),
    )
    _evaluate_alerts(conn, watch["supplier_product_id"], new_price)
    return {
        "watch_id": watch_id,
        "last_price": new_price,
        "previous_price": previous,
        "change_percent": change_percent,
    }


def _evaluate_alerts(
    conn: sqlite3.Connection, supplier_product_id: int, price: float | None
) -> None:
    if price is None:
        return
    alerts = conn.execute(
        """
        SELECT * FROM price_alerts
        WHERE supplier_product_id = ? AND status = 'active'
        """,
        (supplier_product_id,),
    ).fetchall()
    for alert in alerts:
        triggered = False
        if alert["alert_type"] == "target" and price <= alert["threshold_price"]:
            triggered = True
        if alert["alert_type"] == "maximum" and price >= alert["threshold_price"]:
            triggered = True
        if triggered:
            conn.execute(
                """
                UPDATE price_alerts SET status = 'triggered', triggered_at = datetime('now')
                WHERE id = ?
                """,
                (alert["id"],),
            )


def dashboard_price_moves(conn: sqlite3.Connection) -> dict[str, list]:
    increases = conn.execute(
        """
        SELECT sw.*, sp.supplier_product_name, s.name AS supplier_name
        FROM supplier_watches sw
        JOIN supplier_products sp ON sp.id = sw.supplier_product_id
        JOIN suppliers s ON s.id = sp.supplier_id
        WHERE sw.change_percent IS NOT NULL AND sw.change_percent > 0 AND sw.active = 1
        ORDER BY sw.change_percent DESC LIMIT 10
        """
    ).fetchall()
    drops = conn.execute(
        """
        SELECT sw.*, sp.supplier_product_name, s.name AS supplier_name
        FROM supplier_watches sw
        JOIN supplier_products sp ON sp.id = sw.supplier_product_id
        JOIN suppliers s ON s.id = sp.supplier_id
        WHERE sw.change_percent IS NOT NULL AND sw.change_percent < 0 AND sw.active = 1
        ORDER BY sw.change_percent ASC LIMIT 10
        """
    ).fetchall()
    return {"increases": increases, "drops": drops}
