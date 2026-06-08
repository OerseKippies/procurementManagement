"""Flask routes for procM MVP."""

from __future__ import annotations

import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for

from procm import intake
from procm.db import db_conn
from procm.services.cost_engine import COMPONENT_TYPES, calculate_cost
from procm.services.pricing import price_summary, record_price
from procm.services.recipe import calculate_recipe_cost
from procm.services.repack import calculate_repack
from procm.services.suggestions import generate_suggestion

bp = Blueprint("main", __name__)

NAV = [
    ("dashboard", "Dashboard"),
    ("suppliers_list", "Suppliers"),
    ("products_list", "Products"),
    ("url_intake", "URL Intake"),
    ("price_history", "Price History"),
    ("purchasing_hub", "Purchasing"),
    ("invoices_list", "Invoices"),
    ("invoice_import_page", "Invoice Import"),
    ("monitoring", "Monitoring"),
    ("canonical_products", "Canonical"),
    ("consumption", "Consumption"),
    ("forecasts", "Forecasts"),
    ("recipes_list", "Recipes"),
    ("repack_list", "Repack"),
    ("cost_calculator", "Cost Calculator"),
    ("suggestions_list", "Suggestions"),
    ("reports", "Reports"),
    ("settings_page", "Settings"),
]


@bp.app_context_processor
def inject_nav():
    return {"nav_items": NAV}


@bp.route("/")
def dashboard():
    from procm.services.monitoring import dashboard_price_moves

    with db_conn() as conn:
        stats = {
            "suppliers": conn.execute("SELECT COUNT(*) c FROM suppliers").fetchone()["c"],
            "products": conn.execute("SELECT COUNT(*) c FROM supplier_products").fetchone()["c"],
            "orders": conn.execute("SELECT COUNT(*) c FROM purchase_orders").fetchone()["c"],
            "suggestions": conn.execute(
                "SELECT COUNT(*) c FROM purchase_suggestions WHERE status = 'open'"
            ).fetchone()["c"],
            "imports": conn.execute("SELECT COUNT(*) c FROM import_jobs").fetchone()["c"],
            "recipes": conn.execute("SELECT COUNT(*) c FROM recipes").fetchone()["c"],
            "watches": conn.execute("SELECT COUNT(*) c FROM supplier_watches WHERE active=1").fetchone()["c"],
            "alerts": conn.execute("SELECT COUNT(*) c FROM price_alerts WHERE status='triggered'").fetchone()["c"],
        }
        recent = conn.execute(
            """
            SELECT ps.suggested_quantity, ps.reason, sp.supplier_product_name, s.name AS supplier_name
            FROM purchase_suggestions ps
            JOIN supplier_products sp ON sp.id = ps.supplier_product_id
            JOIN suppliers s ON s.id = ps.supplier_id
            ORDER BY ps.created_at DESC LIMIT 5
            """
        ).fetchall()
        moves = dashboard_price_moves(conn)
    return render_template(
        "dashboard.html", stats=stats, recent=recent, increases=moves["increases"], drops=moves["drops"]
    )


@bp.route("/suppliers", methods=["GET", "POST"])
def suppliers_list():
    if request.method == "POST":
        with db_conn() as conn:
            conn.execute(
                "INSERT INTO suppliers (name, domain, contact_email, notes) VALUES (?, ?, ?, ?)",
                (
                    request.form["name"],
                    request.form.get("domain"),
                    request.form.get("contact_email"),
                    request.form.get("notes"),
                ),
            )
        flash("Supplier opgeslagen.", "success")
        return redirect(url_for("main.suppliers_list"))
    with db_conn() as conn:
        rows = conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    return render_template("suppliers.html", suppliers=rows)


@bp.route("/suppliers/<int:supplier_id>/edit", methods=["GET", "POST"])
def supplier_edit(supplier_id: int):
    if request.method == "POST":
        with db_conn() as conn:
            conn.execute(
                """
                UPDATE suppliers SET name=?, domain=?, contact_email=?, contact_phone=?, notes=?, active=?
                WHERE id=?
                """,
                (
                    request.form["name"],
                    request.form.get("domain"),
                    request.form.get("contact_email"),
                    request.form.get("contact_phone"),
                    request.form.get("notes"),
                    1 if request.form.get("active") else 0,
                    supplier_id,
                ),
            )
        flash("Supplier bijgewerkt.", "success")
        return redirect(url_for("main.suppliers_list"))
    with db_conn() as conn:
        row = conn.execute("SELECT * FROM suppliers WHERE id=?", (supplier_id,)).fetchone()
    return render_template("supplier_edit.html", supplier=row)


