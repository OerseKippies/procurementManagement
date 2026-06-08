"""Purchase suggestion engine."""

from __future__ import annotations

import math
import sqlite3
from typing import Any


def generate_suggestion(
    conn: sqlite3.Connection,
    supplier_product_id: int,
    *,
    current_quantity: float,
    minimum_desired: float,
    usage_per_week: float,
    lead_time_weeks: float = 1,
    safety_buffer: float = 1,
) -> dict[str, Any]:
    product = conn.execute(
        """
        SELECT sp.*, s.name AS supplier_name, s.id AS supplier_id
        FROM supplier_products sp
        JOIN suppliers s ON s.id = sp.supplier_id
        WHERE sp.id = ?
        """,
        (supplier_product_id,),
    ).fetchone()
    if not product:
        raise ValueError("Supplier product not found")

    weeks_cover = lead_time_weeks + safety_buffer
    needed_for_usage = usage_per_week * weeks_cover
    shortfall = max(0, minimum_desired - current_quantity)
    suggested = max(shortfall, math.ceil(needed_for_usage - current_quantity))
    if suggested <= 0:
        suggested = 0
        reason = "Stock boven minimum en voldoende voor lead time."
    else:
        reason = (
            f"Huidig {current_quantity}, minimum {minimum_desired}, "
            f"verbruik {usage_per_week}/week, lead time {lead_time_weeks}w + buffer {safety_buffer}."
        )

    cur = conn.execute(
        """
        INSERT INTO purchase_suggestions (supplier_product_id, supplier_id, suggested_quantity, reason, priority)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            supplier_product_id,
            product["supplier_id"],
            suggested,
            reason,
            "high" if suggested > 0 else "low",
        ),
    )
    suggestion_id = cur.lastrowid
    conn.execute(
        "INSERT INTO procurement_recommendations (purchase_suggestion_id, summary) VALUES (?, ?)",
        (
            suggestion_id,
            f"Bestel {suggested} × {product['supplier_product_name']} bij {product['supplier_name']}",
        ),
    )
    return {
        "suggestion_id": suggestion_id,
        "suggested_quantity": suggested,
        "reason": reason,
        "supplier_name": product["supplier_name"],
        "product_name": product["supplier_product_name"],
    }


def generate_suggestion_enhanced(conn: sqlite3.Connection, supplier_product_id: int) -> dict[str, Any]:
    """Suggestion using forecast profile and cheapest supplier for canonical product."""
    from procm.services.forecast import compute_forecast

    forecast = compute_forecast(conn, supplier_product_id)
    product = conn.execute(
        "SELECT * FROM supplier_products WHERE id = ?", (supplier_product_id,)
    ).fetchone()
    preferred_supplier_id = None
    if product and product["canonical_product_id"]:
        best = conn.execute(
            """
            SELECT sp.id, sp.supplier_id, sp.current_price, s.name
            FROM supplier_products sp
            JOIN suppliers s ON s.id = sp.supplier_id
            WHERE sp.canonical_product_id = ? AND sp.active = 1 AND sp.current_price IS NOT NULL
            ORDER BY sp.current_price ASC LIMIT 1
            """,
            (product["canonical_product_id"],),
        ).fetchone()
        if best:
            supplier_product_id = best["id"]
            preferred_supplier_id = best["supplier_id"]

    qty = 0
    reason_parts = []
    if forecast.get("reorder_in_days") is not None and forecast["reorder_in_days"] <= 0:
        daily = forecast.get("avg_daily_consumption") or 1
        qty = max(1, int(daily * (forecast["lead_time_days"] + forecast["safety_days"])))
        if forecast.get("days_remaining") is not None:
            reason_parts.append(f"Forecast: {forecast['days_remaining']:.1f} dagen resterend")
    if not qty:
        return generate_suggestion(
            conn,
            supplier_product_id,
            current_quantity=forecast.get("current_planning_qty") or 0,
            minimum_desired=2,
            usage_per_week=(forecast.get("avg_daily_consumption") or 0) * 7,
        )
    prod = conn.execute(
        """
        SELECT sp.*, s.name AS supplier_name FROM supplier_products sp
        JOIN suppliers s ON s.id = sp.supplier_id WHERE sp.id = ?
        """,
        (supplier_product_id,),
    ).fetchone()
    sid = preferred_supplier_id or prod["supplier_id"]
    reason = "; ".join(reason_parts) + f" — voorkeur leverancier op prijs."
    cur = conn.execute(
        """
        INSERT INTO purchase_suggestions (supplier_product_id, supplier_id, suggested_quantity, reason, priority)
        VALUES (?, ?, ?, ?, 'high')
        """,
        (supplier_product_id, sid, qty, reason),
    )
    return {
        "suggestion_id": cur.lastrowid,
        "suggested_quantity": qty,
        "reason": reason,
        "supplier_name": prod["supplier_name"],
        "product_name": prod["supplier_product_name"],
    }
