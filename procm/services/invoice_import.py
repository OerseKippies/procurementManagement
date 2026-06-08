"""CSV and Excel invoice import."""

from __future__ import annotations

import csv
import io
import sqlite3
from typing import Any

from procm.services.pricing import record_price

try:
    import openpyxl
except ImportError:  # pragma: no cover
    openpyxl = None


def _resolve_product(conn: sqlite3.Connection, supplier_id: int | None, token: str) -> int | None:
    token = token.strip()
    if token.isdigit():
        row = conn.execute(
            "SELECT id FROM supplier_products WHERE id = ?", (int(token),)
        ).fetchone()
        return row["id"] if row else None
    row = conn.execute(
        """
        SELECT id FROM supplier_products
        WHERE supplier_sku = ? OR supplier_product_name LIKE ?
        ORDER BY id LIMIT 1
        """,
        (token, f"%{token}%"),
    ).fetchone()
    return row["id"] if row else None


def import_csv(
    conn: sqlite3.Connection,
    content: str,
    *,
    supplier_id: int | None = None,
    filename: str | None = None,
) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(content))
    cur = conn.execute(
        """
        INSERT INTO invoice_imports (supplier_id, source_type, source_filename)
        VALUES (?, 'csv', ?)
        """,
        (supplier_id, filename),
    )
    import_id = cur.lastrowid
    lines = 0
    invoice_total = 0.0
    for row in reader:
        ref = row.get("supplier_product_id") or row.get("sku") or row.get("product") or ""
        qty = float(row.get("quantity") or row.get("qty") or 0)
        price = float(row.get("unit_price") or row.get("price") or 0)
        total = float(row.get("line_total") or row.get("total") or qty * price)
        pid = _resolve_product(conn, supplier_id, str(ref)) if ref else None
        conn.execute(
            """
            INSERT INTO invoice_import_lines (
                invoice_import_id, supplier_product_id, line_description, quantity, unit_price, line_total
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (import_id, pid, row.get("description") or ref, qty, price, total),
        )
        if pid and price > 0:
            record_price(conn, pid, price, source="invoice_import")
        lines += 1
        invoice_total += total
    conn.execute(
        "UPDATE invoice_imports SET line_count = ? WHERE id = ?", (lines, import_id)
    )
    if supplier_id and lines > 0:
        conn.execute(
            """
            INSERT INTO purchase_invoices (supplier_id, invoice_number, invoice_total, import_id, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                supplier_id,
                f"IMPORT-{import_id}",
                invoice_total,
                import_id,
                f"Imported from {filename or 'csv'}",
            ),
        )
    return {"import_id": import_id, "line_count": lines, "invoice_total": invoice_total}


def import_excel(
    conn: sqlite3.Connection,
    data: bytes,
    *,
    supplier_id: int | None = None,
    filename: str | None = None,
) -> dict[str, Any]:
    if openpyxl is None:
        raise RuntimeError("openpyxl not installed")
    wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return {"import_id": 0, "line_count": 0, "invoice_total": 0}
    headers = [str(h or "").strip().lower() for h in rows[0]]
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for row in rows[1:]:
        writer.writerow([str(c or "") for c in row])
    return import_csv(conn, buf.getvalue(), supplier_id=supplier_id, filename=filename)