@bp.route("/products", methods=["GET", "POST"])
def products_list():
    with db_conn() as conn:
        suppliers = conn.execute("SELECT id, name FROM suppliers ORDER BY name").fetchall()
        if request.method == "POST":
            cur = conn.execute(
                """
                INSERT INTO supplier_products (
                    supplier_id, supplier_sku, supplier_product_name, canonical_name, source_url,
                    package_size, package_unit, current_price, image_url, notes, active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.form["supplier_id"],
                    request.form.get("supplier_sku"),
                    request.form["supplier_product_name"],
                    request.form.get("canonical_name"),
                    request.form.get("source_url"),
                    request.form.get("package_size") or None,
                    request.form.get("package_unit"),
                    request.form.get("current_price") or None,
                    request.form.get("image_url"),
                    request.form.get("notes"),
                    1 if request.form.get("active", "on") else 0,
                ),
            )
            pid = cur.lastrowid
            if request.form.get("current_price"):
                record_price(conn, pid, float(request.form["current_price"]), source="manual")
            flash("Product opgeslagen.", "success")
            return redirect(url_for("main.products_list"))
        rows = conn.execute(
            """
            SELECT sp.*, s.name AS supplier_name FROM supplier_products sp
            JOIN suppliers s ON s.id = sp.supplier_id
            ORDER BY sp.supplier_product_name
            """
        ).fetchall()
    return render_template("products.html", products=rows, suppliers=suppliers)


@bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def product_edit(product_id: int):
    with db_conn() as conn:
        suppliers = conn.execute("SELECT id, name FROM suppliers ORDER BY name").fetchall()
        if request.method == "POST":
            old = conn.execute(
                "SELECT current_price FROM supplier_products WHERE id=?", (product_id,)
            ).fetchone()
            new_price = request.form.get("current_price")
            conn.execute(
                """
                UPDATE supplier_products SET
                    supplier_id=?, supplier_sku=?, supplier_product_name=?, canonical_name=?,
                    source_url=?, package_size=?, package_unit=?, current_price=?, currency=?,
                    image_url=?, notes=?, active=?, updated_at=datetime('now')
                WHERE id=?
                """,
                (
                    request.form["supplier_id"],
                    request.form.get("supplier_sku"),
                    request.form["supplier_product_name"],
                    request.form.get("canonical_name"),
                    request.form.get("source_url"),
                    request.form.get("package_size") or None,
                    request.form.get("package_unit"),
                    new_price or None,
                    request.form.get("currency", "EUR"),
                    request.form.get("image_url"),
                    request.form.get("notes"),
                    1 if request.form.get("active") else 0,
                    product_id,
                ),
            )
            if new_price and (not old or float(old["current_price"] or 0) != float(new_price)):
                record_price(conn, product_id, float(new_price), source="manual")
            flash("Product bijgewerkt.", "success")
            return redirect(url_for("main.products_list"))
        row = conn.execute("SELECT * FROM supplier_products WHERE id=?", (product_id,)).fetchone()
    return render_template("product_edit.html", product=row, suppliers=suppliers)


@bp.route("/url-intake", methods=["GET", "POST"])
def url_intake():
    result = None
    if request.method == "POST":
        url = request.form.get("source_url", "").strip()
        if not url:
            flash("URL is verplicht.", "error")
        else:
            with db_conn() as conn:
                result = intake.run_url_intake(conn, url)
            flash(f"Import job {result['import_job_id']} — status {result['status']}.", "success")
    with db_conn() as conn:
        jobs = conn.execute(
            """
            SELECT ij.*, s.name AS supplier_name, spi.supplier_product_id
            FROM import_jobs ij
            LEFT JOIN suppliers s ON s.id = ij.supplier_id
            LEFT JOIN supplier_product_imports spi ON spi.import_job_id = ij.id
            ORDER BY ij.created_at DESC LIMIT 20
            """
        ).fetchall()
    return render_template("url_intake.html", result=result, jobs=jobs)


@bp.route("/price-history")
def price_history():
    product_id = request.args.get("product_id", type=int)
    with db_conn() as conn:
        products = conn.execute(
            """
            SELECT sp.id, sp.supplier_product_name, s.name AS supplier_name
            FROM supplier_products sp JOIN suppliers s ON s.id = sp.supplier_id
            ORDER BY sp.supplier_product_name
            """
        ).fetchall()
        history = []
        summary = None
        if product_id:
            history = conn.execute(
                "SELECT * FROM price_history WHERE supplier_product_id=? ORDER BY recorded_date DESC",
                (product_id,),
            ).fetchall()
            summary = price_summary(conn, product_id)
    return render_template(
        "price_history.html",
        products=products,
        product_id=product_id,
        history=history,
        summary=summary,
    )


@bp.route("/purchase-orders", methods=["GET", "POST"])
def purchase_orders():
    with db_conn() as conn:
        suppliers = conn.execute("SELECT id, name FROM suppliers ORDER BY name").fetchall()
        products = conn.execute(
            """
            SELECT sp.id, sp.supplier_product_name, s.name AS supplier_name, sp.current_price
            FROM supplier_products sp JOIN suppliers s ON s.id = sp.supplier_id
            ORDER BY sp.supplier_product_name
            """
        ).fetchall()
        if request.method == "POST":
            supplier_id = int(request.form["supplier_id"])
            order_date = request.form.get("order_date") or conn.execute(
                "SELECT date('now')"
            ).fetchone()[0]
            cur = conn.execute(
                "INSERT INTO purchase_orders (supplier_id, order_date, status, notes) VALUES (?, ?, 'draft', ?)",
                (supplier_id, order_date, request.form.get("notes")),
            )
            po_id = cur.lastrowid
            pid = int(request.form["supplier_product_id"])
            qty = float(request.form["quantity"])
            price = float(request.form["unit_price"])
            conn.execute(
                """
                INSERT INTO purchase_order_lines (purchase_order_id, supplier_product_id, quantity, unit_price, line_total)
                VALUES (?, ?, ?, ?, ?)
                """,
                (po_id, pid, qty, price, qty * price),
            )
            flash(f"Inkooporder {po_id} aangemaakt.", "success")
            return redirect(url_for("main.purchase_orders"))
        orders = conn.execute(
            """
            SELECT po.*, s.name AS supplier_name,
                   (SELECT SUM(line_total) FROM purchase_order_lines WHERE purchase_order_id = po.id) AS total
            FROM purchase_orders po JOIN suppliers s ON s.id = po.supplier_id
            ORDER BY po.created_at DESC
            """
        ).fetchall()
    return render_template(
        "purchase_orders.html", orders=orders, suppliers=suppliers, products=products
    )


@bp.route("/purchase-orders/<int:po_id>/status", methods=["POST"])
def purchase_order_status(po_id: int):
    status = request.form.get("status", "draft")
    with db_conn() as conn:
        conn.execute("UPDATE purchase_orders SET status=? WHERE id=?", (status, po_id))
    flash(f"Status bijgewerkt naar {status}.", "success")
    return redirect(url_for("main.purchase_orders"))


@bp.route("/receipts", methods=["GET", "POST"])
def receipts_list():
    with db_conn() as conn:
        suppliers = conn.execute("SELECT id, name FROM suppliers ORDER BY name").fetchall()
        products = conn.execute(
            "SELECT id, supplier_product_name FROM supplier_products ORDER BY supplier_product_name"
        ).fetchall()
        if request.method == "POST":
            cur = conn.execute(
                """
                INSERT INTO purchase_receipts (supplier_id, purchase_order_id, received_date, notes)
                VALUES (?, ?, ?, ?)
                """,
                (
                    request.form["supplier_id"],
                    request.form.get("purchase_order_id") or None,
                    request.form.get("received_date"),
                    request.form.get("notes"),
                ),
            )
            rid = cur.lastrowid
            conn.execute(
                "INSERT INTO purchase_receipt_lines (purchase_receipt_id, supplier_product_id, quantity) VALUES (?, ?, ?)",
                (rid, request.form["supplier_product_id"], float(request.form["quantity"])),
            )
            if request.form.get("purchase_order_id"):
                conn.execute(
                    "UPDATE purchase_orders SET status='received' WHERE id=?",
                    (request.form["purchase_order_id"],),
                )
            flash("Ontvangst geregistreerd.", "success")
            return redirect(url_for("main.receipts_list"))
        rows = conn.execute(
            """
            SELECT pr.*, s.name AS supplier_name FROM purchase_receipts pr
            JOIN suppliers s ON s.id = pr.supplier_id ORDER BY pr.received_date DESC
            """
        ).fetchall()
    return render_template("receipts.html", receipts=rows, suppliers=suppliers, products=products)


@bp.route("/invoices", methods=["GET", "POST"])
def invoices_list():
    with db_conn() as conn:
        suppliers = conn.execute("SELECT id, name FROM suppliers ORDER BY name").fetchall()
        products = conn.execute(
            "SELECT id, supplier_product_name FROM supplier_products ORDER BY supplier_product_name"
        ).fetchall()
        if request.method == "POST":
            qty = float(request.form["quantity"])
            price = float(request.form["unit_price"])
            total = qty * price
            cur = conn.execute(
                """
                INSERT INTO purchase_invoices (supplier_id, invoice_number, invoice_date, invoice_total, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    request.form["supplier_id"],
                    request.form["invoice_number"],
                    request.form.get("invoice_date"),
                    total,
                    request.form.get("notes"),
                ),
            )
            iid = cur.lastrowid
            conn.execute(
                """
                INSERT INTO purchase_invoice_lines (purchase_invoice_id, supplier_product_id, quantity, unit_price, line_total)
                VALUES (?, ?, ?, ?, ?)
                """,
                (iid, request.form["supplier_product_id"], qty, price, total),
            )
            record_price(conn, int(request.form["supplier_product_id"]), price, source="invoice")
            flash("Factuur geregistreerd.", "success")
            return redirect(url_for("main.invoices_list"))
        rows = conn.execute(
            """
            SELECT pi.*, s.name AS supplier_name FROM purchase_invoices pi
            JOIN suppliers s ON s.id = pi.supplier_id ORDER BY pi.invoice_date DESC
            """
        ).fetchall()
    return render_template("invoices.html", invoices=rows, suppliers=suppliers, products=products)


