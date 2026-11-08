# static-site-deploy-script fixture

A static HTML/CSS site under `public/`, deployed with Deployer. Its only PHP file is the Deployer recipe
`deploy.php`, which configures the tool and holds no code of the project's own; there is no `composer.json`. The PHP
Pack's *Applies when* does not hold here, so only the generic Pack's Stages are proposed.
