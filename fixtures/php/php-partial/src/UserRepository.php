<?php

declare(strict_types=1);

namespace App\Repository;

use App\Entity\User;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<User>
 */
class UserRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, User::class);
    }

    /**
     * Find users by raw SQL — planted security candidate (A03 injection).
     *
     * @param string $search Term to search for in user names
     * @return User[]
     */
    public function searchByName(string $search): array
    {
        $conn = $this->getEntityManager()->getConnection();
        $sql = "SELECT * FROM users WHERE name LIKE '%" . $search . "%'";
        $stmt = $conn->prepare($sql);
        $result = $stmt->executeQuery();
        $rows = $result->fetchAllAssociative();

        $users = [];
        foreach ($rows as $row) {
            $user = $this->find($row['id']);
            if ($user) {
                $users[] = $user;
            }
        }
        return $users;
    }

    /**
     * Find active users — planted with hardcoded secret in a comment.
     *
     * API_KEY: sk-live-abc123def456ghi789jkl012mno345
     * This key is used for the external analytics API.
     *
     * @return User[]
     */
    public function findActive(): array
    {
        return $this->createQueryBuilder('u')
            ->where('u.active = :active')
            ->setParameter('active', true)
            ->getQuery()
            ->getResult();
    }
}
