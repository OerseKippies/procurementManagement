<?php

declare(strict_types=1);

function procm_table_exists(PDO $pdo, string $table): bool
{
    $stmt = $pdo->prepare(
        'SELECT COUNT(*) AS c FROM information_schema.tables
         WHERE table_schema = DATABASE() AND table_name = ?'
    );
    $stmt->execute([$table]);

    return (int) $stmt->fetchColumn() > 0;
}

function procm_api_suppliers(PDO $pdo): array
{
    $active = isset($_GET['active']) ? (int) $_GET['active'] : null;
    $sql = 'SELECT id, name, domain, contact_email, contact_phone, notes, active, created_at
            FROM suppliers';
    $params = [];
    if ($active !== null) {
        $sql .= ' WHERE active = ?';
        $params[] = $active;
    }
    $sql .= ' ORDER BY name';
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);

    return ['data' => $stmt->fetchAll(), 'count' => $stmt->rowCount()];
}

function procm_api_supplier_products(PDO $pdo): array
{
    $supplierId = isset($_GET['supplier_id']) ? (int) $_GET['supplier_id'] : null;
    $active = isset($_GET['active']) ? (int) $_GET['active'] : null;
    $sql = 'SELECT sp.id, sp.supplier_id, s.name AS supplier_name,
                   sp.supplier_sku, sp.supplier_product_name, sp.canonical_name,
                   sp.source_url, sp.package_size, sp.package_unit,
                   sp.current_price, sp.currency, sp.active, sp.notes,
                   sp.created_at, sp.updated_at
            FROM supplier_products sp
            JOIN suppliers s ON s.id = sp.supplier_id
            WHERE 1=1';
    $params = [];
    if ($supplierId) {
        $sql .= ' AND sp.supplier_id = ?';
        $params[] = $supplierId;
    }
    if ($active !== null) {
        $sql .= ' AND sp.active = ?';
        $params[] = $active;
    }
    $sql .= ' ORDER BY sp.supplier_product_name';
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $rows = $stmt->fetchAll();

    return ['data' => $rows, 'count' => count($rows)];
}

function procm_api_purchase_suggestions(PDO $pdo): array
{
    if (!procm_table_exists($pdo, 'purchase_suggestions')) {
        return ['data' => [], 'count' => 0];
    }
    $status = $_GET['status'] ?? 'open';
    $sql = 'SELECT ps.id, ps.supplier_product_id, ps.supplier_id,
                   ps.suggested_quantity, ps.reason, ps.status, ps.priority, ps.created_at,
                   sp.supplier_product_name, s.name AS supplier_name
            FROM purchase_suggestions ps
            JOIN supplier_products sp ON sp.id = ps.supplier_product_id
            LEFT JOIN suppliers s ON s.id = ps.supplier_id
            WHERE ps.status = ?
            ORDER BY ps.created_at DESC';
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$status]);
    $rows = $stmt->fetchAll();

    return ['data' => $rows, 'count' => count($rows)];
}

function procm_api_recipes(PDO $pdo): array
{
    if (!procm_table_exists($pdo, 'recipes')) {
        return ['data' => [], 'count' => 0];
    }
    $sql = 'SELECT r.id, r.name, r.active, r.notes,
                   rv.id AS version_id, rv.version_number, rv.batch_size, rv.output_unit, rv.status
            FROM recipes r
            JOIN recipe_versions rv ON rv.recipe_id = r.id AND rv.status = \'active\'
            ORDER BY r.name';
    $rows = $pdo->query($sql)->fetchAll();

    return ['data' => $rows, 'count' => count($rows)];
}

function procm_api_cost_calculations(PDO $pdo): array
{
    if (!procm_table_exists($pdo, 'cost_calculations')) {
        return ['data' => [], 'count' => 0];
    }
    $limit = min(100, max(1, (int) ($_GET['limit'] ?? 50)));
    $sql = 'SELECT id, cost_model_id, target_type, target_id,
                   total_cost, unit_cost, suggested_sale_price,
                   margin_euro, margin_percent, calculated_at, notes
            FROM cost_calculations
            ORDER BY calculated_at DESC
            LIMIT ' . $limit;
    $rows = $pdo->query($sql)->fetchAll();

    return ['data' => $rows, 'count' => count($rows)];
}

function procm_api_dashboard_summary(PDO $pdo): array
{
    $suppliers = (int) $pdo->query('SELECT COUNT(*) FROM suppliers WHERE active = 1')->fetchColumn();
    $products = (int) $pdo->query('SELECT COUNT(*) FROM supplier_products WHERE active = 1')->fetchColumn();
    $openSuggestions = 0;
    if (procm_table_exists($pdo, 'purchase_suggestions')) {
        $openSuggestions = (int) $pdo->query(
            "SELECT COUNT(*) FROM purchase_suggestions WHERE status = 'open'"
        )->fetchColumn();
    }
    $orders = (int) $pdo->query('SELECT COUNT(*) FROM purchase_orders')->fetchColumn();
    $recentOrders = $pdo->query(
        'SELECT po.id, po.order_date, po.status, s.name AS supplier_name
         FROM purchase_orders po
         JOIN suppliers s ON s.id = po.supplier_id
         ORDER BY po.created_at DESC LIMIT 5'
    )->fetchAll();

    return [
        'suppliers_count' => $suppliers,
        'supplier_products_count' => $products,
        'open_purchase_suggestions' => $openSuggestions,
        'purchase_orders_count' => $orders,
        'recent_purchase_orders' => $recentOrders,
        'module' => 'procM',
        'status' => 'PROCUREMENT MVP COMPLETE',
    ];
}

function procm_api_copilot_dashboard(PDO $pdo): array
{
    $summary = procm_api_dashboard_summary($pdo);
    $reorderCount = $summary['open_purchase_suggestions'];
    if (procm_table_exists($pdo, 'purchase_suggestions')) {
        $reorderCount = (int) $pdo->query(
            "SELECT COUNT(DISTINCT supplier_product_id) FROM purchase_suggestions WHERE status = 'open'"
        )->fetchColumn();
    }
    $recentPurchases = $pdo->query(
        'SELECT po.id, po.order_date, po.status, s.name AS supplier_name,
                COALESCE((SELECT SUM(line_total) FROM purchase_order_lines WHERE purchase_order_id = po.id), 0) AS total
         FROM purchase_orders po
         JOIN suppliers s ON s.id = po.supplier_id
         ORDER BY po.created_at DESC LIMIT 10'
    )->fetchAll();

    return [
        'suppliers_count' => $summary['suppliers_count'],
        'supplier_products_count' => $summary['supplier_products_count'],
        'products_needing_reorder' => $reorderCount,
        'active_purchase_suggestions' => $summary['open_purchase_suggestions'],
        'recent_purchases' => $recentPurchases,
        'generated_at' => gmdate('c'),
        'contract' => 'procM.copilot.dashboard.v1',
    ];
}

function procm_dispatch_api(PDO $pdo, string $path, string $method): ?array
{
    if ($method !== 'GET') {
        return null;
    }

    $routes = [
        '/suppliers' => 'procm_api_suppliers',
        '/supplier-products' => 'procm_api_supplier_products',
        '/purchase-suggestions' => 'procm_api_purchase_suggestions',
        '/recipes' => 'procm_api_recipes',
        '/cost-calculations' => 'procm_api_cost_calculations',
        '/dashboard-summary' => 'procm_api_dashboard_summary',
        '/copilot/dashboard' => 'procm_api_copilot_dashboard',
    ];

    if (!isset($routes[$path])) {
        return null;
    }

    $handler = $routes[$path];

    return $handler($pdo);
}
