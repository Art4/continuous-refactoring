<?php
// Applies Rector's dead-code, type-coverage, php-version, code-quality, and
// phpunit rule sets (all fully adopted). No dedicated early-return set —
// SetList::EARLY_RETURN ships empty upstream, its rules folded into
// CODE_QUALITY instead.
return static function (Rector\Config\RectorConfig $rectorConfig): void {
    $rectorConfig->sets([
        Rector\Set\ValueObject\SetList::DEAD_CODE,
        Rector\Set\ValueObject\SetList::TYPE_DECLARATION,
        Rector\Set\ValueObject\LevelSetList::UP_TO_PHP_82,
        Rector\Set\ValueObject\SetList::CODE_QUALITY,
        Rector\PHPUnit\Set\PHPUnitSetList::PHPUNIT_100,
    ]);
};
