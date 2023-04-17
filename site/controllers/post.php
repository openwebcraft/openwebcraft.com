<?php

# Controller for the single post page
return function ($page, $pages, $site, $kirby) {

    # Grab the default SEO controller
    $seo = $kirby->controller('seo' , compact('page', 'pages', 'site', 'kirby'));

    # Fetch the page content
    $posts = $kirby->collection('posts');
    $post  = $page;
    $title = $post->title()->html();
    $url   = $post->parent()->url();
    $text  = $post->text()->kt();

    # Return some data and pass it to the template
    $data = compact('title' , 'url' , 'text' , 'posts' , 'post');

    # Return the compact array to the template
    return a::merge($data , $seo);

};