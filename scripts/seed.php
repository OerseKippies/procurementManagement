<?php

declare(strict_types=1);

$root = dirname(__DIR__);
require $root . '/src-php/bootstrap.php';

if (!procm_config_loaded()) {
    fwrite(STDERR, "Missing config/config.php\n");
    exit(1);
}

$pdo = procm_pdo();
if (!$pdo) {
    fwrite(STDERR, "Unable to connect to database.\n");
    exit(1);
}

$files = ['SEED-SUPPLIERS.sql', 'SEED-PRODUCTS.sql'];

foreach ($files as $file) {
    $path = $root . '/' . $file;
    if (!is_file($path)) {
        fwrite(STDERR, "Missing {$file}\n");
        exit(1);
    }
    $sql = file_get_contents($path);
    if ($sql === false) {
        fwrite(STDERR, "Cannot read {$file}\n");
        exit(1);
    }
    $pdo->exec($sql);
    echo "Seed {$file} applied.\n";
}

echo "procM seed complete.\n";
