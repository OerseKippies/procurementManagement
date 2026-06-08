"""Recipe costing."""

from __future__ import annotations

import sqlite3
from typing import Any

from procm.services.cost_engine import calculate_cost


def calculate_recipe_cost(conn: sqlite3.Connection, version_id: int) -> dict[str, Any]:
    version = conn.execute(
        "SELECT * FROM recipe_versions WHERE id = ?", (version_id,)
    ).fetchone()
    if not version:
        raise ValueError("Recipe version not found")
    components = conn.execute(
        """
        SELECT rc.*, sp.supplier_product_name, sp.current_price
        FROM recipe_components rc
        LEFT JOIN supplier_products sp ON sp.id = rc.supplier_product_id
        WHERE rc.recipe_version_id = ?
        """,
        (version_id,),
    ).fetchall()
    cost_lines = []
    batch_cost = 0.0
    for comp in components:
        unit_cost = comp["unit_cost"] or comp["current_price"] or 0
        line_cost = float(unit_cost) * float(comp["quantity"])
        batch_cost += line_cost
        cost_lines.append(
            {
                "component_type": "raw_material",
                "amount": line_cost,
                "quantity_basis": f"{comp['quantity']} {comp['unit']}",
                "source_reference": comp["component_name"],
            }
        )
    batch_size = float(version["batch_size"]) or 1
    result = calculate_cost(
        conn,
        cost_lines,
        units=batch_size,
        target_type="recipe_version",
        target_id=version_id,
        notes=f"Recipe version {version_id}",
    )
    conn.execute(
        """
        INSERT INTO recipe_costs (recipe_version_id, cost_calculation_id, batch_cost, unit_cost)
        VALUES (?, ?, ?, ?)
        """,
        (version_id, result["calculation_id"], batch_cost, result["unit_cost"]),
    )
    result["batch_cost"] = batch_cost
    return result
