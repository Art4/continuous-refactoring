<?php

declare(strict_types=1);

namespace App;

class Greeter
{
    public function greet(string $name): string
    {
        return "Hello, {$name}!";
    }
}