@bp.route("/recipes")
def recipes_list():
    with db_conn() as conn:
        recipes = conn.execute(
            """
            SELECT r.*, rv.id AS version_id, rv.batch_size, rv.output_unit,
                   (SELECT batch_cost FROM recipe_costs WHERE recipe_version_id = rv.id ORDER BY id DESC LIMIT 1) AS last_batch_cost,
                   (SELECT unit_cost FROM recipe_costs WHERE recipe_version_id = rv.id ORDER BY id DESC LIMIT 1) AS last_unit_cost
            FROM recipes r
            JOIN recipe_versions rv ON rv.recipe_id = r.id AND rv.status = 'active'
            ORDER BY r.name
            """
        ).fetchall()
    return render_template("recipes.html", recipes=recipes)


@bp.route("/recipes/<int:version_id>/calculate", methods=["POST"])
def recipe_calculate(version_id: int):
    with db_conn() as conn:
        result = calculate_recipe_cost(conn, version_id)
    flash(
        f"Receptkost: batch €{result['batch_cost']:.2f}, per eenheid €{result['unit_cost']:.2f}.",
        "success",
    )
    return redirect(url_for("main.recipes_list"))


@bp.route("/repack")
def repack_list():
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT rr.*, sp.supplier_product_name,
                   ro.output_quantity, ro.output_unit, ro.suggested_sale_price,
                   (SELECT cost_per_output_unit FROM repack_costs WHERE repack_recipe_id = rr.id ORDER BY id DESC LIMIT 1) AS last_unit_cost
            FROM repack_recipes rr
            LEFT JOIN supplier_products sp ON sp.id = rr.input_supplier_product_id
            LEFT JOIN repack_outputs ro ON ro.repack_recipe_id = rr.id
            ORDER BY rr.name
            """
        ).fetchall()
    return render_template("repack.html", repacks=rows)


@bp.route("/repack/<int:repack_id>/calculate", methods=["POST"])
def repack_calculate(repack_id: int):
    with db_conn() as conn:
        result = calculate_repack(conn, repack_id)
    flash(
        f"Repack: {result['output_units']} eenheden, €{result['cost_per_output_unit']:.2f}/stuk, rest {result['waste_remainder']:.2f}.",
        "success",
    )
    return redirect(url_for("main.repack_list"))


@bp.route("/cost-calculator", methods=["GET", "POST"])
def cost_calculator():
    result = None
    if request.method == "POST":
        components = []
        for ctype in COMPONENT_TYPES:
            val = request.form.get(f"amount_{ctype}")
            if val:
                components.append({"component_type": ctype, "amount": float(val)})
        units = float(request.form.get("units") or 1)
        margin = float(request.form.get("margin_percent") or 30)
        with db_conn() as conn:
            result = calculate_cost(conn, components, units=units, target_margin_percent=margin)
    return render_template(
        "cost_calculator.html", result=result, component_types=COMPONENT_TYPES
    )


@bp.route("/suggestions", methods=["GET", "POST"])
def suggestions_list():
    if request.method == "POST":
        with db_conn() as conn:
            generate_suggestion(
                conn,
                int(request.form["supplier_product_id"]),
                current_quantity=float(request.form.get("current_quantity") or 0),
                minimum_desired=float(request.form.get("minimum_desired") or 0),
                usage_per_week=float(request.form.get("usage_per_week") or 0),
                lead_time_weeks=float(request.form.get("lead_time_weeks") or 1),
                safety_buffer=float(request.form.get("safety_buffer") or 1),
            )
        flash("Inkoopadvies gegenereerd.", "success")
        return redirect(url_for("main.suggestions_list"))
    with db_conn() as conn:
        products = conn.execute(
            """
            SELECT sp.id, sp.supplier_product_name, s.name AS supplier_name
            FROM supplier_products sp JOIN suppliers s ON s.id = sp.supplier_id
            ORDER BY sp.supplier_product_name
            """
        ).fetchall()
        rows = conn.execute(
            """
            SELECT ps.*, sp.supplier_product_name, s.name AS supplier_name
            FROM purchase_suggestions ps
            JOIN supplier_products sp ON sp.id = ps.supplier_product_id
            JOIN suppliers s ON s.id = ps.supplier_id
            ORDER BY ps.created_at DESC
            """
        ).fetchall()
    return render_template("suggestions.html", suggestions=rows, products=products)


@bp.route("/matching", methods=["GET", "POST"])
def matching_list():
    with db_conn() as conn:
        products = conn.execute(
            "SELECT id, supplier_product_name FROM supplier_products ORDER BY supplier_product_name"
        ).fetchall()
        if request.method == "POST":
            conn.execute(
                """
                INSERT INTO product_matches (
                    source_supplier_product_id, target_supplier_product_id,
                    confidence, decision, notes
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    request.form["source_id"],
                    request.form["target_id"],
                    float(request.form.get("confidence") or 0.5),
                    request.form.get("decision", "unknown"),
                    request.form.get("notes"),
                ),
            )
            match_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.execute(
                "INSERT INTO match_decisions (product_match_id, decision) VALUES (?, ?)",
                (match_id, request.form.get("decision", "unknown")),
            )
            flash("Match opgeslagen.", "success")
            return redirect(url_for("main.matching_list"))
        rows = conn.execute(
            """
            SELECT pm.*,
                   sp1.supplier_product_name AS source_name,
                   sp2.supplier_product_name AS target_name
            FROM product_matches pm
            JOIN supplier_products sp1 ON sp1.id = pm.source_supplier_product_id
            JOIN supplier_products sp2 ON sp2.id = pm.target_supplier_product_id
            ORDER BY pm.created_at DESC
            """
        ).fetchall()
    return render_template("matching.html", matches=rows, products=products)


