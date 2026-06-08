"""Repack costing."""

from __future__ import annotations

import sqlite3
from typing import Any

from procm.services.cost_engine import calculate_cost


def calculate_repack(conn: sqlite3.Connection, repack_id: int) -> dict[str, Any]:
    recipe = conn.execute("SELECT * FROM repack_recipes WHERE id = ?", (repack_id,)).fetchone()
    if not recipe:
        raise ValueError("Repack recipe not found")
    outputs = conn.execute(
        "SELECT * FROM repack_outputs WHERE repack_recipe_id = ?", (repack_id,)
    ).fetchall()
    if not outputs:
        raise ValueError("Repack output not defined")

    product = None
    if recipe["input_supplier_product_id"]:
        product = conn.execute(
            "SELECT * FROM supplier_products WHERE id = ?",
            (recipe["input_supplier_product_id"],),
        ).fetchone()

    input_qty = float(recipe["input_quantity"])
    input_price = float(product["current_price"] or 0) if product else 0
    input_cost = input_price

    output = outputs[0]
    output_qty = float(output["output_quantity"])
    if input_qty <= 0 or output_qty <= 0:
        raise ValueError("Invalid quantities")

    output_units = int(input_qty // output_qty) if output_qty else 0
    waste = input_qty - (output_units * output_qty)

    components = [
        {"component_type": "raw_material", "amount": input_cost, "source_reference": "bulk input"},
        {"component_type": "packaging", "amount": float(recipe["packaging_cost"])},
        {"component_type": "label", "amount": float(recipe["label_cost"])},
        {"component_type": "labor", "amount": float(recipe["labor_cost"])},
    ]
    result = calculate_cost(
        conn,
        components,
        units=max(output_units, 1),
        target_type="repack_recipe",
        target_id=repack_id,
        notes=recipe["name"],
    )
    cost_per_unit = result["unit_cost"]
    conn.execute(
        """
        INSERT INTO repack_costs (repack_recipe_id, cost_calculation_id, output_units, cost_per_output_unit, waste_remainder)
        VALUES (?, ?, ?, ?, ?)
        """,
        (repack_id, result["calculation_id"], output_units, cost_per_unit, waste),
    )
    result.update(
        {
            "output_units": output_units,
            "cost_per_output_unit": cost_per_unit,
            "waste_remainder": waste,
            "suggested_sale_price": output["suggested_sale_price"] or result["suggested_sale_price"],
        }
    )
    return result
