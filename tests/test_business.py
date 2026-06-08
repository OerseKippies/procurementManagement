"""Business edition tests."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from procm import create_app
from procm.db import get_connection, init_db
from procm.migrations import run_migrations
from procm.seed import seed_business_extensions, seed_if_empty
from procm.services.forecast import compute_forecast, record_consumption_event
from procm.services.invoice_import import import_csv
from procm.services.monitoring import refresh_watch
from procm.services.reports import purchase_history_report, supplier_history_report


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "business.sqlite3"
    init_db(path)
    conn = get_connection(path)
    try:
        seed_if_empty(conn)
        seed_business_extensions(conn)
        conn.commit()
    finally:
        conn.close()
    return path


@pytest.fixture
def client(db_path: Path):
    return create_app({"TESTING": True, "DATABASE_PATH": str(db_path)}).test_client()


def test_migrations_add_business_tables(db_path: Path):
    conn = get_connection(db_path)
    try:
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        for name in (
            "canonical_products",
            "supplier_watches",
            "price_alerts",
            "consumption_events",
            "forecast_profiles",
            "invoice_imports",
        ):
            assert name in tables
    finally:
        conn.close()


def test_canonical_products_seeded(db_path: Path):
    conn = get_connection(db_path)
    try:
        count = conn.execute("SELECT COUNT(*) c FROM canonical_products").fetchone()["c"]
        assert count >= 3
        linked = conn.execute(
            "SELECT COUNT(*) c FROM supplier_products WHERE canonical_product_id IS NOT NULL"
        ).fetchone()["c"]
        assert linked >= 1
    finally:
        conn.close()


def test_forecasting(client, db_path: Path):
    conn = get_connection(db_path)
    try:
        pid = conn.execute("SELECT id FROM supplier_products LIMIT 1").fetchone()["id"]
        record_consumption_event(conn, pid, "consumed", 2, "kg")
        conn.commit()
        result = compute_forecast(conn, pid)
        assert "avg_daily_consumption" in result
    finally:
        conn.close()
    rv = client.get("/forecasts?product_id=1")
    assert rv.status_code == 200
    assert b"Forecast" in rv.data


def test_monitoring_page(client):
    rv = client.get("/monitoring")
    assert rv.status_code == 200
    assert b"Watchlist" in rv.data


def test_invoice_csv_import(db_path: Path):
    conn = get_connection(db_path)
    try:
        csv_text = "sku,quantity,unit_price\nHAV-SG-KOR-25,2,19.50\n"
        result = import_csv(conn, csv_text, supplier_id=1, filename="test.csv")
        conn.commit()
        assert result["line_count"] == 1
        assert result["invoice_total"] > 0
    finally:
        conn.close()


def test_reports_export(client):
    rv = client.get("/reports/export/purchases?format=csv")
    assert rv.status_code == 200
    assert b"order_id" in rv.data or b"supplier" in rv.data


def test_reports_page(client):
    assert client.get("/reports").status_code == 200


def test_purchasing_hub(client):
    assert client.get("/purchasing").status_code == 200


def test_canonical_page(client):
    assert client.get("/canonical").status_code == 200


def test_consumption_page(client):
    rv = client.post(
        "/consumption",
        data={"supplier_product_id": "1", "event_type": "consumed", "quantity": "1"},
        follow_redirects=True,
    )
    assert rv.status_code == 200


def test_recipe_builder_page(client):
    assert client.get("/recipes/builder").status_code == 200


def test_invoice_import_page(client):
    assert client.get("/invoices/import").status_code == 200


def test_purchase_history_report(db_path: Path):
    conn = get_connection(db_path)
    try:
        csv_out = purchase_history_report(conn)
        assert "supplier" in csv_out or "order_id" in csv_out
        assert supplier_history_report(conn)
    finally:
        conn.close()


def test_health_business_edition(client):
    rv = client.get("/health")
    assert rv.get_json().get("edition") == "business"


def test_monitoring_add_watch(client):
    rv = client.post(
        "/monitoring",
        data={"action": "add_watch", "supplier_product_id": "2"},
        follow_redirects=True,
    )
    assert rv.status_code == 200


def test_canonical_create_and_link(client):
    rv = client.post(
        "/canonical",
        data={"action": "create", "name": "Test Canon", "category": "feed"},
        follow_redirects=True,
    )
    assert b"Test Canon" in rv.data or rv.status_code == 200


def test_forecast_suggestion_post(client, db_path: Path):
    pid = get_connection(db_path).execute("SELECT id FROM supplier_products LIMIT 1").fetchone()["id"]
    rv = client.post(
        "/forecasts",
        data={
            "action": "suggest",
            "supplier_product_id": str(pid),
            "current_planning_qty": "2",
            "safety_days": "7",
            "lead_time_days": "5",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200


def test_recipe_builder_create(client):
    rv = client.post(
        "/recipes/builder",
        data={
            "name": "Test Recipe Biz",
            "batch_size": "5",
            "output_unit": "kg",
            "component_name": "Grain",
            "component_qty": "2",
            "component_unit": "kg",
            "component_cost": "1.5",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Test Recipe Biz" in rv.data


def test_repack_builder_create(client):
    rv = client.post(
        "/repack/builder",
        data={
            "name": "Test Repack 500g",
            "input_supplier_product_id": "1",
            "input_quantity": "25",
            "output_quantity": "0.5",
            "output_unit": "kg",
            "packaging_cost": "0.5",
            "label_cost": "0.1",
            "labor_cost": "1",
            "suggested_sale_price": "2.99",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200


def test_reports_xlsx_export(client):
    rv = client.get("/reports/export/suppliers?format=xlsx")
    assert rv.status_code == 200
    assert "spreadsheet" in rv.content_type


def test_intake_parse_html():
    from procm.intake import parse_product_page

    html = """
    <html><head><title>Start Grow 20kg</title>
    <meta property="og:title" content="Havens Start &amp; Grow 20 kg"/>
    <meta property="og:description" content="Kuikenvoer"/>
    <meta property="og:image" content="https://example.com/img.jpg"/>
  </head><body>€ 18,95 per zak 20 kg</body></html>
    """
    parsed = parse_product_page("https://www.teurlings.nl/product/start-grow", html)
    assert parsed["price"] == 18.95
    assert "Start" in parsed["product_name"]


def test_monitoring_refresh(db_path: Path):
    conn = get_connection(db_path)
    try:
        wid = conn.execute("SELECT id FROM supplier_watches LIMIT 1").fetchone()
        if wid:
            refresh_watch(conn, wid["id"])
            conn.commit()
    finally:
        conn.close()


def test_additional_pages(client):
    for path in (
        "/price-history?product_id=1",
        "/url-intake",
        "/cost-calculator",
        "/suggestions",
        "/recipes",
        "/repack",
        "/purchase-orders",
        "/receipts",
        "/invoices",
        "/settings",
    ):
        assert client.get(path).status_code == 200


def test_cost_calculator_post(client):
    rv = client.post(
        "/cost-calculator",
        data={"amount_raw_material": "10", "units": "5", "margin_percent": "25"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Totaal" in rv.data or b"10" in rv.data


def test_enhanced_suggestion(db_path: Path):
    from procm.services.suggestions import generate_suggestion_enhanced

    conn = get_connection(db_path)
    try:
        pid = conn.execute("SELECT id FROM supplier_products LIMIT 1").fetchone()["id"]
        result = generate_suggestion_enhanced(conn, pid)
        conn.commit()
        assert "suggestion_id" in result
    finally:
        conn.close()
