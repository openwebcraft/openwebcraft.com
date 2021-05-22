<?php

include __DIR__ . '/../kirby/bootstrap.php';

$kirby = new Kirby([
    'roots' => [
        'index'   => __DIR__,
        'site'    => __DIR__ . '/../site',
        'content' => __DIR__ . '/../content',
        'media'   => __DIR__ . '/../static/kmedia'
    ],
    'urls' => [
        'index'  => 'https://openwebcraft.com',
        'media'  => 'https://openwebcraft.com/kmedia',
        'assets' => 'https://openwebcraft.com/kassets'
    ]
]);

echo $kirby->render();
