"""Consumption forecasting and reorder planning."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Any


def compute_forecast(conn: sqlite3.Connection, supplier_product_id: int) -> dict[str, Any]:
    profile = conn.execute(
        "SELECT * FROM forecast_profiles WHERE supplier_product_id = ?",
        (supplier_product_id,),
    ).fetchone()
    consumption = conn.execute(
        "SELECT * FROM consumption_profiles WHERE supplier_product_id = ?",
        (supplier_product_id,),
    ).fetchone()
    product = conn.execute(
        """
        SELECT sp.*, s.name AS supplier_name, s.id AS supplier_id
        FROM supplier_products sp JOIN suppliers s ON s.id = sp.supplier_id
        WHERE sp.id = ?
        """,
        (supplier_product_id,),
    ).fetchone()
    if not product:
        raise ValueError("Product not found")

    avg_daily = consumption["avg_daily_consumption"] if consumption else 0
    if avg_daily <= 0:
        events = conn.execute(
            """
            SELECT quantity, event_date FROM consumption_events
            WHERE supplier_product_id = ? AND event_type = 'consumed'
            ORDER BY event_date DESC LIMIT 30
            """,
            (supplier_product_id,),
        ).fetchall()
        if events:
            total = sum(e["quantity"] for e in events)
            avg_daily = total / max(len(events), 1)

    current_qty = profile["current_planning_qty"] if profile else 0
    safety_days = profile["safety_days"] if profile else 7
    lead_time = profile["lead_time_days"] if profile else 7

    days_remaining = (current_qty / avg_daily) if avg_daily > 0 else None
    reorder_in_days = None
    reorder_date = None
    if days_remaining is not None:
        reorder_in_days = max(0, days_remaining - lead_time - safety_days)
        reorder_date = (datetime.now(UTC) + timedelta(days=reorder_in_days)).strftime("%Y-%m-%d")

    return {
        "supplier_product_id": supplier_product_id,
        "product_name": product["supplier_product_name"],
        "supplier_name": product["supplier_name"],
        "current_planning_qty": current_qty,
        "avg_daily_consumption": avg_daily,
        "days_remaining": days_remaining,
        "reorder_in_days": reorder_in_days,
        "reorder_date": reorder_date,
        "safety_days": safety_days,
        "lead_time_days": lead_time,
    }


def record_consumption_event(
    conn: sqlite3.Connection,
    supplier_product_id: int,
    event_type: str,
    quantity: float,
    unit: str = "kg",
    notes: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO consumption_events (supplier_product_id, event_type, quantity, unit, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (supplier_product_id, event_type, quantity, unit, notes),
    )
    if event_type == "consumed":
        events = conn.execute(
            """
            SELECT quantity FROM consumption_events
            WHERE supplier_product_id = ? AND event_type = 'consumed'
            ORDER BY event_date DESC LIMIT 14
            """,
            (supplier_product_id,),
        ).fetchall()
        avg = sum(e["quantity"] for e in events) / max(len(events), 1)
        conn.execute(
            """
            INSERT INTO consumption_profiles (supplier_product_id, avg_daily_consumption, unit, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(supplier_product_id) DO UPDATE SET
                avg_daily_consumption = excluded.avg_daily_consumption,
                unit = excluded.unit,
                updated_at = datetime('now')
            """,
            (supplier_product_id, avg, unit),
        )
    profile = conn.execute(
        "SELECT current_planning_qty FROM forecast_profiles WHERE supplier_product_id = ?",
        (supplier_product_id,),
    ).fetchone()
    qty = profile["current_planning_qty"] if profile else 0
    if event_type == "purchased":
        qty += quantity
    elif event_type == "consumed":
        qty = max(0, qty - quantity)
    elif event_type == "repacked":
        qty = max(0, qty - quantity)
    conn.execute(
        """
        INSERT INTO forecast_profiles (supplier_product_id, current_planning_qty, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(supplier_product_id) DO UPDATE SET
            current_planning_qty = excluded.current_planning_qty,
            updated_at = datetime('now')
        """,
        (supplier_product_id, qty),
    )
