-- procM core schema — MariaDB (Versio nol_module_procM)

CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NULL,
    contact_email VARCHAR(255) NULL,
    contact_phone VARCHAR(64) NULL,
    notes TEXT NULL,
    active TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS supplier_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(128) NULL,
    email VARCHAR(255) NULL,
    phone VARCHAR(64) NULL,
    notes TEXT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS canonical_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NULL,
    category VARCHAR(128) NULL,
    active TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS supplier_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    supplier_sku VARCHAR(128) NULL,
    supplier_product_name VARCHAR(255) NOT NULL,
    canonical_name VARCHAR(255) NULL,
    canonical_product_id INT NULL,
    source_url TEXT NULL,
    package_size DECIMAL(12,3) NULL,
    package_unit VARCHAR(32) NULL,
    current_price DECIMAL(12,2) NULL,
    currency VARCHAR(8) NOT NULL DEFAULT 'EUR',
    image_url TEXT NULL,
    description TEXT NULL,
    active TINYINT NOT NULL DEFAULT 1,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (canonical_product_id) REFERENCES canonical_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS supplier_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_product_id INT NOT NULL,
    effective_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price DECIMAL(12,2) NOT NULL,
    currency VARCHAR(8) NOT NULL DEFAULT 'EUR',
    shipping_cost DECIMAL(12,2) DEFAULT 0,
    source VARCHAR(64) NOT NULL DEFAULT 'manual',
    notes TEXT NULL,
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS price_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_product_id INT NOT NULL,
    recorded_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    unit_price DECIMAL(12,2) NOT NULL,
    effective_unit_cost DECIMAL(12,4) NULL,
    source VARCHAR(64) NOT NULL DEFAULT 'manual',
    notes TEXT NULL,
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS purchase_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS purchase_order_lines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_order_id INT NOT NULL,
    supplier_product_id INT NOT NULL,
    quantity DECIMAL(12,3) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    line_total DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id),
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS purchase_suggestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_product_id INT NOT NULL,
    supplier_id INT NULL,
    suggested_quantity DECIMAL(12,3) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'open',
    priority VARCHAR(16) NOT NULL DEFAULT 'medium',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS supplier_watches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_product_id INT NOT NULL,
    source_url TEXT NULL,
    last_checked_at DATETIME NULL,
    last_price DECIMAL(12,2) NULL,
    previous_price DECIMAL(12,2) NULL,
    change_percent DECIMAL(8,2) NULL,
    active TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_product_id) REFERENCES supplier_products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS settings (
    `key` VARCHAR(128) PRIMARY KEY,
    value TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
