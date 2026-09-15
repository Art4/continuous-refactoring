<?php
namespace App;

class PaymentRetryDispatcher
{
    public function dispatch(array $payment): bool
    {
        $tries = 0;
        $waitSeconds = 2;
        while ($tries < 4) {
            if ($this->attempt($payment)) {
                return true;
            }
            sleep($waitSeconds);
            $waitSeconds = $waitSeconds + 2;
            $tries++;
        }
        return false;
    }

    private function attempt(array $payment): bool
    {
        return (bool) rand(0, 1);
    }
}
