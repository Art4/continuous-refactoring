<?php

use Rector\Config\RectorConfig;

// The PHP set at the floor, dead code, code quality and type coverage, each fully applied.
// The PHPUnit set is a Guardrails Stage and not set up yet.
return RectorConfig::configure()
    ->withPaths([__DIR__ . '/src', __DIR__ . '/tests'])
    ->withPhpSets(php82: true)
    ->withPreparedSets(deadCode: true, codeQuality: true, typeDeclarations: true);
