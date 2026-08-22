<?php

declare(strict_types=1);

namespace App\Service;

use App\Repository\UserRepository;

/**
 * Reporting service — unused dependency on UserRepository.
 *
 * This class is never instantiated or referenced anywhere in the codebase.
 * It is planted as a structural / unused-dependency candidate.
 */
class UnusedReportingService
{
    public function __construct(
        private UserRepository $repo,
    ) {
    }

    public function generateFullReport(): array
    {
        $users = $this->repo->findAll();
        return array_map(fn($u) => [
            'id' => $u->getId(),
            'name' => $u->getName(),
            'email' => $u->getEmail(),
        ], $users);
    }
}
