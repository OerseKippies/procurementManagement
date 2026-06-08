"""Cost calculation engine."""

from __future__ import annotations

import sqlite3
from typing import Any


COMPONENT_TYPES = (
    "raw_material",
    "packaging",
    "label",
    "labor",
    "shipping",
    "overhead",
    "other",
)


def calculate_cost(
    conn: sqlite3.Connection,
    components: list[dict[str, Any]],
    *,
    units: float = 1,
    target_margin_percent: float = 30,
    cost_model_id: int | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    total = sum(float(c.get("amount", 0)) for c in components)
    unit_cost = total / units if units > 0 else total
    margin_factor = 1 + (target_margin_percent / 100)
    suggested_sale = unit_cost * margin_factor if unit_cost else 0
    margin_euro = suggested_sale - unit_cost
    margin_percent = target_margin_percent

    cur = conn.execute(
        """
        INSERT INTO cost_calculations (
            cost_model_id, target_type, target_id, total_cost, unit_cost,
            suggested_sale_price, margin_euro, margin_percent, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            cost_model_id,
            target_type,
            target_id,
            total,
            unit_cost,
            suggested_sale,
            margin_euro,
            margin_percent,
            notes,
        ),
    )
    calc_id = cur.lastrowid
    for comp in components:
        conn.execute(
            """
            INSERT INTO cost_components (cost_calculation_id, component_type, amount, quantity_basis, source_reference)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                calc_id,
                comp.get("component_type", "other"),
                float(comp.get("amount", 0)),
                comp.get("quantity_basis"),
                comp.get("source_reference"),
            ),
        )
    return {
        "calculation_id": calc_id,
        "total_cost": total,
        "unit_cost": unit_cost,
        "suggested_sale_price": suggested_sale,
        "margin_euro": margin_euro,
        "margin_percent": margin_percent,
        "components": components,
    }
