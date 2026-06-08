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
