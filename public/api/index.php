<?php

declare(strict_types=1);

require dirname(__DIR__, 2) . '/src-php/bootstrap.php';

$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';
$path = preg_replace('#/index\.php$#', '', $path) ?: '/';
$path = preg_replace('#^/api#', '', $path) ?: '/';

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
        'time' => gmdate('c'),
    ]);
    exit;
}

if (!procm_check_api_key()) {
    procm_json_response(['error' => 'unauthorized'], 401);
    exit;
}

procm_json_response(['error' => 'not_found', 'path' => $path], 404);
