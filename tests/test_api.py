"""procM consumption API tests for Co-Pilot integration."""

from __future__ import annotations

from pathlib import Path

import pytest

from procm import create_app
from procm.db import get_connection, init_db
from procm.intake import run_url_intake
from procm.seed import seed_if_empty
from procm.services.repack import calculate_repack


@pytest.fixture
def client(tmp_path: Path):
    path = tmp_path / "api_test.sqlite3"
    init_db(path)
    conn = get_connection(path)
    try:
        seed_if_empty(conn)
        conn.commit()
    finally:
        conn.close()
    app = create_app({"TESTING": True, "DATABASE_PATH": str(path)})
    return app.test_client()


def test_api_suppliers(client):
    rv = client.get("/api/suppliers")
    assert rv.status_code == 200
    body = rv.get_json()
    assert body["count"] >= 4
    names = {s["name"] for s in body["data"]}
    assert "Teurlings de Mulder" in names
    assert "Plein" in names


def test_api_supplier_products(client):
    rv = client.get("/api/supplier-products")
    assert rv.status_code == 200
    assert rv.get_json()["count"] >= 10


def test_api_copilot_dashboard(client):
    rv = client.get("/api/copilot/dashboard")
    assert rv.status_code == 200
    body = rv.get_json()
    assert body["contract"] == "procM.copilot.dashboard.v1"
    assert body["suppliers_count"] >= 4
    assert body["supplier_products_count"] >= 10
    assert "recent_purchases" in body


def test_api_recipes_and_costs(client):
    rv = client.get("/api/recipes")
    assert rv.status_code == 200
    assert rv.get_json()["count"] >= 1
    rv = client.get("/api/cost-calculations")
    assert rv.status_code == 200


def test_url_intake_api_flow(client, tmp_path: Path):
    path = Path(client.application.config.get("DATABASE_PATH", tmp_path / "x.sqlite3"))
    conn = get_connection(path)
    try:
        result = run_url_intake(conn, "https://www.teurlings.nl/product/meelwormen")
        conn.commit()
        assert result["import_job_id"] > 0
        job = conn.execute(
            "SELECT status FROM import_jobs WHERE id = ?", (result["import_job_id"],)
        ).fetchone()
        assert job is not None
        snap = conn.execute(
            "SELECT captured_json FROM supplier_product_snapshots WHERE import_job_id = ?",
            (result["import_job_id"],),
        ).fetchone()
        assert snap is not None
    finally:
        conn.close()


def test_repack_cost_engine_examples(client, tmp_path: Path):
    path = Path(client.application.config.get("DATABASE_PATH", tmp_path / "x.sqlite3"))
    conn = get_connection(path)
    try:
        repacks = conn.execute(
            "SELECT id, name FROM repack_recipes WHERE name LIKE '%Maagkiezel%' OR name LIKE '%Start%Grow%'"
        ).fetchall()
        assert len(repacks) >= 2
        for repack in repacks:
            result = calculate_repack(conn, repack["id"])
            assert result["cost_per_output_unit"] > 0
            assert result["suggested_sale_price"] is not None
        conn.commit()
    finally:
        conn.close()
