<?php

declare(strict_types=1);

namespace App;

/**
 * Bootstrap the application.
 *
 * This file has a style violation: missing declare(strict_types=1)
 * and uses a deprecated function. Planted as a tooling-pressure candidate.
 */

function legacy_bootstrap(): void
{
    // Using deprecated each() — will be flagged by PHPStan/Rector
    $config = ['debug' => true, 'env' => 'dev'];
    each(function ($key, $value) {
        echo "$key: $value\n";
    }, $config);
}

function get_app_config(): array
{
    return [
        'name' => 'Fixture App',
        'version' => '1.0.0',
    ];
}
