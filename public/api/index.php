<?php

declare(strict_types=1);

require dirname(__DIR__, 2) . '/src-php/bootstrap.php';
require dirname(__DIR__, 2) . '/src-php/api_handlers.php';

$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';
$path = preg_replace('#/index\.php$#', '', $path) ?: '/';
$path = preg_replace('#^/api#', '', $path) ?: '/';
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';

if ($path === '/health' || $path === '/') {
    $commitFile = procm_root_dir() . '/DEPLOY_COMMIT.txt';
    $commit = is_file($commitFile) ? trim((string) file_get_contents($commitFile)) : 'unknown';
    $dbStatus = 'not_configured';
    $tables = null;
    if (procm_config_loaded()) {
        try {
            $pdo = procm_pdo();
            if ($pdo) {
                $pdo->query('SELECT 1');
                $dbStatus = 'connected';
                $row = $pdo->query(
                    "SELECT COUNT(*) AS c FROM information_schema.tables WHERE table_schema = DATABASE()"
                )->fetch();
                $tables = (int) ($row['c'] ?? 0);
            }
        } catch (Throwable $e) {
            $dbStatus = 'error';
        }
    }
    procm_json_response([
        'status' => 'ok',
        'module' => 'procM',
        'edition' => 'business',
        'commit' => $commit,
        'config' => procm_config_loaded() ? 'config.php' : 'example_only',
        'database' => $dbStatus,
        'table_count' => $tables,
        'flask_local' => 'python run.py (dev)',
        'procurement_mvp_status' => 'PROCUREMENT MVP COMPLETE',
        'time' => gmdate('c'),
    ]);
    exit;
}

if (!procm_check_api_key()) {
    procm_json_response(['error' => 'unauthorized'], 401);
    exit;
}

if (!procm_config_loaded()) {
    procm_json_response(['error' => 'config_required'], 503);
    exit;
}

try {
    $pdo = procm_pdo();
    if (!$pdo) {
        procm_json_response(['error' => 'database_unavailable'], 503);
        exit;
    }
    $result = procm_dispatch_api($pdo, $path, $method);
    if ($result !== null) {
        procm_json_response($result);
        exit;
    }
} catch (Throwable $e) {
    procm_json_response(['error' => 'server_error', 'message' => $e->getMessage()], 500);
    exit;
}

procm_json_response(['error' => 'not_found', 'path' => $path], 404);
