<?php
// Applies Rector's dead-code, type-coverage, php-version, code-quality,
// phpunit, and early-return rule sets (all fully adopted).
return static function (Rector\Config\RectorConfig $rectorConfig): void {
    $rectorConfig->sets([
        Rector\Set\ValueObject\SetList::DEAD_CODE,
        Rector\Set\ValueObject\SetList::TYPE_DECLARATION,
        Rector\Set\ValueObject\LevelSetList::UP_TO_PHP_82,
        Rector\Set\ValueObject\SetList::CODE_QUALITY,
        Rector\PHPUnit\Set\PHPUnitSetList::PHPUNIT_100,
        Rector\Set\ValueObject\SetList::EARLY_RETURN,
    ]);
};
