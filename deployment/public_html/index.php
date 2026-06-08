<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
$commitFile = dirname(__DIR__, 2) . '/DEPLOY_COMMIT.txt';
$commit = is_file($commitFile) ? trim((string) file_get_contents($commitFile)) : 'unknown';
echo json_encode([
    'status' => 'deployed',
    'module' => 'procM',
    'edition' => 'business',
    'commit' => $commit,
    'runtime_note' => 'Flask runtime requires Python 3.10+; use local run.py or pending Versio Python upgrade',
    'health' => 'ok',
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
