<?php

# Controller for the homepage
return function ($page, $pages, $site, $kirby) {

    # Grab the default SEO controller
    $seo = $kirby->controller('seo' , compact('page', 'pages', 'site', 'kirby'));

    # Fetch the page content
    $posts = $kirby->collection('posts');
    $post  = $posts->first();
    $title = $post->title()->html();
    $url   = $post->url();
    $text  = $post->text()->kt();

    # Return some data and pass it to the template
    $data = compact('title' , 'url' , 'text' , 'posts' , 'post');

    # Return the compact array to the template
    return a::merge($data , $seo);

};