<?php

declare(strict_types=1);

namespace App\Service;

use App\Entity\User;
use App\Repository\UserRepository;
use Doctrine\ORM\EntityManagerInterface;

/**
 * Handles all user-related operations.
 *
 * This is a shallow "god service" that mixes concerns:
 * authentication, profile management, notification, and reporting.
 * It is a planted structural candidate for refactor-scan.
 */
class UserService
{
    public function __construct(
        private UserRepository $repo,
        private EntityManagerInterface $em,
    ) {
    }

    public function findById(int $id): ?User
    {
        return $this->repo->find($id);
    }

    public function findByEmail(string $email): ?User
    {
        return $this->repo->findOneBy(['email' => $email]);
    }

    public function create(array $data): User
    {
        $user = new User();
        $user->setName($data['name']);
        $user->setEmail($data['email']);
        $user->setPassword(password_hash($data['password'], PASSWORD_BCRYPT));
        $this->em->persist($user);
        $this->em->flush();
        return $user;
    }

    public function updateProfile(int $id, array $data): User
    {
        $user = $this->repo->find($id);
        if (!$user) {
            throw new \RuntimeException("User $id not found");
        }
        if (isset($data['name'])) {
            $user->setName($data['name']);
        }
        if (isset($data['email'])) {
            $user->setEmail($data['email']);
        }
        if (isset($data['bio'])) {
            $user->setBio($data['bio']);
        }
        $this->em->flush();
        return $user;
    }

    public function changePassword(int $id, string $old, string $new): void
    {
        $user = $this->repo->find($id);
        if (!$user || !password_verify($old, $user->getPassword())) {
            throw new \RuntimeException("Invalid credentials");
        }
        $user->setPassword(password_hash($new, PASSWORD_BCRYPT));
        $this->em->flush();
    }

    public function sendWelcomeEmail(User $user): void
    {
        // Inline notification logic — should be a separate service
        $to = $user->getEmail();
        $subject = 'Welcome!';
        $body = "Hello {$user->getName()}, welcome to our platform.";
        mail($to, $subject, $body);
    }

    public function sendPasswordReset(User $user): void
    {
        $token = bin2hex(random_bytes(32));
        // Store token inline — should be a token service
        $to = $user->getEmail();
        $subject = 'Password Reset';
        $body = "Reset your password: https://example.com/reset?token=$token";
        mail($to, $subject, $body);
    }

    public function getMonthlyReport(): array
    {
        // Reporting logic mixed into the service
        $users = $this->repo->findAll();
        $active = 0;
        $inactive = 0;
        foreach ($users as $user) {
            if ($user->getLastLoginAt() && $user->getLastLoginAt() > new \DateTimeImmutable('-30 days')) {
                $active++;
            } else {
                $inactive++;
            }
        }
        return [
            'total' => count($users),
            'active' => $active,
            'inactive' => $inactive,
        ];
    }

    public function deactivate(int $id): void
    {
        $user = $this->repo->find($id);
        if (!$user) {
            throw new \RuntimeException("User $id not found");
        }
        $user->setActive(false);
        $this->em->flush();
    }

    public function reactivate(int $id): void
    {
        $user = $this->repo->find($id);
        if (!$user) {
            throw new \RuntimeException("User $id not found");
        }
        $user->setActive(true);
        $this->em->flush();
    }

    public function delete(int $id): void
    {
        $user = $this->repo->find($id);
        if (!$user) {
            throw new \RuntimeException("User $id not found");
        }
        $this->em->remove($user);
        $this->em->flush();
    }
}
