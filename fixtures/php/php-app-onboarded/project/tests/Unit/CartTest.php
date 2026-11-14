<?php

declare(strict_types=1);

namespace Acme\Shop\Tests\Unit;

use Acme\Shop\Cart;
use PHPUnit\Framework\TestCase;

final class CartTest extends TestCase
{
    public function testCountsTheQuantitiesAdded(): void
    {
        $cart = new Cart();
        $cart->add('A-1', 2);
        $cart->add('A-1', 1);

        self::assertSame(3, $cart->count());
    }
}
