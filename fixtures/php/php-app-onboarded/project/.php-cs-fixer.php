<?php

$finder = PhpCsFixer\Finder::create()->in([__DIR__ . '/src', __DIR__ . '/tests']);

return (new PhpCsFixer\Config())
    ->setRules([
        '@PER-CS3x0' => true,
        'no_unused_imports' => true,
        'array_syntax' => false, // Not yet: 212 files
        'single_quote' => false, // Not yet: 31 files
        'native_function_casing' => false, // Not yet: 9 files
    ])
    ->setFinder($finder);
