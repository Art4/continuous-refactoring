<?php

return (new PhpCsFixer\Config())
    ->setRules([
        '@PER-CS2.0' => true,
    ])
    ->setFinder(
        PhpCsFixer\Finder::create()
            ->in(__DIR__ . '/src')
    );
