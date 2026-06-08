-- procM production seed — supplier products (post-go-live)
-- Run SEED-SUPPLIERS.sql first
-- Idempotent: skips when supplier_sku already exists for supplier

-- Feed (Teurlings de Mulder)
INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'TEU-HAV-SG-KOR-25', 'Havens Start & Grow Korrel 25kg', 'Havens Start & Grow',
       25, 'kg', 18.95, 'EUR', 1, 'Kuikenvoer korrel — bulk 25 kg'
FROM suppliers s
WHERE s.name = 'Teurlings de Mulder'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'TEU-HAV-SG-KOR-25'
  );

INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'TEU-HAV-SG-MEEL-25', 'Havens Start & Grow Meel 25kg', 'Havens Start & Grow',
       25, 'kg', 17.50, 'EUR', 1, 'Kuikenvoer meel — bulk 25 kg'
FROM suppliers s
WHERE s.name = 'Teurlings de Mulder'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'TEU-HAV-SG-MEEL-25'
  );

INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'TEU-HAV-LEG-20', 'Fuite Legkorrel 20kg', 'Legkorrel',
       20, 'kg', 16.80, 'EUR', 1, 'Legkorrel leghennen — 20 kg'
FROM suppliers s
WHERE s.name = 'Teurlings de Mulder'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'TEU-HAV-LEG-20'
  );

INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'TEU-HAV-GG-25', 'Gemengd Graan 25kg', 'Gemengd Graan',
       25, 'kg', 14.20, 'EUR', 1, 'Graanmix — bulk 25 kg'
FROM suppliers s
WHERE s.name = 'Teurlings de Mulder'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'TEU-HAV-GG-25'
  );

-- Supplements (Plein)
INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'PLN-MK-FIJN-25', 'Maagkiezel Fijn 25kg', 'Maagkiezel',
       25, 'kg', 12.50, 'EUR', 1, 'Fijne maagkiezel — bulk 25 kg'
FROM suppliers s
WHERE s.name = 'Plein'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'PLN-MK-FIJN-25'
  );

INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'PLN-MK-GROF-25', 'Maagkiezel Grof 25kg', 'Maagkiezel',
       25, 'kg', 12.80, 'EUR', 1, 'Grove maagkiezel — bulk 25 kg'
FROM suppliers s
WHERE s.name = 'Plein'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'PLN-MK-GROF-25'
  );

INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'PLN-GRIT-25', 'Grit 25kg', 'Grit',
       25, 'kg', 11.90, 'EUR', 1, 'Grit — bulk 25 kg'
FROM suppliers s
WHERE s.name = 'Plein'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'PLN-GRIT-25'
  );

-- Supplements (Teurlings de Mulder)
INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'TEU-WORM-5L', 'Meelwormen', 'Meelwormen',
       5, 'liter', 24.00, 'EUR', 1, 'Gedroogde meelwormen — 5 liter emmer'
FROM suppliers s
WHERE s.name = 'Teurlings de Mulder'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'TEU-WORM-5L'
  );

INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'TEU-BSF-1KG', 'BSF Larven', 'BSF Larven',
       1, 'kg', 18.00, 'EUR', 1, 'Black soldier fly larven — 1 kg'
FROM suppliers s
WHERE s.name = 'Teurlings de Mulder'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'TEU-BSF-1KG'
  );

-- Packaging (Bol)
INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'BOL-KRAFT-100', 'Kraft Zakjes', 'Kraft Zakjes',
       100, 'stuk', 8.50, 'EUR', 1, 'Kraft papieren zakjes — per 100'
FROM suppliers s
WHERE s.name = 'Bol'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'BOL-KRAFT-100'
  );

INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'BOL-STICKER-500', 'Stickers', 'Stickers',
       500, 'stuk', 15.00, 'EUR', 1, 'Productstickers / etiketten — per 500'
FROM suppliers s
WHERE s.name = 'Bol'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'BOL-STICKER-500'
  );

INSERT INTO supplier_products (
    supplier_id, supplier_sku, supplier_product_name, canonical_name,
    package_size, package_unit, current_price, currency, active, notes
)
SELECT s.id, 'BOL-EMMER-50', 'Emmers', 'Emmers',
       50, 'stuk', 22.00, 'EUR', 1, '1 liter emmertjes — per 50'
FROM suppliers s
WHERE s.name = 'Bol'
  AND NOT EXISTS (
      SELECT 1 FROM supplier_products sp
      WHERE sp.supplier_id = s.id AND sp.supplier_sku = 'BOL-EMMER-50'
  );

-- Price history for seeded products (initial record)
INSERT INTO price_history (supplier_product_id, unit_price, effective_unit_cost, source, notes)
SELECT sp.id, sp.current_price,
       CASE WHEN sp.package_size > 0 THEN sp.current_price / sp.package_size ELSE sp.current_price END,
       'seed', 'Initial seed price'
FROM supplier_products sp
WHERE sp.supplier_sku IN (
    'TEU-HAV-SG-KOR-25', 'TEU-HAV-SG-MEEL-25', 'TEU-HAV-LEG-20', 'TEU-HAV-GG-25',
    'PLN-MK-FIJN-25', 'PLN-MK-GROF-25', 'PLN-GRIT-25',
    'TEU-WORM-5L', 'TEU-BSF-1KG',
    'BOL-KRAFT-100', 'BOL-STICKER-500', 'BOL-EMMER-50'
)
AND NOT EXISTS (
    SELECT 1 FROM price_history ph
    WHERE ph.supplier_product_id = sp.id AND ph.source = 'seed'
);
