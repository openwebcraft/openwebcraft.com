<?php

# Add a bit of customizations to the already awesome K3
Kirby::plugin('manu/zendo', [

    # General Settings
    'options' => [
        'maxWidth' => 2000
    ],

    # Include the components
    'controllers' => include __DIR__ . '/inc/controllers.php', # Custom Cntroller
    'tags'        => include __DIR__ . '/inc/tags.php',        # Custom Kirbytags
    'hooks'       => include __DIR__ . '/inc/hooks.php',       # Custom Hooks
    'routes'      => include __DIR__ . '/inc/routes.php',      # Custom Routes

]);