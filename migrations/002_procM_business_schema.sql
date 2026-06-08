-- procM business extension — purchasing completion, URL intake, costing, recipes

CREATE TABLE IF NOT EXISTS supplier_product_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_product_id INT NOT NULL,
    image_url TEXT NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS import_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_url TEXT NOT NULL,
    supplier_id INT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    error_message TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS imported_pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    import_job_id INT NOT NULL,
    raw_title TEXT NULL,
    raw_html_hash VARCHAR(64) NULL,
    parser_version VARCHAR(32) NOT NULL DEFAULT 'mvp-1',
    FOREIGN KEY (import_job_id) REFERENCES import_jobs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS supplier_product_imports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    import_job_id INT NOT NULL,
    supplier_product_id INT NULL,
    outcome VARCHAR(32) NULL,
    FOREIGN KEY (import_job_id) REFERENCES import_jobs(id),
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS supplier_product_snapshots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    import_job_id INT NULL,
    supplier_product_id INT NULL,
    captured_json TEXT NOT NULL,
    captured_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (import_job_id) REFERENCES import_jobs(id),
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS purchase_receipts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    purchase_order_id INT NULL,
    received_date DATE NOT NULL,
    notes TEXT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS purchase_receipt_lines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_receipt_id INT NOT NULL,
    supplier_product_id INT NOT NULL,
    quantity DECIMAL(12,3) NOT NULL,
    FOREIGN KEY (purchase_receipt_id) REFERENCES purchase_receipts(id),
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS purchase_invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    purchase_order_id INT NULL,
    invoice_number VARCHAR(64) NOT NULL,
    invoice_date DATE NOT NULL,
    invoice_total DECIMAL(12,2) NOT NULL DEFAULT 0,
    notes TEXT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS purchase_invoice_lines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_invoice_id INT NOT NULL,
    supplier_product_id INT NOT NULL,
    quantity DECIMAL(12,3) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    line_total DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (purchase_invoice_id) REFERENCES purchase_invoices(id),
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cost_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    model_type VARCHAR(64) NOT NULL DEFAULT 'generic',
    active TINYINT NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cost_calculations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cost_model_id INT NULL,
    target_type VARCHAR(64) NULL,
    target_id INT NULL,
    total_cost DECIMAL(12,4) NOT NULL,
    unit_cost DECIMAL(12,4) NULL,
    suggested_sale_price DECIMAL(12,4) NULL,
    margin_euro DECIMAL(12,4) NULL,
    margin_percent DECIMAL(8,2) NULL,
    price_basis_date DATE NULL,
    calculated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT NULL,
    FOREIGN KEY (cost_model_id) REFERENCES cost_models(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cost_components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cost_calculation_id INT NOT NULL,
    component_type VARCHAR(64) NOT NULL,
    amount DECIMAL(12,4) NOT NULL,
    quantity_basis VARCHAR(64) NULL,
    source_reference VARCHAR(255) NULL,
    FOREIGN KEY (cost_calculation_id) REFERENCES cost_calculations(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    active TINYINT NOT NULL DEFAULT 1,
    notes TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS recipe_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    version_number INT NOT NULL DEFAULT 1,
    batch_size DECIMAL(12,3) NOT NULL DEFAULT 1,
    output_unit VARCHAR(32) NOT NULL DEFAULT 'unit',
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    effective_from DATE NOT NULL DEFAULT (CURRENT_DATE),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS recipe_components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_version_id INT NOT NULL,
    supplier_product_id INT NULL,
    component_name VARCHAR(255) NOT NULL,
    quantity DECIMAL(12,3) NOT NULL,
    unit VARCHAR(32) NOT NULL DEFAULT 'kg',
    unit_cost DECIMAL(12,4) NOT NULL DEFAULT 0,
    FOREIGN KEY (recipe_version_id) REFERENCES recipe_versions(id),
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS recipe_costs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_version_id INT NOT NULL,
    cost_calculation_id INT NULL,
    batch_cost DECIMAL(12,4) NOT NULL,
    unit_cost DECIMAL(12,4) NOT NULL,
    calculated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_version_id) REFERENCES recipe_versions(id),
    FOREIGN KEY (cost_calculation_id) REFERENCES cost_calculations(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS repack_recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    input_supplier_product_id INT NULL,
    input_quantity DECIMAL(12,3) NOT NULL,
    input_unit VARCHAR(32) NOT NULL DEFAULT 'kg',
    packaging_cost DECIMAL(12,4) NOT NULL DEFAULT 0,
    label_cost DECIMAL(12,4) NOT NULL DEFAULT 0,
    labor_cost DECIMAL(12,4) NOT NULL DEFAULT 0,
    notes TEXT NULL,
    FOREIGN KEY (input_supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS repack_outputs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    repack_recipe_id INT NOT NULL,
    output_quantity DECIMAL(12,3) NOT NULL,
    output_unit VARCHAR(32) NOT NULL DEFAULT 'kg',
    suggested_sale_price DECIMAL(12,4) NULL,
    FOREIGN KEY (repack_recipe_id) REFERENCES repack_recipes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS repack_costs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    repack_recipe_id INT NOT NULL,
    cost_calculation_id INT NULL,
    output_units DECIMAL(12,3) NOT NULL,
    cost_per_output_unit DECIMAL(12,4) NOT NULL,
    waste_remainder DECIMAL(12,4) NOT NULL DEFAULT 0,
    calculated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repack_recipe_id) REFERENCES repack_recipes(id),
    FOREIGN KEY (cost_calculation_id) REFERENCES cost_calculations(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO settings (`key`, value) VALUES ('schema_version', '2-business');
INSERT IGNORE INTO settings (`key`, value) VALUES ('procurement_mvp_status', 'PROCUREMENT MVP COMPLETE');
