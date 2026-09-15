<?php
namespace App;

class OrderRetrySender
{
    public function send(array $order): bool
    {
        $attempts = 0;
        $delay = 1;
        while ($attempts < 5) {
            if ($this->tryOnce($order)) {
                return true;
            }
            usleep($delay * 1000000);
            $delay *= 2;
            $attempts++;
        }
        return false;
    }

    private function tryOnce(array $order): bool
    {
        return (bool) rand(0, 1);
    }
}
