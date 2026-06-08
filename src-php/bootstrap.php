<?php

declare(strict_types=1);

function procm_root_dir(): string
{
    return dirname(__DIR__);
}

function procm_config(): array
{
    $root = procm_root_dir();
    $path = $root . '/config/config.php';
    if (!is_file($path)) {
        return require $root . '/config/config.example.php';
    }

    return require $path;
}

function procm_config_loaded(): bool
{
    return is_file(procm_root_dir() . '/config/config.php');
}

function procm_pdo(): ?PDO
{
    if (!procm_config_loaded()) {
        return null;
    }
    $db = procm_config()['database'];
    $dsn = sprintf(
        'mysql:host=%s;port=%d;dbname=%s;charset=%s',
        $db['host'],
        (int) $db['port'],
        $db['dbname'],
        $db['charset'] ?? 'utf8mb4'
    );

    return new PDO($dsn, $db['username'], $db['password'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);
}

function procm_check_api_key(): bool
{
    $api = procm_config()['api'] ?? [];
    if (empty($api['require_api_key'])) {
        return true;
    }
    $expected = (string) ($api['api_key'] ?? '');
    $provided = (string) ($_SERVER['HTTP_X_API_KEY'] ?? $_GET['api_key'] ?? '');

    return $expected !== '' && hash_equals($expected, $provided);
}

function procm_json_response(array $payload, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
}
