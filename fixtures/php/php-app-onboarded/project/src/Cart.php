<?php

declare(strict_types=1);

namespace Acme\Shop;

final class Cart
{
    /** @var array<string, int> */
    private array $items = [];

    public function add(string $sku, int $quantity): void
    {
        $this->items[$sku] = ($this->items[$sku] ?? 0) + $quantity;
    }

    public function count(): int
    {
        return array_sum($this->items);
    }
}
