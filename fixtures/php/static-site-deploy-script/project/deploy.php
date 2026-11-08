<?php

namespace Deployer;

require 'recipe/common.php';

set('application', 'acme-shop');
set('repository', 'git@example.com:acme/shop.git');
set('keep_releases', 3);

host('www.example.com')
    ->set('remote_user', 'deploy')
    ->set('deploy_path', '/var/www/acme-shop');

task('deploy', [
    'deploy:prepare',
    'deploy:publish',
]);

after('deploy:failed', 'deploy:unlock');
