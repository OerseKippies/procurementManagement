"""Seed realistic Oerse Kippies procurement data."""

from __future__ import annotations

import sqlite3

from procm.services.pricing import record_price


def seed_if_empty(conn: sqlite3.Connection) -> bool:
    row = conn.execute("SELECT COUNT(*) AS c FROM suppliers").fetchone()
    if row and row["c"] > 0:
        return False

    suppliers = [
        ("Teurlings de Mulder", "teurlings.nl"),
        ("Plein", "plein.nl"),
        ("Bol", "bol.com"),
        ("Scharrelpluimvee", "scharrelpluimvee.nl"),
        ("Olba", "olba.nl"),
    ]
    supplier_ids: dict[str, int] = {}
    for name, domain in suppliers:
        cur = conn.execute(
            "INSERT INTO suppliers (name, domain) VALUES (?, ?)", (name, domain)
        )
        supplier_ids[name] = cur.lastrowid

    products = [
        ("Scharrelpluimvee", "HAV-SG-KOR-25", "Havens Start & Grow Korrel 25 kg", 25, "kg", 18.95),
        ("Scharrelpluimvee", "HAV-SG-MEEL-25", "Havens Start & Grow Meel 25 kg", 25, "kg", 17.50),
        ("Scharrelpluimvee", "HAV-LEG-20", "Fuite Pluimvee Legkorrel 20 kg", 20, "kg", 16.80),
        ("Scharrelpluimvee", "HAV-GG-25", "Gemengd Graan 25 kg", 25, "kg", 14.20),
        ("Plein", "PLN-MK-FIJN", "Maagkiezel fijn 25 kg", 25, "kg", 12.50),
        ("Plein", "PLN-MK-GROF", "Maagkiezel grof 25 kg", 25, "kg", 12.80),
        ("Plein", "PLN-GRIT-25", "Grit 25 kg", 25, "kg", 11.90),
        ("Teurlings de Mulder", "TEU-WORM-5L", "Meelwormen 5 liter", 5, "liter", 24.00),
        ("Teurlings de Mulder", "TEU-BSF", "BSF larven", 1, "kg", 18.00),
        ("Bol", "BOL-KRAFT", "Kraft zakjes", 100, "stuk", 8.50),
        ("Bol", "BOL-LABEL", "Stickers / etiketten", 500, "stuk", 15.00),
        ("Bol", "BOL-EMM-1L", "1 liter emmertjes", 50, "stuk", 22.00),
        ("Olba", "OLBA-VB-START", "VitalBoost Start basis", 1, "kg", 6.50),
    ]
    product_ids: dict[str, int] = {}
    for supplier, sku, name, size, unit, price in products:
        cur = conn.execute(
            """
            INSERT INTO supplier_products (
                supplier_id, supplier_sku, supplier_product_name, canonical_name,
                package_size, package_unit, current_price, active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (supplier_ids[supplier], sku, name, name, size, unit, price),
        )
        product_ids[name] = cur.lastrowid
        record_price(conn, cur.lastrowid, price, source="seed")

    recipes = [
        ("VitalBoost Start", 10, "kg", [
            ("VitalBoost Start basis", "OLBA-VB-START", 2, "kg", 6.50),
            ("Havens Start & Grow Korrel 25 kg", "HAV-SG-KOR-25", 5, "kg", 0.76),
            ("Meelwormen 5 liter", "TEU-WORM-5L", 1, "liter", 4.80),
        ]),
        ("OK Verwennerij Tamme Kuikenmix", 5, "kg", [
            ("Meelwormen 5 liter", "TEU-WORM-5L", 2, "liter", 4.80),
            ("BSF larven", "TEU-BSF", 0.5, "kg", 18.00),
            ("Gemengd Graan 25 kg", "HAV-GG-25", 2, "kg", 0.57),
        ]),
        ("Wormenmix", 3, "kg", [
            ("Meelwormen 5 liter", "TEU-WORM-5L", 2, "liter", 4.80),
            ("BSF larven", "TEU-BSF", 0.5, "kg", 18.00),
        ]),
        ("Kuikenstartpakket", 1, "set", [
            ("Havens Start & Grow Meel 25 kg", "HAV-SG-MEEL-25", 2, "kg", 0.70),
            ("Maagkiezel fijn 25 kg", "PLN-MK-FIJN", 0.5, "kg", 0.50),
            ("Grit 25 kg", "PLN-GRIT-25", 0.5, "kg", 0.48),
            ("1 liter emmertjes", "BOL-EMM-1L", 1, "stuk", 0.44),
        ]),
    ]
    sku_map: dict[str, int] = {}
    for _supplier, sku, name, _size, _unit, _price in products:
        sku_map[sku] = product_ids[name]

    for recipe_name, batch_size, output_unit, components in recipes:
        rcur = conn.execute("INSERT INTO recipes (name) VALUES (?)", (recipe_name,))
        recipe_id = rcur.lastrowid
        vcur = conn.execute(
            """
            INSERT INTO recipe_versions (recipe_id, version_number, batch_size, output_unit, status)
            VALUES (?, 1, ?, ?, 'active')
            """,
            (recipe_id, batch_size, output_unit),
        )
        version_id = vcur.lastrowid
        for comp_name, sku, qty, unit, unit_cost in components:
            conn.execute(
                """
                INSERT INTO recipe_components (
                    recipe_version_id, supplier_product_id, component_name, quantity, unit, unit_cost
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (version_id, sku_map.get(sku), comp_name, qty, unit, unit_cost),
            )

    repacks = [
        (
            "Start & Grow 25 kg naar 2 kg zakken",
            product_ids["Havens Start & Grow Korrel 25 kg"],
            25,
            "kg",
            2,
            "kg",
            1.20,
            0.15,
            2.50,
            4.50,
        ),
        (
            "Maagkiezel 25 kg naar 500 g zakken",
            product_ids["Maagkiezel fijn 25 kg"],
            25,
            "kg",
            0.5,
            "kg",
            0.80,
            0.10,
            3.00,
            3.20,
        ),
    ]
    for name, inp_id, in_qty, in_unit, out_qty, out_unit, pack, label, labor, sale in repacks:
        rcur = conn.execute(
            """
            INSERT INTO repack_recipes (
                name, input_supplier_product_id, input_quantity, input_unit,
                packaging_cost, label_cost, labor_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, inp_id, in_qty, in_unit, pack, label, labor),
        )
        repack_id = rcur.lastrowid
        conn.execute(
            """
            INSERT INTO repack_outputs (repack_recipe_id, output_quantity, output_unit, suggested_sale_price)
            VALUES (?, ?, ?, ?)
            """,
            (repack_id, out_qty, out_unit, sale),
        )

    conn.execute(
        "INSERT INTO settings (key, value) VALUES ('default_margin_percent', '30')"
    )
    conn.execute(
        "INSERT INTO settings (key, value) VALUES ('seed_version', '2-business')"
    )
    seed_business_extensions(conn)
    return True


def seed_business_extensions(conn: sqlite3.Connection) -> bool:
    """Canonical products, watches, forecasts — runs once per database."""
    row = conn.execute(
        "SELECT value FROM settings WHERE key = 'business_seed'"
    ).fetchone()
    if row:
        return False

    canonical = [
        ("Havens Start & Grow", "Kuikenvoer start/grow", "feed"),
        ("Legkorrel", "Legkorrel leghennen", "feed"),
        ("Gemengd Graan", "Graanmix", "feed"),
        ("Maagkiezel", "Maagkiezel fijn/grof", "supplement"),
        ("Meelwormen", "Gedroogde meelwormen", "treat"),
    ]
    canon_ids: dict[str, int] = {}
    for name, desc, cat in canonical:
        cur = conn.execute(
            "INSERT OR IGNORE INTO canonical_products (name, description, category) VALUES (?, ?, ?)",
            (name, desc, cat),
        )
        if cur.lastrowid:
            canon_ids[name] = cur.lastrowid
        else:
            rid = conn.execute(
                "SELECT id FROM canonical_products WHERE name = ?", (name,)
            ).fetchone()
            canon_ids[name] = rid["id"]

    links = [
        ("Havens Start & Grow Korrel 25 kg", "Havens Start & Grow"),
        ("Havens Start & Grow Meel 25 kg", "Havens Start & Grow"),
        ("Fuite Pluimvee Legkorrel 20 kg", "Legkorrel"),
        ("Gemengd Graan 25 kg", "Gemengd Graan"),
        ("Maagkiezel fijn 25 kg", "Maagkiezel"),
        ("Meelwormen 5 liter", "Meelwormen"),
    ]
    for prod_name, canon_name in links:
        if canon_name in canon_ids:
            conn.execute(
                """
                UPDATE supplier_products SET canonical_product_id = ?, canonical_name = ?
                WHERE supplier_product_name = ?
                """,
                (canon_ids[canon_name], canon_name, prod_name),
            )

    feed_id = conn.execute(
        "SELECT id FROM supplier_products WHERE supplier_product_name LIKE 'Havens Start%Korrel%' LIMIT 1"
    ).fetchone()
    if feed_id:
        conn.execute(
            """
            INSERT INTO supplier_watches (supplier_product_id, last_price, active)
            SELECT id, current_price, 1 FROM supplier_products WHERE id = ?
            """,
            (feed_id["id"],),
        )
        conn.execute(
            """
            INSERT INTO forecast_profiles (supplier_product_id, current_planning_qty, safety_days, lead_time_days)
            VALUES (?, 8, 7, 5)
            """,
            (feed_id["id"],),
        )
        conn.execute(
            """
            INSERT INTO consumption_profiles (supplier_product_id, avg_daily_consumption, unit)
            VALUES (?, 1.5, 'kg')
            """,
            (feed_id["id"],),
        )
        conn.execute(
            """
            INSERT INTO price_alerts (supplier_product_id, alert_type, threshold_price, status)
            VALUES (?, 'maximum', 20.00, 'active')
            """,
            (feed_id["id"],),
        )

    extra_repack = conn.execute(
        "SELECT id FROM supplier_products WHERE supplier_product_name = 'Havens Start & Grow Korrel 25 kg'"
    ).fetchone()
    if extra_repack and not conn.execute(
        "SELECT id FROM repack_recipes WHERE name LIKE '%1 kg%'"
    ).fetchone():
        rcur = conn.execute(
            """
            INSERT INTO repack_recipes (
                name, input_supplier_product_id, input_quantity, input_unit, packaging_cost, label_cost, labor_cost
            ) VALUES ('Start & Grow 25 kg naar 1 kg zakken', ?, 25, 'kg', 0.90, 0.12, 2.00)
            """,
            (extra_repack["id"],),
        )
        conn.execute(
            "INSERT INTO repack_outputs (repack_recipe_id, output_quantity, output_unit, suggested_sale_price) VALUES (?, 1, 'kg', 3.25)",
            (rcur.lastrowid,),
        )

    conn.execute(
        "INSERT INTO settings (key, value) VALUES ('business_seed', '1')"
    )
    return True
