<?php
// Applies Rector's dead-code and type-coverage rule sets (fully adopted).
return static function (Rector\Config\RectorConfig $rectorConfig): void {
    $rectorConfig->sets([
        Rector\Set\ValueObject\SetList::DEAD_CODE,
        Rector\Set\ValueObject\SetList::TYPE_DECLARATION,
    ]);
};
