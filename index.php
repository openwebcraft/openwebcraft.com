<?php

include __DIR__ . '/kirby/bootstrap.php';

$kirby = new Kirby([
    'roots' => [
        'index'   => __DIR__,
        'site'    => __DIR__ . '/site',
        'content' => __DIR__ . '/content',
        'media'   => __DIR__ . '/static/kmedia',
        'assets'   => __DIR__ . '/static/kassets'
    ],
    'urls' => [
        'index'  => 'http://localhost:8000',
        'media'  => 'http://localhost:8000/static/kmedia',
        'assets' => 'http://localhost:8000/static/kassets'
    ]
]);

echo $kirby->render();
