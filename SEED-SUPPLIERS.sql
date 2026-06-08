-- procM production seed — suppliers (post-go-live)
-- Target: MariaDB nol_module_procM
-- Idempotent: skips rows when supplier name already exists

INSERT INTO suppliers (name, domain, notes, active)
SELECT 'Teurlings de Mulder', 'teurlings.nl', 'Poultry feed, treats, and supplements — primary feed supplier', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE name = 'Teurlings de Mulder');

INSERT INTO suppliers (name, domain, notes, active)
SELECT 'Plein', 'plein.nl', 'Maagkiezel, grit, and mineral supplements', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE name = 'Plein');

INSERT INTO suppliers (name, domain, notes, active)
SELECT 'Bol', 'bol.com', 'Packaging materials — kraft bags, stickers, buckets', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE name = 'Bol');

INSERT INTO suppliers (name, domain, notes, active)
SELECT 'Olba', 'olba.nl', 'Vitamin and mineral premixes for poultry', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE name = 'Olba');
