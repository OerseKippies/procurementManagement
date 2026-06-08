"""Report generation and CSV/Excel export."""

from __future__ import annotations

import csv
import io
import sqlite3
from typing import Any

try:
    import openpyxl
except ImportError:  # pragma: no cover
    openpyxl = None


def _to_csv(headers: list[str], rows: list[list[Any]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    return buf.getvalue()


def purchase_history_report(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        """
        SELECT po.id, s.name, po.order_date, po.status, pol.quantity, sp.supplier_product_name, pol.unit_price, pol.line_total
        FROM purchase_orders po
        JOIN suppliers s ON s.id = po.supplier_id
        JOIN purchase_order_lines pol ON pol.purchase_order_id = po.id
        JOIN supplier_products sp ON sp.id = pol.supplier_product_id
        ORDER BY po.order_date DESC, po.id DESC
        """
    ).fetchall()
    return _to_csv(
        ["order_id", "supplier", "order_date", "status", "qty", "product", "unit_price", "line_total"],
        [[r[c] for c in r.keys()] for r in rows],
    )


def supplier_history_report(conn: sqlite3.Connection, supplier_id: int | None = None) -> str:
    q = """
        SELECT s.name, sp.supplier_product_name, ph.recorded_date, ph.unit_price, ph.source
        FROM price_history ph
        JOIN supplier_products sp ON sp.id = ph.supplier_product_id
        JOIN suppliers s ON s.id = sp.supplier_id
    """
    params: tuple = ()
    if supplier_id:
        q += " WHERE s.id = ?"
        params = (supplier_id,)
    q += " ORDER BY ph.recorded_date DESC"
    rows = conn.execute(q, params).fetchall()
    return _to_csv(
        ["supplier", "product", "date", "price", "source"],
        [[r["name"], r["supplier_product_name"], r["recorded_date"], r["unit_price"], r["source"]] for r in rows],
    )


def recipe_cost_report(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        """
        SELECT r.name, rv.version_number, rc.batch_cost, rc.unit_cost, rc.calculated_at
        FROM recipe_costs rc
        JOIN recipe_versions rv ON rv.id = rc.recipe_version_id
        JOIN recipes r ON r.id = rv.recipe_id
        ORDER BY rc.calculated_at DESC
        """
    ).fetchall()
    return _to_csv(
        ["recipe", "version", "batch_cost", "unit_cost", "calculated_at"],
        [[r[c] for c in ["name", "version_number", "batch_cost", "unit_cost", "calculated_at"]] for r in rows],
    )


def repack_history_report(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        """
        SELECT rr.name, rpc.output_units, rpc.cost_per_output_unit, rpc.waste_remainder, rpc.calculated_at
        FROM repack_costs rpc
        JOIN repack_recipes rr ON rr.id = rpc.repack_recipe_id
        ORDER BY rpc.calculated_at DESC
        """
    ).fetchall()
    return _to_csv(
        ["repack", "output_units", "cost_per_unit", "waste", "calculated_at"],
        [[r[c] for c in r.keys()] for r in rows],
    )


def to_excel(sheet_name: str, headers: list[str], rows: list[list[Any]]) -> bytes:
    if openpyxl is None:
        raise RuntimeError("openpyxl not installed")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name[:31]
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
