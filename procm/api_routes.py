"""procM consumption API for Co-Pilot integration."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from procm.db import db_conn, row_to_dict

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _rows_to_list(rows):
    return [row_to_dict(r) for r in rows]


@api_bp.route("/suppliers", methods=["GET"])
def api_suppliers():
    active = request.args.get("active", type=int)
    with db_conn() as conn:
        if active is not None:
            rows = conn.execute(
                "SELECT * FROM suppliers WHERE active = ? ORDER BY name", (active,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    data = _rows_to_list(rows)
    return jsonify({"data": data, "count": len(data)})


@api_bp.route("/supplier-products", methods=["GET"])
def api_supplier_products():
    supplier_id = request.args.get("supplier_id", type=int)
    active = request.args.get("active", type=int)
    sql = """
        SELECT sp.*, s.name AS supplier_name
        FROM supplier_products sp
        JOIN suppliers s ON s.id = sp.supplier_id
        WHERE 1=1
    """
    params: list = []
    if supplier_id:
        sql += " AND sp.supplier_id = ?"
        params.append(supplier_id)
    if active is not None:
        sql += " AND sp.active = ?"
        params.append(active)
    sql += " ORDER BY sp.supplier_product_name"
    with db_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    data = _rows_to_list(rows)
    return jsonify({"data": data, "count": len(data)})


@api_bp.route("/purchase-suggestions", methods=["GET"])
def api_purchase_suggestions():
    status = request.args.get("status", "open")
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT ps.*, sp.supplier_product_name, s.name AS supplier_name
            FROM purchase_suggestions ps
            JOIN supplier_products sp ON sp.id = ps.supplier_product_id
            LEFT JOIN suppliers s ON s.id = ps.supplier_id
            WHERE ps.status = ?
            ORDER BY ps.created_at DESC
            """,
            (status,),
        ).fetchall()
    data = _rows_to_list(rows)
    return jsonify({"data": data, "count": len(data)})


@api_bp.route("/recipes", methods=["GET"])
def api_recipes():
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT r.id, r.name, r.active, r.notes,
                   rv.id AS version_id, rv.version_number, rv.batch_size, rv.output_unit, rv.status
            FROM recipes r
            JOIN recipe_versions rv ON rv.recipe_id = r.id AND rv.status = 'active'
            ORDER BY r.name
            """
        ).fetchall()
    data = _rows_to_list(rows)
    return jsonify({"data": data, "count": len(data)})


@api_bp.route("/cost-calculations", methods=["GET"])
def api_cost_calculations():
    limit = min(100, max(1, request.args.get("limit", 50, type=int)))
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, cost_model_id, target_type, target_id,
                   total_cost, unit_cost, suggested_sale_price,
                   margin_euro, margin_percent, calculated_at, notes
            FROM cost_calculations
            ORDER BY calculated_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
    data = _rows_to_list(rows)
    return jsonify({"data": data, "count": len(data)})


@api_bp.route("/dashboard-summary", methods=["GET"])
def api_dashboard_summary():
    with db_conn() as conn:
        suppliers = conn.execute(
            "SELECT COUNT(*) c FROM suppliers WHERE active = 1"
        ).fetchone()["c"]
        products = conn.execute(
            "SELECT COUNT(*) c FROM supplier_products WHERE active = 1"
        ).fetchone()["c"]
        open_suggestions = conn.execute(
            "SELECT COUNT(*) c FROM purchase_suggestions WHERE status = 'open'"
        ).fetchone()["c"]
        orders = conn.execute("SELECT COUNT(*) c FROM purchase_orders").fetchone()["c"]
        recent = conn.execute(
            """
            SELECT po.id, po.order_date, po.status, s.name AS supplier_name
            FROM purchase_orders po
            JOIN suppliers s ON s.id = po.supplier_id
            ORDER BY po.created_at DESC LIMIT 5
            """
        ).fetchall()
    return jsonify(
        {
            "suppliers_count": suppliers,
            "supplier_products_count": products,
            "open_purchase_suggestions": open_suggestions,
            "purchase_orders_count": orders,
            "recent_purchase_orders": _rows_to_list(recent),
            "module": "procM",
            "status": "PROCUREMENT MVP COMPLETE",
        }
    )


@api_bp.route("/copilot/dashboard", methods=["GET"])
def api_copilot_dashboard():
    with db_conn() as conn:
        suppliers = conn.execute(
            "SELECT COUNT(*) c FROM suppliers WHERE active = 1"
        ).fetchone()["c"]
        products = conn.execute(
            "SELECT COUNT(*) c FROM supplier_products WHERE active = 1"
        ).fetchone()["c"]
        open_suggestions = conn.execute(
            "SELECT COUNT(*) c FROM purchase_suggestions WHERE status = 'open'"
        ).fetchone()["c"]
        reorder = conn.execute(
            """
            SELECT COUNT(DISTINCT supplier_product_id) c
            FROM purchase_suggestions WHERE status = 'open'
            """
        ).fetchone()["c"]
        recent = conn.execute(
            """
            SELECT po.id, po.order_date, po.status, s.name AS supplier_name,
                   COALESCE((SELECT SUM(line_total) FROM purchase_order_lines
                             WHERE purchase_order_id = po.id), 0) AS total
            FROM purchase_orders po
            JOIN suppliers s ON s.id = po.supplier_id
            ORDER BY po.created_at DESC LIMIT 10
            """
        ).fetchall()
        generated_at = conn.execute("SELECT datetime('now')").fetchone()[0]
    return jsonify(
        {
            "suppliers_count": suppliers,
            "supplier_products_count": products,
            "products_needing_reorder": reorder,
            "active_purchase_suggestions": open_suggestions,
            "recent_purchases": _rows_to_list(recent),
            "generated_at": generated_at,
            "contract": "procM.copilot.dashboard.v1",
        }
    )
