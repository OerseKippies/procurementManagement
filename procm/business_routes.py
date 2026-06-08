"""Business edition routes — monitoring, forecasts, reports, canonical, imports."""

from __future__ import annotations

from io import BytesIO

from flask import flash, redirect, render_template, request, send_file, url_for

from procm.db import db_conn
from procm.services.forecast import compute_forecast, record_consumption_event
from procm.services.invoice_import import import_csv, import_excel
from procm.services.monitoring import dashboard_price_moves, refresh_watch
from procm.services.recipe import calculate_recipe_cost
from procm.services.repack import calculate_repack
from procm.services.reports import (
    purchase_history_report,
    recipe_cost_report,
    repack_history_report,
    supplier_history_report,
    to_excel,
)
from procm.services.suggestions import generate_suggestion_enhanced


def register_business_routes(bp) -> None:
  """Register business edition endpoints on the main blueprint."""

  @bp.route("/purchasing")
  def purchasing_hub():
      with db_conn() as conn:
          orders = conn.execute(
              """
              SELECT po.*, s.name AS supplier_name,
                     (SELECT SUM(line_total) FROM purchase_order_lines WHERE purchase_order_id = po.id) AS total
              FROM purchase_orders po JOIN suppliers s ON s.id = po.supplier_id
              ORDER BY po.created_at DESC LIMIT 20
              """
          ).fetchall()
      return render_template("purchasing.html", orders=orders)

  @bp.route("/monitoring", methods=["GET", "POST"])
  def monitoring():
      if request.method == "POST":
          action = request.form.get("action")
          with db_conn() as conn:
              if action == "add_watch":
                  conn.execute(
                      """
                      INSERT INTO supplier_watches (supplier_product_id, source_url, last_price, active)
                      SELECT id, source_url, current_price, 1 FROM supplier_products WHERE id = ?
                      """,
                      (request.form["supplier_product_id"],),
                  )
                  flash("Product toegevoegd aan watchlist.", "success")
              elif action == "refresh":
                  refresh_watch(conn, int(request.form["watch_id"]))
                  flash("Prijs ververst.", "success")
              elif action == "add_alert":
                  conn.execute(
                      """
                      INSERT INTO price_alerts (supplier_product_id, alert_type, threshold_price, status)
                      VALUES (?, ?, ?, 'active')
                      """,
                      (
                          request.form["supplier_product_id"],
                          request.form["alert_type"],
                          float(request.form["threshold_price"]),
                      ),
                  )
                  flash("Price alert aangemaakt.", "success")
              elif action == "dismiss_alert":
                  conn.execute(
                      "UPDATE price_alerts SET status = 'dismissed' WHERE id = ?",
                      (request.form["alert_id"],),
                  )
      with db_conn() as conn:
          watches = conn.execute(
              """
              SELECT sw.*, sp.supplier_product_name, s.name AS supplier_name
              FROM supplier_watches sw
              JOIN supplier_products sp ON sp.id = sw.supplier_product_id
              JOIN suppliers s ON s.id = sp.supplier_id
              WHERE sw.active = 1 ORDER BY sw.last_checked_at DESC
              """
          ).fetchall()
          alerts = conn.execute(
              """
              SELECT pa.*, sp.supplier_product_name FROM price_alerts pa
              JOIN supplier_products sp ON sp.id = pa.supplier_product_id
              ORDER BY pa.created_at DESC LIMIT 30
              """
          ).fetchall()
          products = conn.execute(
              "SELECT id, supplier_product_name FROM supplier_products WHERE active = 1 ORDER BY supplier_product_name"
          ).fetchall()
          moves = dashboard_price_moves(conn)
      return render_template(
          "monitoring.html",
          watches=watches,
          alerts=alerts,
          products=products,
          increases=moves["increases"],
          drops=moves["drops"],
      )

  @bp.route("/canonical", methods=["GET", "POST"])
  def canonical_products():
      if request.method == "POST":
          action = request.form.get("action")
          with db_conn() as conn:
              if action == "create":
                  conn.execute(
                      "INSERT INTO canonical_products (name, description, category) VALUES (?, ?, ?)",
                      (
                          request.form["name"],
                          request.form.get("description"),
                          request.form.get("category"),
                      ),
                  )
              elif action == "link":
                  conn.execute(
                      "UPDATE supplier_products SET canonical_product_id = ? WHERE id = ?",
                      (request.form["canonical_product_id"], request.form["supplier_product_id"]),
                  )
          flash("Canonical product bijgewerkt.", "success")
          return redirect(url_for("main.canonical_products"))
      with db_conn() as conn:
          canonical = conn.execute(
              "SELECT * FROM canonical_products WHERE active = 1 ORDER BY name"
          ).fetchall()
          linked = conn.execute(
              """
              SELECT sp.id, sp.supplier_product_name, s.name AS supplier_name,
                     sp.current_price, sp.package_size, sp.package_unit, cp.name AS canonical_name
              FROM supplier_products sp
              JOIN suppliers s ON s.id = sp.supplier_id
              LEFT JOIN canonical_products cp ON cp.id = sp.canonical_product_id
              ORDER BY cp.name, sp.supplier_product_name
              """
          ).fetchall()
          products = conn.execute(
              "SELECT id, supplier_product_name FROM supplier_products ORDER BY supplier_product_name"
          ).fetchall()
      return render_template(
          "canonical.html", canonical=canonical, linked=linked, products=products
      )

  @bp.route("/consumption", methods=["GET", "POST"])
  def consumption():
      if request.method == "POST":
          with db_conn() as conn:
              record_consumption_event(
                  conn,
                  int(request.form["supplier_product_id"]),
                  request.form["event_type"],
                  float(request.form["quantity"]),
                  request.form.get("unit") or "kg",
                  request.form.get("notes"),
              )
          flash("Verbruik geregistreerd (planning data, geen voorraad).", "success")
          return redirect(url_for("main.consumption"))
      with db_conn() as conn:
          products = conn.execute(
              """
              SELECT sp.id, sp.supplier_product_name, s.name AS supplier_name
              FROM supplier_products sp JOIN suppliers s ON s.id = sp.supplier_id
              ORDER BY sp.supplier_product_name
              """
          ).fetchall()
          events = conn.execute(
              """
              SELECT ce.*, sp.supplier_product_name FROM consumption_events ce
              JOIN supplier_products sp ON sp.id = ce.supplier_product_id
              ORDER BY ce.event_date DESC, ce.id DESC LIMIT 50
              """
          ).fetchall()
      return render_template("consumption.html", products=products, events=events)

  @bp.route("/forecasts", methods=["GET", "POST"])
  def forecasts():
      forecast = None
      if request.method == "POST":
          action = request.form.get("action")
          with db_conn() as conn:
              pid = int(request.form["supplier_product_id"])
              if action == "profile":
                  conn.execute(
                      """
                      INSERT INTO forecast_profiles (
                          supplier_product_id, current_planning_qty, safety_days, lead_time_days, preferred_supplier_id, updated_at
                      ) VALUES (?, ?, ?, ?, ?, datetime('now'))
                      ON CONFLICT(supplier_product_id) DO UPDATE SET
                          current_planning_qty = excluded.current_planning_qty,
                          safety_days = excluded.safety_days,
                          lead_time_days = excluded.lead_time_days,
                          preferred_supplier_id = excluded.preferred_supplier_id,
                          updated_at = datetime('now')
                      """,
                      (
                          pid,
                          float(request.form.get("current_planning_qty") or 0),
                          int(request.form.get("safety_days") or 7),
                          int(request.form.get("lead_time_days") or 7),
                          request.form.get("preferred_supplier_id") or None,
                      ),
                  )
              elif action == "suggest":
                  generate_suggestion_enhanced(conn, pid)
                  flash("Inkoopadvies gegenereerd op basis van forecast.", "success")
              forecast = compute_forecast(conn, pid)
      else:
          pid = request.args.get("product_id", type=int)
          if pid:
              with db_conn() as conn:
                  forecast = compute_forecast(conn, pid)
      with db_conn() as conn:
          products = conn.execute(
              """
              SELECT sp.id, sp.supplier_product_name, s.name AS supplier_name
              FROM supplier_products sp JOIN suppliers s ON s.id = sp.supplier_id
              ORDER BY sp.supplier_product_name
              """
          ).fetchall()
          suppliers = conn.execute("SELECT id, name FROM suppliers ORDER BY name").fetchall()
      return render_template(
          "forecasts.html",
          products=products,
          suppliers=suppliers,
          forecast=forecast,
          product_id=request.args.get("product_id", type=int)
          or (request.form.get("supplier_product_id") if request.method == "POST" else None),
      )

  @bp.route("/invoices/import", methods=["GET", "POST"])
  def invoice_import_page():
      if request.method == "POST":
          supplier_id = int(request.form["supplier_id"]) if request.form.get("supplier_id") else None
          with db_conn() as conn:
              if request.form.get("csv_text"):
                  result = import_csv(
                      conn,
                      request.form["csv_text"],
                      supplier_id=supplier_id,
                      filename="paste.csv",
                  )
              elif "file" in request.files and request.files["file"].filename:
                  f = request.files["file"]
                  name = f.filename or "upload"
                  data = f.read()
                  if name.lower().endswith((".xlsx", ".xls")):
                      result = import_excel(conn, data, supplier_id=supplier_id, filename=name)
                  else:
                      result = import_csv(
                          conn, data.decode("utf-8", errors="replace"), supplier_id=supplier_id, filename=name
                      )
              else:
                  flash("Geen bestand of CSV tekst.", "error")
                  return redirect(url_for("main.invoice_import_page"))
          flash(f"Import #{result['import_id']}: {result['line_count']} regels, €{result['invoice_total']:.2f}.", "success")
          return redirect(url_for("main.invoices_list"))
      with db_conn() as conn:
          suppliers = conn.execute("SELECT id, name FROM suppliers ORDER BY name").fetchall()
          imports = conn.execute(
              "SELECT * FROM invoice_imports ORDER BY imported_at DESC LIMIT 20"
          ).fetchall()
      return render_template("invoice_import.html", suppliers=suppliers, imports=imports)

  @bp.route("/recipes/builder", methods=["GET", "POST"])
  def recipe_builder():
      if request.method == "POST":
          with db_conn() as conn:
              rcur = conn.execute(
                  "INSERT INTO recipes (name, notes) VALUES (?, ?)",
                  (request.form["name"], request.form.get("notes")),
              )
              recipe_id = rcur.lastrowid
              max_v = conn.execute(
                  "SELECT COALESCE(MAX(version_number), 0) + 1 AS v FROM recipe_versions WHERE recipe_id = ?",
                  (recipe_id,),
              ).fetchone()["v"]
              vcur = conn.execute(
                  """
                  INSERT INTO recipe_versions (recipe_id, version_number, batch_size, output_unit, status)
                  VALUES (?, ?, ?, ?, 'active')
                  """,
                  (
                      recipe_id,
                      max_v,
                      float(request.form.get("batch_size") or 1),
                      request.form.get("output_unit") or "kg",
                  ),
              )
              version_id = vcur.lastrowid
              names = request.form.getlist("component_name")
              qtys = request.form.getlist("component_qty")
              units = request.form.getlist("component_unit")
              costs = request.form.getlist("component_cost")
              pids = request.form.getlist("component_product_id")
              for i, name in enumerate(names):
                  if not name.strip():
                      continue
                  conn.execute(
                      """
                      INSERT INTO recipe_components (
                          recipe_version_id, supplier_product_id, component_name, quantity, unit, unit_cost
                      ) VALUES (?, ?, ?, ?, ?, ?)
                      """,
                      (
                          version_id,
                          int(pids[i]) if i < len(pids) and pids[i] else None,
                          name,
                          float(qtys[i] if i < len(qtys) else 1),
                          units[i] if i < len(units) else "kg",
                          float(costs[i] if i < len(costs) else 0),
                      ),
                  )
              calculate_recipe_cost(conn, version_id)
          flash("Recept en versie opgeslagen, kost berekend.", "success")
          return redirect(url_for("main.recipes_list"))
      with db_conn() as conn:
          products = conn.execute(
              "SELECT id, supplier_product_name, current_price FROM supplier_products ORDER BY supplier_product_name"
          ).fetchall()
      return render_template("recipe_builder.html", products=products)

  @bp.route("/repack/builder", methods=["GET", "POST"])
  def repack_builder():
      if request.method == "POST":
          with db_conn() as conn:
              rcur = conn.execute(
                  """
                  INSERT INTO repack_recipes (
                      name, input_supplier_product_id, input_quantity, input_unit,
                      packaging_cost, label_cost, labor_cost, notes
                  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                  """,
                  (
                      request.form["name"],
                      int(request.form["input_supplier_product_id"]),
                      float(request.form["input_quantity"]),
                      request.form.get("input_unit") or "kg",
                      float(request.form.get("packaging_cost") or 0),
                      float(request.form.get("label_cost") or 0),
                      float(request.form.get("labor_cost") or 0),
                      request.form.get("notes"),
                  ),
              )
              repack_id = rcur.lastrowid
              out_qtys = request.form.getlist("output_quantity")
              out_units = request.form.getlist("output_unit")
              sale_prices = request.form.getlist("suggested_sale_price")
              for i, oq in enumerate(out_qtys):
                  if not oq:
                      continue
                  conn.execute(
                      """
                      INSERT INTO repack_outputs (repack_recipe_id, output_quantity, output_unit, suggested_sale_price)
                      VALUES (?, ?, ?, ?)
                      """,
                      (
                          repack_id,
                          float(oq),
                          out_units[i] if i < len(out_units) else "kg",
                          float(sale_prices[i]) if i < len(sale_prices) and sale_prices[i] else None,
                      ),
                  )
              calculate_repack(conn, repack_id)
          flash("Repack recept opgeslagen en berekend.", "success")
          return redirect(url_for("main.repack_list"))
      with db_conn() as conn:
          products = conn.execute(
              "SELECT id, supplier_product_name, current_price, package_size, package_unit FROM supplier_products ORDER BY supplier_product_name"
          ).fetchall()
      return render_template("repack_builder.html", products=products)

  @bp.route("/reports")
  def reports():
      return render_template("reports.html")

  @bp.route("/reports/export/<report_type>")
  def reports_export(report_type: str):
      fmt = request.args.get("format", "csv")
      with db_conn() as conn:
          if report_type == "purchases":
              csv_data = purchase_history_report(conn)
              headers = csv_data.splitlines()[0].split(",")
              rows = [line.split(",") for line in csv_data.splitlines()[1:]]
          elif report_type == "suppliers":
              csv_data = supplier_history_report(conn)
              headers = csv_data.splitlines()[0].split(",")
              rows = [line.split(",") for line in csv_data.splitlines()[1:]]
          elif report_type == "recipes":
              csv_data = recipe_cost_report(conn)
              headers = csv_data.splitlines()[0].split(",")
              rows = [line.split(",") for line in csv_data.splitlines()[1:]]
          elif report_type == "repack":
              csv_data = repack_history_report(conn)
              headers = csv_data.splitlines()[0].split(",")
              rows = [line.split(",") for line in csv_data.splitlines()[1:]]
          else:
              flash("Onbekend rapport.", "error")
              return redirect(url_for("main.reports"))
      if fmt == "xlsx":
          data = to_excel(report_type, headers, rows)
          return send_file(
              BytesIO(data),
              mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
              as_attachment=True,
              download_name=f"procm-{report_type}.xlsx",
          )
      return send_file(
          BytesIO(csv_data.encode("utf-8")),
          mimetype="text/csv",
          as_attachment=True,
          download_name=f"procm-{report_type}.csv",
      )
