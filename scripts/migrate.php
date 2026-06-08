<?php

declare(strict_types=1);

$root = dirname(__DIR__);
require $root . '/src-php/bootstrap.php';

if (!procm_config_loaded()) {
    fwrite(STDERR, "Missing config/config.php — copy config.example.php and set database password.\n");
    exit(1);
}

$pdo = procm_pdo();
if (!$pdo) {
    fwrite(STDERR, "Unable to connect to database.\n");
    exit(1);
}

$pdo->exec(
    'CREATE TABLE IF NOT EXISTS procm_schema_migrations (
        migrationId VARCHAR(64) PRIMARY KEY,
        appliedAt DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'
);

$migrations = [
    '001_procM_core_schema' => '001_procM_core_schema.sql',
    '002_procM_business_schema' => '002_procM_business_schema.sql',
];

foreach ($migrations as $id => $file) {
    $stmt = $pdo->prepare('SELECT migrationId FROM procm_schema_migrations WHERE migrationId = ? LIMIT 1');
    $stmt->execute([$id]);
    if ($stmt->fetch()) {
        echo "Migration {$id} already applied.\n";
        continue;
    }
    $sql = file_get_contents($root . '/migrations/' . $file);
    if ($sql === false) {
        fwrite(STDERR, "Cannot read {$file}\n");
        exit(1);
    }
    $pdo->exec($sql);
    $ins = $pdo->prepare('INSERT INTO procm_schema_migrations (migrationId, appliedAt) VALUES (?, ?)');
    $ins->execute([$id, gmdate('Y-m-d H:i:s')]);
    echo "Migration {$id} applied.\n";
}

echo "procM migrate complete.\n";