@bp.route("/intelligence")
def intelligence():
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT s.name AS supplier_name, sp.supplier_product_name, sp.package_size, sp.package_unit,
                   sp.current_price, sp.updated_at AS last_checked,
                   CASE WHEN sp.package_size > 0 THEN sp.current_price / sp.package_size ELSE sp.current_price END AS effective_unit_cost,
                   (SELECT shipping_cost FROM supplier_prices WHERE supplier_product_id = sp.id ORDER BY id DESC LIMIT 1) AS shipping
            FROM supplier_products sp
            JOIN suppliers s ON s.id = sp.supplier_id
            WHERE sp.active = 1
            ORDER BY sp.canonical_name, effective_unit_cost
            """
        ).fetchall()
    return render_template("intelligence.html", rows=rows)


@bp.route("/settings", methods=["GET", "POST"])
def settings_page():
    if request.method == "POST":
        with db_conn() as conn:
            for key in ("default_margin_percent", "company_name"):
                if key in request.form:
                    conn.execute(
                        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (key, request.form[key]),
                    )
        flash("Instellingen opgeslagen.", "success")
        return redirect(url_for("main.settings_page"))
    with db_conn() as conn:
        settings = {
            r["key"]: r["value"]
            for r in conn.execute("SELECT key, value FROM settings").fetchall()
        }
    return render_template("settings.html", settings=settings)


@bp.route("/health")
def health():
    return {"status": "ok", "module": "procM", "edition": "business"}


from procm.business_routes import register_business_routes  # noqa: E402

register_business_routes(bp)
