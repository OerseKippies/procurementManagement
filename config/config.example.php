<?php

/**
 * procM production config — copy to config.php and set password + api_key.
 * Database: nol_module_procM (Versio MariaDB)
 */
return [
    'app' => [
        'name' => 'procurementManagement',
        'module_code' => 'procM',
        'timezone' => 'Europe/Amsterdam',
    ],
    'database' => [
        'driver' => 'mysql',
        'host' => 'localhost',
        'port' => 3306,
        'dbname' => 'nol_module_procM',
        'username' => 'nol_module_procM',
        'password' => 'CHANGE_ME',
        'charset' => 'utf8mb4',
    ],
    'api' => [
        'require_api_key' => false,
        'api_key' => 'CHANGE_ME',
    ],
];
