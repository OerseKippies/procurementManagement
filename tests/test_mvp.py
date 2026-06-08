"""procM MVP smoke and integration tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from procm import create_app
from procm.db import get_connection, init_db
from procm.intake import parse_product_page, run_url_intake
from procm.seed import seed_if_empty
from procm.services.cost_engine import calculate_cost
from procm.services.pricing import price_summary, record_price
from procm.services.recipe import calculate_recipe_cost
from procm.services.repack import calculate_repack
from procm.services.suggestions import generate_suggestion


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.sqlite3"
    init_db(path)
    conn = get_connection(path)
    try:
        seed_if_empty(conn)
        conn.commit()
    finally:
        conn.close()
    return path


@pytest.fixture
def client(db_path: Path):
    app = create_app({"TESTING": True, "DATABASE_PATH": str(db_path)})
    return app.test_client()


def test_app_starts(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.get_json()["status"] == "ok"


def test_database_initializes(db_path: Path):
    conn = get_connection(db_path)
    try:
        count = conn.execute("SELECT COUNT(*) c FROM suppliers").fetchone()["c"]
        assert count >= 5
    finally:
        conn.close()


def test_dashboard_loads(client):
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"Dashboard" in rv.data


def test_suppliers_crud(client):
    rv = client.post(
        "/suppliers",
        data={"name": "Test Supplier", "domain": "test.nl", "contact_email": "a@test.nl"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Test Supplier" in rv.data


def test_supplier_products_crud(client):
    rv = client.post(
        "/products",
        data={
            "supplier_id": "1",
            "supplier_product_name": "Test Product MVP",
            "current_price": "9.99",
            "package_size": "10",
            "package_unit": "kg",
            "active": "on",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Test Product MVP" in rv.data


def test_url_intake_fallback(db_path: Path):
    conn = get_connection(db_path)
    try:
        result = run_url_intake(conn, "https://www.bol.com/nl/nl/p/test-product/123/")
        conn.commit()
        assert result["import_job_id"] > 0
        assert result["supplier_product_id"] > 0
        assert result["status"] in ("COMPLETED", "MANUAL_REQUIRED")
    finally:
        conn.close()


def test_parse_product_page_without_html():
    parsed = parse_product_page("https://teurlings.nl/product/start-grow-20kg", None)
    assert parsed["supplier_name"] == "Teurlings de Mulder"
    assert "Start" in parsed["product_name"] or "start" in parsed["product_name"].lower()


def test_price_history_created(db_path: Path):
    conn = get_connection(db_path)
    try:
        pid = conn.execute("SELECT id FROM supplier_products LIMIT 1").fetchone()["id"]
        record_price(conn, pid, 19.99, source="test")
        conn.commit()
        summary = price_summary(conn, pid)
        assert summary["current"] == 19.99
        count = conn.execute(
            "SELECT COUNT(*) c FROM price_history WHERE supplier_product_id=?", (pid,)
        ).fetchone()["c"]
        assert count >= 2
    finally:
        conn.close()


def test_purchase_order_created(client):
    rv = client.post(
        "/purchase-orders",
        data={
            "supplier_id": "1",
            "supplier_product_id": "1",
            "quantity": "4",
            "unit_price": "18.95",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Inkooporder" in rv.data or b"draft" in rv.data


def test_cost_calculation_works(db_path: Path):
    conn = get_connection(db_path)
    try:
        result = calculate_cost(
            conn,
            [
                {"component_type": "raw_material", "amount": 10},
                {"component_type": "packaging", "amount": 2},
            ],
            units=5,
            target_margin_percent=30,
        )
        conn.commit()
        assert result["total_cost"] == 12
        assert result["unit_cost"] == pytest.approx(2.4)
    finally:
        conn.close()


def test_recipe_cost_works(db_path: Path):
    conn = get_connection(db_path)
    try:
        vid = conn.execute(
            "SELECT id FROM recipe_versions LIMIT 1"
        ).fetchone()["id"]
        result = calculate_recipe_cost(conn, vid)
        conn.commit()
        assert result["batch_cost"] > 0
        assert result["unit_cost"] > 0
    finally:
        conn.close()


def test_repack_calculation_works(db_path: Path):
    conn = get_connection(db_path)
    try:
        rid = conn.execute("SELECT id FROM repack_recipes LIMIT 1").fetchone()["id"]
        result = calculate_repack(conn, rid)
        conn.commit()
        assert result["output_units"] >= 1
        assert result["cost_per_output_unit"] > 0
    finally:
        conn.close()


def test_purchase_suggestion_works(db_path: Path):
    conn = get_connection(db_path)
    try:
        pid = conn.execute("SELECT id FROM supplier_products LIMIT 1").fetchone()["id"]
        result = generate_suggestion(
            conn,
            pid,
            current_quantity=1,
            minimum_desired=4,
            usage_per_week=2,
        )
        conn.commit()
        assert "suggestion_id" in result
        assert result["suggested_quantity"] >= 0
    finally:
        conn.close()
