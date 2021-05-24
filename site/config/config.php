<?php

return [
    'servers' => ['httpd'],
    'panel' => [
        'install' => true,
        'slug' => 'kirby/panel'
    ],
    'api' => [
        'slug' => 'kirby/api'
    ],
    'debug' => false,
    'home'  => 'home',
    'community.markdown-field.font' => [
        'family'  => 'sans-serif',
        'scaling' => true,
        'size'    => 'small',
    ],
    'community.markdown-field.modals'        => true,
    'community.markdown-field.blank'         => false,
    'community.markdown-field.invisibles'    => false,
    'community.markdown-field.strikethrough' => true,
    'kirby-extended.highlighter.autodetect'  => true,
    'oblik.git.repo' => '/htdocs/openwebcraft.com',
    'oblik.git.merge' => 'kirbyobsd',
    'oblik.git.bin' => '/bin/git',
    'matthiasjg' => [
        'static_site_composer' => [
            'endpoint' => 'compose-static-site',
            'output_folder' => '../static',
            'preserve' => ['notes', 'kassets', 'kmedia', 'favicon.ico'],
            'base_url' => '/',
            'skip_media' => true,
            'skip_templates' => [],
            'pages_parent_home_root' => true,
            'preview_url_slug' => 'kirby/preview',
            'feed_formats' => ['rss', 'json'],
            'feed_description' => 'Latest writing',
            'feedollection' => 'posts',
            'feed_collection_limit' => 10,
            'feed_collection_datefield' => 'published',
            'feed_collection_textfield' => 'text'
        ]
    ]
];
